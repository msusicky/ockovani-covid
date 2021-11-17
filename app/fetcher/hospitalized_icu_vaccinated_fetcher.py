import modin.pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import HospitalizaceJipOckovani


class HospitalizedIcuVaccinatedFetcher(Fetcher):
    """
    Class for updating hospitalized ICU table.
    """

    HOSPITALIZED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-jip.csv'

    def __init__(self):
        super().__init__(HospitalizaceJipOckovani.__tablename__, self.HOSPITALIZED_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df[['datum', 'jip_celkem', 'jip_bez_ockovani', 'jip_bez_ockovani_vek_prumer',
                 'jip_nedokoncene_ockovani', 'jip_nedokoncene_ockovani_vek_prumer',
                 'jip_dokoncene_ockovani', 'jip_dokoncene_ockovani_vek_prumer',
                 'jip_posilujici_davka', 'jip_posilujici_davka_vek_prumer']]

        df = df.rename(columns={'jip_celkem': 'celkem',
                                'jip_bez_ockovani': 'bez_ockovani',
                                'jip_bez_ockovani_vek_prumer': 'bez_ockovani_vek_prumer',
                                'jip_nedokoncene_ockovani': 'nedokoncene_ockovani',
                                'jip_nedokoncene_ockovani_vek_prumer': 'nedokoncene_ockovani_vek_prumer',
                                'jip_dokoncene_ockovani': 'dokoncene_ockovani',
                                'jip_dokoncene_ockovani_vek_prumer': 'dokoncene_ockovani_vek_prumer',
                                'jip_posilujici_davka': 'posilujici_davka',
                                'jip_posilujici_davka_vek_prumer': 'posilujici_davka_vek_prumer'})

        df['bez_ockovani_vek_prumer'] = df['bez_ockovani_vek_prumer'].fillna(0).astype('int')
        df['nedokoncene_ockovani_vek_prumer'] = df['nedokoncene_ockovani_vek_prumer'].fillna(0).astype('int')
        df['dokoncene_ockovani_vek_prumer'] = df['dokoncene_ockovani_vek_prumer'].fillna(0).astype('int')
        df['posilujici_davka_vek_prumer'] = df['posilujici_davka_vek_prumer'].fillna(0).astype('int')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
