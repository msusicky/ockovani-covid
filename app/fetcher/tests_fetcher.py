import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import Testy


class TestsFetcher(Fetcher):
    """
    Class for updating hospitalized people table.
    """

    TESTS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/testy-pcr-antigenni.csv'

    def __init__(self):
        super().__init__(Testy.__tablename__, self.TESTS_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df.drop(columns=['id'])

        df = df.rename(columns=str.lower)

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
