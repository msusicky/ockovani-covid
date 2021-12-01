import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import Hospitalizace


class HospitalizedFetcher(Fetcher):
    """
    Class for updating hospitalized people table.
    """

    HOSPITALIZED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/hospitalizace.csv'

    def __init__(self):
        super().__init__(Hospitalizace.__tablename__, self.HOSPITALIZED_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df.drop(columns=['id'])

        for col in df.columns:
            if col != 'datum':
                df[col] = df[col].fillna('0').astype('int')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
