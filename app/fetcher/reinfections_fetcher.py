import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import Reinfekce


class ReinfectionsFetcher(Fetcher):
    """
    Class for updating reinfections table.
    """

    REINFECTIONS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/prehled-reinfekce.csv'

    def __init__(self):
        super().__init__(Reinfekce.__tablename__, self.REINFECTIONS_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df.rename(columns={'60_dnu': 'pocet'})

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
