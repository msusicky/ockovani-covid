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
        df['incidence_pozitivni'] = df['incidence_pozitivni'].fillna(-1).astype(int)
        df['pozit_typologie_test_indik_diagnosticka'] = df['pozit_typologie_test_indik_diagnosticka'].fillna(-1).astype(int)
        df['pozit_typologie_test_indik_epidemiologicka'] = df['pozit_typologie_test_indik_epidemiologicka'].fillna(-1).astype(int)
        df['pozit_typologie_test_indik_preventivni'] = df['pozit_typologie_test_indik_preventivni'].fillna(
            -1).astype(int)
        df['pozit_typologie_test_indik_ostatni'] = df['pozit_typologie_test_indik_ostatni'].fillna(-1).astype(
            int)
        df['PCR_pozit_sympt'] = df['PCR_pozit_sympt'].fillna(-1).astype(
            int)
        df['AG_pozit_symp'] = df['AG_pozit_symp'].fillna(-1).astype(
            int)
        df['AG_pozit_asymp_PCR_conf'] = df['AG_pozit_asymp_PCR_conf'].fillna(-1).astype(
            int)
        df['PCR_pozit_asymp'] = df['PCR_pozit_asymp'].fillna(-1).astype(
            int)
        df['PCR_pozit_sympt'] = df['PCR_pozit_sympt'].fillna(-1).astype(
            int)
        df = df.drop(columns=['id'])

        df = df.rename(columns=str.lower)

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
