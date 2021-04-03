import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaniSpotreba


class UsedFetcher(Fetcher):
    """
    Class for updating used vaccines table.
    """

    USED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-spotreba.csv'

    def __init__(self):
        super().__init__(OckovaniSpotreba.__tablename__, self.USED_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df['kraj_nuts_kod'] = df['kraj_nuts_kod'].fillna('-')

        df = df.groupby(['datum', 'ockovaci_misto_id', 'ockovaci_latka', 'vyrobce'], dropna=False).sum().reset_index()

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
