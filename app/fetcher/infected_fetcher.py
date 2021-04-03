import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import Nakazeni


class InfectedFetcher(Fetcher):
    """
    Class for updating infected people table.
    """

    INFECTED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/osoby.csv'

    def __init__(self):
        super().__init__(Nakazeni.__tablename__, self.INFECTED_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df['kraj_nuts_kod'] = df['kraj_nuts_kod'].fillna('-')

        df = df[['datum', 'vek', 'kraj_nuts_kod']]

        df = df.groupby(df.columns.tolist(), dropna=False).size().reset_index(name='pocet')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
