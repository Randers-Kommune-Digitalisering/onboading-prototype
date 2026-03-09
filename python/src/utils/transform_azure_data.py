import io
import pandas as pd
import logging
import os
import threading
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)


_cache_lock = threading.Lock()
_df_cache: Dict[Tuple[str, float], pd.DataFrame] = {}
_result_cache: Dict[Tuple[str, float, str], Any] = {}


def _cache_key(file_path: str) -> Tuple[str, float]:
    abs_path = os.path.abspath(file_path)
    mtime = os.path.getmtime(abs_path)
    return abs_path, mtime


def _get_filtered_ad_df(file_path: str) -> pd.DataFrame:
    """Load AD CSV once per mtime and return filtered rows (DQ/AP users)."""
    abs_path, mtime = _cache_key(file_path)

    with _cache_lock:
        cached = _df_cache.get((abs_path, mtime))
        if cached is not None:
            return cached

        # Drop any older versions of the same file to keep memory bounded.
        for (path_key, _), _df in list(_df_cache.items()):
            if path_key == abs_path:
                _df_cache.pop((path_key, _), None)
        for (path_key, _, _name) in list(_result_cache.keys()):
            if path_key == abs_path:
                _result_cache.pop((path_key, _, _name), None)

    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"No such file or directory: '{abs_path}'")

    with open(abs_path, 'r', encoding='utf-8') as f:
        content = f.read()
        needed_cols = ['displayName', 'mail', 'onPremisesSamAccountName']
        df = pd.read_csv(io.StringIO(content), sep=",", header=0, na_filter=False, usecols=needed_cols)

    filtered_df = df[df['onPremisesSamAccountName'].str.startswith(('DQ', 'AP'))].copy()

    with _cache_lock:
        _df_cache[(abs_path, mtime)] = filtered_df
    return filtered_df


def _get_cached_result(file_path: str, name: str, compute):
    abs_path, mtime = _cache_key(file_path)
    cache_id = (abs_path, mtime, name)
    with _cache_lock:
        if cache_id in _result_cache:
            return _result_cache[cache_id]
    value = compute()
    with _cache_lock:
        _result_cache[cache_id] = value
    return value


def transform_ad_data(file_path):
    logger.info('Transforming AD data')
    try:
        def compute():
            filtered_df = _get_filtered_ad_df(file_path)
            return [
                {
                    "name": row['displayName'],
                    "email": row['mail'],
                    "dq": row['onPremisesSamAccountName']
                }
                for _, row in filtered_df.iterrows()
            ]

        return _get_cached_result(file_path, 'data', compute)
    except Exception as e:
        logger.error(f"Error handling files: {e}")
        return []


def transform_ad_email(file_path):
    logger.info('Transforming AD email')
    try:
        def compute():
            filtered_df = _get_filtered_ad_df(file_path)
            emails = [email for email in filtered_df['mail'].tolist() if email]
            logger.info(f"Emails with onPremisesSamAccountName starting with 'DQ' or 'AP': {emails}")
            return emails

        return _get_cached_result(file_path, 'email', compute)
    except Exception as e:
        logger.error(f"Error handling files: {e}")
        return []


def transform_ad_dq_number(file_path):
    logger.info('Transforming AD DQ number')
    try:
        def compute():
            filtered_df = _get_filtered_ad_df(file_path)
            dq_numbers = [dq for dq in filtered_df['onPremisesSamAccountName'].tolist() if dq]
            logger.info(f"DQ numbers with onPremisesSamAccountName starting with 'DQ' or 'AP': {dq_numbers}")
            return dq_numbers

        return _get_cached_result(file_path, 'dq_numbers', compute)
    except Exception as e:
        logger.error(f"Error handling files: {e}")
        return []


def transform_ad_fullname(file_path):
    logger.info('Transforming AD full name')
    try:
        def compute():
            filtered_df = _get_filtered_ad_df(file_path)
            remove_values = ['Vikar', 'Distrikt Bakkegården', 'Afløser', 'Langå', 'Mobil', 'Vorup Plejecenter']

            for value in remove_values:
                filtered_df = filtered_df[~filtered_df['displayName'].str.contains(value, case=False, na=False)]

            fullnames = [name for name in filtered_df['displayName'].tolist() if name]
            logger.info(f"Full names with onPremisesSamAccountName starting with 'DQ' or 'AP': {fullnames}")
            return fullnames

        return _get_cached_result(file_path, 'fullnames', compute)
    except Exception as e:
        logger.error(f"Error handling files: {e}")
        return []
