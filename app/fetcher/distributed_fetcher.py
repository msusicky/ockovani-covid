import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaniDistribuce


class DistributedFetcher(Fetcher):
    """
    Class for updating distributed vaccines table.
    """

    DISTRIBUTED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-distribuce.csv'

    def __init__(self):
        super().__init__(OckovaniDistribuce.__tablename__, self.DISTRIBUTED_CSV, ignore_errors=True)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df['cilove_ockovaci_misto_id'] = df['cilove_ockovaci_misto_id'].fillna('-')

        df = df.groupby(['datum', 'ockovaci_misto_id', 'cilove_ockovaci_misto_id', 'ockovaci_latka', 'vyrobce',
                         'akce'], dropna=False) \
            .sum() \
            .reset_index()

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
