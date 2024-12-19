from flask import jsonify
from utils.azure_client import AzureClient
import pandas as pd
from utils.df_to_csv import df_to_csv
from utils.sftp import SFTPClient
from utils.admin_names import handle_files
from utils.transform_azure_data import transform_ad_email, transform_ad_dq_number, transform_ad_fullname
from utils.config import AZURE_CLIENTID, AZURE_TENANTID, AZURE_CLIENTSECRET, CSV_PATH, SFTP_HOST, SFTP_USER, SFTP_PASS
import logging

logger = logging.getLogger(__name__)


def get_email():
    logger.info("Retrieving randers emails from Azure AD'...")

    try:
        absolute_path = CSV_PATH
        emails = transform_ad_email(absolute_path)
        if not emails:
            logger.error("Error retrieving emails from CSV")
            return jsonify({"error": "Error retrieving emails from CSV"}), 500
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        return jsonify({"error": "Error processing CSV file"}), 500

    logger.info(f"Retrieved emails: {emails}")
    return jsonify({"emails": emails}), 200


def get_dq_numbers():
    logger.info("Retrieving DQ Numbers from Azure AD'...")

    try:
        absolute_path = CSV_PATH
        dq_numbers = transform_ad_dq_number(absolute_path)
        if not dq_numbers:
            logger.error("Error retrieving DQ numbers from CSV")
            return jsonify({"error": "Error retrieving DQ numbers from CSV"}), 500
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        return jsonify({"error": "Error processing CSV file"}), 500

    logger.info(f"Retrieved DQ numbers: {dq_numbers}")
    return jsonify({"dq_numbers": dq_numbers}), 200


def get_fullname():
    logger.info("Retrieving user FullName from Azure AD'...")

    try:
        absolute_path = CSV_PATH
        logger.info(f"Absolute path to CSV file: {absolute_path}")
        fullnames = transform_ad_fullname(absolute_path)
        if not fullnames:
            logger.error("Error retrieving full names from CSV")
            return jsonify({"error": "Error retrieving full names from CSV"}), 500
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        return jsonify({"error": "Error processing CSV file"}), 500

    logger.info(f"Retrieved full names: {fullnames}")
    return jsonify({"fullnames": fullnames}), 200


def get_and_save_azure_ad_data():
    logger.info("Retrieving data from Azure AD and save to CSV...")

    try:
        azure_client = AzureClient(AZURE_CLIENTID, AZURE_CLIENTSECRET, AZURE_TENANTID, "https://graph.microsoft.com")
        users = azure_client.get_all_users()

        if not users:
            logger.error("Error retrieving data from Azure AD")
            return jsonify({"error": "Error retrieving data from Azure AD"}), 500

        df = pd.DataFrame(users)
        csv_filename = 'file'
        df_to_csv(df, csv_filename)
        logger.info(f"Data saved to {csv_filename}.csv")
        return jsonify({"message": f"Data saved to {csv_filename}.csv"}), 200
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return jsonify({"error": "Error processing data"}), 500


def get_admin_names():
    logger.info("Retrieving admin names...")
    sftp_client = SFTPClient(SFTP_HOST, SFTP_USER, SFTP_PASS)
    conn = sftp_client.get_connection()
    if conn:
        admin_names = handle_files(conn)
        if not admin_names:
            logger.error("Error retrieving admin names from SFTP")
            return jsonify({"error": "Error retrieving admin names from SFTP"}), 500
    else:
        logger.error("Error establishing SFTP connection")
        return jsonify({"error": "Error establishing SFTP connection"}), 500

    logger.info(f"Retrieved admin names: {admin_names}")
    return jsonify({"admin_names": admin_names}), 200
