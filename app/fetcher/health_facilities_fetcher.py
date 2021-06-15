import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciZarizeni


class HealthFacilitiesFetcher(Fetcher):
    """
    Class for updating health facilities table.
    """

    FACILITIES_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovaci-zarizeni.csv'

    def __init__(self):
        super().__init__(OckovaciZarizeni.__tablename__, self.FACILITIES_CSV, check_date=False)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url, dtype={'zarizeni_kod': 'object'})

        df['zarizeni_kod'] = df['zarizeni_kod'].str.zfill(11)
        df['provoz_zahajen'] = df['provoz_zahajen'].fillna(False).astype('bool')
        df['prakticky_lekar'] = df['prakticky_lekar'].fillna(False).astype('bool')

        df = df.drop(['kraj_nuts_kod', 'kraj_nazev', 'okres_nazev'], axis=1)
        df = df.rename(columns={'zarizeni_kod': 'id', 'okres_lau_kod': 'okres_id'})

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
