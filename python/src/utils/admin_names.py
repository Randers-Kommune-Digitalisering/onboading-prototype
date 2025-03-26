import pandas as pd
import io
import logging

logger = logging.getLogger(__name__)


def handle_files(connection):
    logger.info('Handling SFTP-SDRoller file')
    try:
        with connection.open('/Brugeradministration-da.csv') as f:
            content = f.read().decode('utf-16')
            needed_cols = ['Navn', 'Rolle']
            df = pd.read_csv(io.StringIO(content), sep=";", header=0, decimal=",", na_filter=False, usecols=needed_cols)
            leder_df = df[df['Rolle'] == 'Leder']
            leder_df = leder_df.drop_duplicates(subset=['Navn'])
            leder_names = leder_df['Navn'].tolist()
            logger.info(f"Names with Rolle as Leder: {leder_names}")
            return leder_names
    except Exception as e:
        logger.error(f"Error handling files: {e}")
        return []
