import os

import pandas as pd
import requests

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaniLideProfese, AnalyzaHospitalizaci


class HospitalAnalysisFetcher(Fetcher):
    """
    Class for updating UZIS Hospital analysis.
    """

    HOSPITAL_ANALYSIS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/account/{}/file/modely%252Fmodely_05_hospitalizovani_analyza.csv'

    def __init__(self):
        token = os.environ.get('ODL_UZIS_TOKEN')
        url = self.HOSPITAL_ANALYSIS_CSV.format(token)
        super().__init__(AnalyzaHospitalizaci.__tablename__,
                         url if url is not None and requests.head(url).status_code == 200 else None, check_date=False)

    def fetch(self, import_id: int) -> None:
        if self._url is None:
            return

        df = pd.read_csv(self._url, delimiter=";", header=0)

        df['jip'] = df['jip'].fillna(False).astype('bool')
        df['dni_jip'] = df['dni_jip'].fillna(0).astype('int')
        df['umrti'] = df['umrti'].fillna(False).astype('bool')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
