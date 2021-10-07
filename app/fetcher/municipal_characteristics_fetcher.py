import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import CharakteristikaObci


class MunicipalCharacteristicsFetcher(Fetcher):
    """
    Class for updating municipal characteristics table.
    """

    CHARACTERISTICS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/obce.csv'

    def __init__(self):
        super().__init__(CharakteristikaObci.__tablename__, self.CHARACTERISTICS_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df['kraj_kod'] = df['kraj_nuts_kod']
        df['okres_kod'] = df['okres_lau_kod']

        df = df[['datum', 'kraj_kod', 'okres_kod', 'orp_kod', 'nove_pripady', 'aktivni_pripady', 'nove_pripady_65',
                 'nove_pripady_7_dni', 'nove_pripady_14_dni']]

        df['kraj_kod'] = df['kraj_kod'].fillna('-')
        df['okres_kod'] = df['okres_kod'].fillna('-')
        df['orp_kod'] = df['orp_kod'].fillna('-').astype(str).str[:4]

        df = df.groupby(['datum', 'kraj_kod', 'okres_kod', 'orp_kod'], dropna=False).sum().reset_index()

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
