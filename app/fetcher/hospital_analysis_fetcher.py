from datetime import datetime
from typing import Optional

import pandas as pd
import requests

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import AnalyzaHospitalizaci


class HospitalAnalysisFetcher(Fetcher):
    """
    Class for updating UZIS Hospital analysis.
    """

    HOSPITAL_ANALYSIS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/account/{}/file/modely%252Fmodely_05_hospitalizovani_analyza.csv'

    def __init__(self):
        token = app.config['UZIS_TOKEN']
        url = self.HOSPITAL_ANALYSIS_CSV.format(token)
        super().__init__(AnalyzaHospitalizaci.__tablename__, url, check_date=False)

    def get_modified_time(self) -> Optional[datetime]:
        headers = requests.head(url=self._url).headers
        if 'content-disposition' in headers:
            filename = headers['content-disposition']
            modified_date = filename.split('.')[0].split('_')[-1]
            return datetime.strptime(modified_date, '%Y-%m-%d-%H-%M-%S')
        else:
            return None

    def fetch(self, import_id: int) -> None:
        if self._url is None:
            return

        df = pd.read_csv(self._url, delimiter=";", header=0)

        df['jip'] = df['jip'].fillna(False).astype('bool')
        df['dni_jip'] = df['dni_jip'].fillna(0).astype('int')
        df['umrti'] = df['umrti'].fillna(False).astype('bool')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
