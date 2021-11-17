import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import HospitalizaceOckovani


class HospitalizedVaccinatedFetcher(Fetcher):
    """
    Class for updating hospitalized table.
    """

    HOSPITALIZED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-hospitalizace.csv'

    def __init__(self):
        super().__init__(HospitalizaceOckovani.__tablename__, self.HOSPITALIZED_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df[['datum', 'hospitalizovani_celkem', 'hospitalizovani_bez_ockovani', 'hospitalizovani_bez_ockovani_vek_prumer',
                 'hospitalizovani_nedokoncene_ockovani', 'hospitalizovani_nedokoncene_ockovani_vek_prumer',
                 'hospitalizovani_dokoncene_ockovani', 'hospitalizovani_dokoncene_ockovani_vek_prumer',
                 'hospitalizovani_posilujici_davka', 'hospitalizovani_posilujici_davka_vek_prumer']]

        df = df.rename(columns={'hospitalizovani_celkem': 'celkem',
                                'hospitalizovani_bez_ockovani': 'bez_ockovani',
                                'hospitalizovani_bez_ockovani_vek_prumer': 'bez_ockovani_vek_prumer',
                                'hospitalizovani_nedokoncene_ockovani': 'nedokoncene_ockovani',
                                'hospitalizovani_nedokoncene_ockovani_vek_prumer': 'nedokoncene_ockovani_vek_prumer',
                                'hospitalizovani_dokoncene_ockovani': 'dokoncene_ockovani',
                                'hospitalizovani_dokoncene_ockovani_vek_prumer': 'dokoncene_ockovani_vek_prumer',
                                'hospitalizovani_posilujici_davka': 'posilujici_davka',
                                'hospitalizovani_posilujici_davka_vek_prumer': 'posilujici_davka_vek_prumer'})

        df['bez_ockovani_vek_prumer'] = df['bez_ockovani_vek_prumer'].fillna(0).astype('int')
        df['nedokoncene_ockovani_vek_prumer'] = df['nedokoncene_ockovani_vek_prumer'].fillna(0).astype('int')
        df['dokoncene_ockovani_vek_prumer'] = df['dokoncene_ockovani_vek_prumer'].fillna(0).astype('int')
        df['posilujici_davka_vek_prumer'] = df['posilujici_davka_vek_prumer'].fillna(0).astype('int')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
