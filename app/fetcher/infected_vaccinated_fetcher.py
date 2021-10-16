import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import NakazeniOckovani


class InfectedVaccinatedFetcher(Fetcher):
    """
    Class for updating infected table.
    """

    INFECTED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-pozitivni.csv'

    def __init__(self):
        super().__init__(NakazeniOckovani.__tablename__, self.INFECTED_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df[['datum', 'pozitivni_celkem', 'pozitivni_bez_ockovani', 'pozitivni_bez_ockovani_vek_prumer',
                 'pozitivni_nedokoncene_ockovani', 'pozitivni_nedokoncene_ockovani_vek_prumer',
                 'pozitivni_dokoncene_ockovani', 'pozitivni_dokoncene_ockovani_vek_prumer',
                 'pozitivni_posilujici_davka', 'pozitivni_posilujici_davka_vek_prumer']]

        df = df.rename(columns={'pozitivni_celkem': 'celkem',
                                'pozitivni_bez_ockovani': 'bez_ockovani',
                                'pozitivni_bez_ockovani_vek_prumer': 'bez_ockovani_vek_prumer',
                                'pozitivni_nedokoncene_ockovani': 'nedokoncene_ockovani',
                                'pozitivni_nedokoncene_ockovani_vek_prumer': 'nedokoncene_ockovani_vek_prumer',
                                'pozitivni_dokoncene_ockovani': 'dokoncene_ockovani',
                                'pozitivni_dokoncene_ockovani_vek_prumer': 'dokoncene_ockovani_vek_prumer',
                                'pozitivni_posilujici_davka': 'posilujici_davka',
                                'pozitivni_posilujici_davka_vek_prumer': 'posilujici_davka_vek_prumer'})

        df['bez_ockovani_vek_prumer'] = df['bez_ockovani_vek_prumer'].fillna(0).astype('int')
        df['nedokoncene_ockovani_vek_prumer'] = df['nedokoncene_ockovani_vek_prumer'].fillna(0).astype('int')
        df['dokoncene_ockovani_vek_prumer'] = df['dokoncene_ockovani_vek_prumer'].fillna(0).astype('int')
        df['posilujici_davka_vek_prumer'] = df['posilujici_davka_vek_prumer'].fillna(0).astype('int')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
