import pandas as pd

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import OckovaniSpotreba, OckovaciMisto, KapacityNemocnic


class HospitalCapacitiesFetcher(Fetcher):
    """
    Class for updating capacities in hospitals.
    """

    CAPACITIES_CSV = 'https://dip.mzcr.cz/api/v1/kapacity-intenzivni-pece-zdravotnicke-zarizeni-10-2021.csv'

    def __init__(self):
        super().__init__(KapacityNemocnic.__tablename__, self.CAPACITIES_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        for col in df.columns:
            if col not in ['datum', 'zz_kod', 'zz_nazev', 'kraj_nuts_kod', 'kraj_nazev']:
                df[col] = df[col].fillna('0').astype('int')

        df = df.drop('kraj_nazev', axis=1)

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
