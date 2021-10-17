import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import SituaceOrp


class OrpSituationFetcher(Fetcher):
    """
    Class for updating municipal characteristics table.
    """

    SITUATION_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/orp.csv'

    def __init__(self):
        super().__init__(SituaceOrp.__tablename__, self.SITUATION_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df[['datum', 'orp_kod', 'incidence_7', 'incidence_65_7', 'incidence_75_7', 'prevalence', 'prevalence_65',
                 'prevalence_75', 'aktualni_pocet_hospitalizovanych_osob', 'nove_hosp_7', 'testy_7']]

        df['orp_kod'] = df['orp_kod'].replace(0, 1000).astype(str).str[:4]

        df = df.rename(columns={'aktualni_pocet_hospitalizovanych_osob': 'pocet_hosp'})

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
