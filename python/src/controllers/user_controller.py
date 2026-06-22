from flask import jsonify
from utils.azure_client import AzureClient
import pandas as pd
from utils.df_to_csv import df_to_csv
from utils.sftp import SFTPClient
from utils.admin_names import handle_files
from utils.transform_azure_data import transform_ad_email, transform_ad_dq_number, transform_ad_fullname, transform_ad_data
from utils.config import AZURE_CLIENTID, AZURE_TENANTID, AZURE_CLIENTSECRET, AZURE_CSV_PATH, SD_CSV_PATH, SFTP_HOST, SFTP_USER, SFTP_PASS
import logging
import os
from datetime import datetime, timedelta, timezone
import threading

logger = logging.getLogger(__name__)


_azure_cache_lock = threading.Lock()
_azure_cache_mtime: float | None = None
_azure_cache_payloads: dict | None = None


def _is_file_stale(file_path: str, max_age: timedelta) -> bool:
    if not file_path:
        return True
    try:
        if not os.path.exists(file_path):
            return True
        mtime = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
        return (datetime.now(timezone.utc) - mtime) > max_age
    except OSError:
        return True


def ensure_azure_ad_data_fresh(max_age_hours: int = 24) -> bool:
    """Ensure the Azure AD CSV exists and is not older than max_age_hours."""
    absolute_path = AZURE_CSV_PATH
    max_age = timedelta(hours=max_age_hours)

    if _is_file_stale(absolute_path, max_age=max_age):
        logger.info(
            f"Azure AD CSV missing or older than {max_age_hours} hours at {absolute_path}. "
            "Retrieving data from Azure AD..."
        )
        ok = bool(get_and_save_azure_ad_data())
        if not ok:
            return False
    return True


def _rebuild_azure_cache() -> bool:
    """Recompute all AD payloads from the current CSV and store them in memory."""
    global _azure_cache_mtime, _azure_cache_payloads

    absolute_path = AZURE_CSV_PATH
    abs_path = os.path.abspath(absolute_path)
    if not os.path.exists(abs_path):
        return False

    try:
        logger.info("Rebuilding Azure AD cache from CSV...")
        payloads = {
            "data": transform_ad_data(abs_path),
            "emails": transform_ad_email(abs_path),
            "dq_numbers": transform_ad_dq_number(abs_path),
            "fullnames": transform_ad_fullname(abs_path),
        }
        mtime = os.path.getmtime(abs_path)
    except Exception as e:
        logger.error(f"Error rebuilding Azure AD cache: {e}")
        return False

    with _azure_cache_lock:
        _azure_cache_payloads = payloads
        _azure_cache_mtime = mtime

    return True


def ensure_azure_cache(max_age_hours: int = 24) -> bool:
    """Ensure Azure CSV is fresh and the in-memory transformed payloads are built."""
    if not ensure_azure_ad_data_fresh(max_age_hours=max_age_hours):
        return False

    abs_path = os.path.abspath(AZURE_CSV_PATH)
    try:
        current_mtime = os.path.getmtime(abs_path)
    except OSError:
        return False

    with _azure_cache_lock:
        needs_rebuild = _azure_cache_payloads is None or _azure_cache_mtime != current_mtime

    if needs_rebuild:
        logger.info("Rebuilding in-memory Azure AD payload cache")
        return _rebuild_azure_cache()

    return True


def warm_azure_ad_cache(max_age_hours: int = 24) -> bool:
    """Fetch/refresh Azure AD data if needed and build the in-memory payload cache."""
    return ensure_azure_cache(max_age_hours=max_age_hours)


def get_user_data():
    if not ensure_azure_cache(max_age_hours=24):
        return jsonify({"error": "Error retrieving data from Azure AD"}), 500

    with _azure_cache_lock:
        payloads = _azure_cache_payloads or {}
        data = payloads.get("data")

    if not data:
        return jsonify({"error": "Error retrieving data from CSV"}), 500

    return jsonify(data), 200


def get_email():
    if not ensure_azure_cache(max_age_hours=24):
        return jsonify({"error": "Error retrieving data from Azure AD"}), 500

    with _azure_cache_lock:
        payloads = _azure_cache_payloads or {}
        emails = payloads.get("emails")

    if not emails:
        return jsonify({"error": "Error retrieving emails from CSV"}), 500

    return jsonify({"emails": emails}), 200


def get_dq_numbers():
    if not ensure_azure_cache(max_age_hours=24):
        return jsonify({"error": "Error retrieving data from Azure AD"}), 500

    with _azure_cache_lock:
        payloads = _azure_cache_payloads or {}
        dq_numbers = payloads.get("dq_numbers")

    if not dq_numbers:
        return jsonify({"error": "Error retrieving DQ numbers from CSV"}), 500

    return jsonify({"dq_numbers": dq_numbers}), 200


def get_fullname():
    if not ensure_azure_cache(max_age_hours=24):
        return jsonify({"error": "Error retrieving data from Azure AD"}), 500

    with _azure_cache_lock:
        payloads = _azure_cache_payloads or {}
        fullnames = payloads.get("fullnames")

    if not fullnames:
        return jsonify({"error": "Error retrieving full names from CSV"}), 500

    return jsonify({"fullnames": fullnames}), 200


def azure_data_exists():
    absolute_path = AZURE_CSV_PATH
    if os.path.exists(absolute_path):
        logger.info(f"Local file {absolute_path} exists.")
        return True
    else:
        logger.info(f"Local file {absolute_path} does not exist.")
        return False


def azure_data_is_fresh(max_age_hours: int = 24) -> bool:
    absolute_path = AZURE_CSV_PATH
    is_fresh = not _is_file_stale(absolute_path, max_age=timedelta(hours=max_age_hours))
    if is_fresh:
        logger.info(f"Local file {absolute_path} exists and is fresh (< {max_age_hours}h).")
    else:
        logger.info(f"Local file {absolute_path} is missing or stale (>= {max_age_hours}h).")
    return is_fresh


def get_and_save_azure_ad_data():
    logger.info("Retrieving data from Azure AD and save to CSV...")

    try:
        if not (AZURE_CLIENTID and AZURE_CLIENTSECRET and AZURE_TENANTID):
            logger.warning(
                "Azure AD credentials are not configured (AZURE_CLIENTID/AZURE_CLIENTSECRET/AZURE_TENANTID). "
                "Skipping Azure AD fetch."
            )
            return None

        azure_client = AzureClient(AZURE_CLIENTID, AZURE_CLIENTSECRET, AZURE_TENANTID, "https://graph.microsoft.com")
        users = azure_client.get_all_users()

        if not users:
            logger.error("Error retrieving data from Azure AD")
            return None

        df = pd.DataFrame(users)
        csv_filename = AZURE_CSV_PATH
        base_path, extension = os.path.splitext(csv_filename)
        target_base = base_path if extension.lower() == ".csv" else csv_filename
        saved_path = f"{target_base}.csv"
        parent_dir = os.path.dirname(saved_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        df_to_csv(df, target_base)
        logger.info(f"Data saved to {saved_path}")
        return True
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return None


def get_admin_data():
    absolute_path = SD_CSV_PATH

    if not os.path.exists(absolute_path):
        logger.info("Retrieving admin names from SFTP...")
        sftp_client = SFTPClient(SFTP_HOST, SFTP_USER, SFTP_PASS)
        conn = sftp_client.get_connection()

        if conn:
            admin_data = handle_files(conn)
            logger.info(f"Admin data retrieved: {admin_data}")
            with open(absolute_path, 'w', encoding='utf-16') as file:
                file.write(admin_data)
            if not admin_data:
                logger.error("Error retrieving admin data from SFTP")
                return jsonify({"error": "Error retrieving admin data from SFTP"}), 500
        else:
            logger.error("Error establishing SFTP connection")
            return jsonify({"error": "Error establishing SFTP connection"}), 500

    try:
        df = pd.read_csv(absolute_path, encoding='utf-16', delimiter=';')
        admin_data = [{"name": row['Navn'], "mail": row['Email']} for _, row in df.iterrows() if 'Navn' in df.columns and 'Email' in df.columns]

        # Remove objects with missing data
        admin_data = [entry for entry in admin_data if pd.notna(entry['name']) and pd.notna(entry['mail']) and entry['name'] and entry['mail']]
        # Remove duplicates if any
        admin_data = list({entry['name']: entry for entry in admin_data}.values())

        # admin_data = list(set(admin_data))
        return jsonify(admin_data), 200

    except Exception as e:
        logger.error(f"Error reading local file: {e}")
        return jsonify({"error": "Error reading local file"}), 500
