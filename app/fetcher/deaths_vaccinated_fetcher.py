import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import UmrtiOckovani


class DeathsVaccinatedFetcher(Fetcher):
    """
    Class for updating deaths table.
    """

    DEATHS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-umrti.csv'

    def __init__(self):
        super().__init__(UmrtiOckovani.__tablename__, self.DEATHS_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df[['datum', 'zemreli_celkem', 'zemreli_bez_ockovani', 'zemreli_bez_ockovani_vek_prumer',
                 'zemreli_nedokoncene_ockovani', 'zemreli_nedokoncene_ockovani_vek_prumer',
                 'zemreli_dokoncene_ockovani', 'zemreli_dokoncene_ockovani_vek_prumer',
                 'zemreli_posilujici_davka', 'zemreli_posilujici_davka_vek_prumer']]

        df = df.rename(columns={'zemreli_celkem': 'celkem',
                                'zemreli_bez_ockovani': 'bez_ockovani',
                                'zemreli_bez_ockovani_vek_prumer': 'bez_ockovani_vek_prumer',
                                'zemreli_nedokoncene_ockovani': 'nedokoncene_ockovani',
                                'zemreli_nedokoncene_ockovani_vek_prumer': 'nedokoncene_ockovani_vek_prumer',
                                'zemreli_dokoncene_ockovani': 'dokoncene_ockovani',
                                'zemreli_dokoncene_ockovani_vek_prumer': 'dokoncene_ockovani_vek_prumer',
                                'zemreli_posilujici_davka': 'posilujici_davka',
                                'zemreli_posilujici_davka_vek_prumer': 'posilujici_davka_vek_prumer'})

        df['bez_ockovani_vek_prumer'] = df['bez_ockovani_vek_prumer'].fillna(0).astype('int')
        df['nedokoncene_ockovani_vek_prumer'] = df['nedokoncene_ockovani_vek_prumer'].fillna(0).astype('int')
        df['dokoncene_ockovani_vek_prumer'] = df['dokoncene_ockovani_vek_prumer'].fillna(0).astype('int')
        df['posilujici_davka_vek_prumer'] = df['posilujici_davka_vek_prumer'].fillna(0).astype('int')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
