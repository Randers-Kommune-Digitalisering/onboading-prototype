import io
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)


def transform_ad_email(file_path):
    logger.info('Transforming AD email')
    try:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            raise FileNotFoundError(f"No such file or directory: '{file_path}'")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            needed_cols = ['mail', 'onPremisesSamAccountName']
            df = pd.read_csv(io.StringIO(content), sep=",", header=0, na_filter=False, usecols=needed_cols)

            filtered_df = df[df['onPremisesSamAccountName'].str.startswith(('DQ', 'AP'))]
            emails = [email for email in filtered_df['mail'].tolist() if email]
            logger.info(f"Emails with onPremisesSamAccountName starting with 'DQ' or 'AP': {emails}")
            return emails
    except Exception as e:
        logger.error(f"Error handling files: {e}")
        return []


def transform_ad_dq_number(file_path):
    logger.info('Transforming AD DQ number')
    try:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            raise FileNotFoundError(f"No such file or directory: '{file_path}'")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            needed_cols = ['onPremisesSamAccountName']
            df = pd.read_csv(io.StringIO(content), sep=",", header=0, na_filter=False, usecols=needed_cols)

            filtered_df = df[df['onPremisesSamAccountName'].str.startswith(('DQ', 'AP'))]
            dq_numbers = [dq for dq in filtered_df['onPremisesSamAccountName'].tolist() if dq]
            logger.info(f"DQ numbers with onPremisesSamAccountName starting with 'DQ' or 'AP': {dq_numbers}")
            return dq_numbers
    except Exception as e:
        logger.error(f"Error handling files: {e}")
        return []


def transform_ad_fullname(file_path):
    logger.info('Transforming AD full name')
    try:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            raise FileNotFoundError(f"No such file or directory: '{file_path}'")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            needed_cols = ['displayName', 'onPremisesSamAccountName']
            df = pd.read_csv(io.StringIO(content), sep=",", header=0, na_filter=False, usecols=needed_cols)

            filtered_df = df[df['onPremisesSamAccountName'].str.startswith(('DQ', 'AP'))]
            fullnames = [name for name in filtered_df['displayName'].tolist() if name]
            logger.info(f"Full names with onPremisesSamAccountName starting with 'DQ' or 'AP': {fullnames}")
            return fullnames
    except Exception as e:
        logger.error(f"Error handling files: {e}")
        return []
