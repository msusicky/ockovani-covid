import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaniLide


class VaccinatedFetcher(Fetcher):
    """
    Class for updating vaccinated people table.
    """

    VACCINATED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovaci-mista.csv'

    def __init__(self):
        super().__init__(OckovaniLide.__tablename__, self.VACCINATED_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url, dtype={'zarizeni_kod': 'object'})

        df = df.groupby(['datum', 'vakcina', 'kraj_nuts_kod', 'kraj_nazev', 'zarizeni_kod', 'zarizeni_nazev',
                         'poradi_davky', 'vekova_skupina']) \
            .size() \
            .reset_index(name='pocet')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
