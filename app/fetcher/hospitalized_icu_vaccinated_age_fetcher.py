import modin.pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import HospitalizaceJipOckovaniVek


class HospitalizedIcuVaccinatedAgeFetcher(Fetcher):
    """
    Class for updating hospitalized ICU with age table.
    """

    HOSPITALIZED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-jip-tyden.csv'

    def __init__(self):
        super().__init__(HospitalizaceJipOckovaniVek.__tablename__, self.HOSPITALIZED_CSV)

    def fetch(self, import_id: int) -> None:
        usecols = ['tyden', 'tyden_od', 'tyden_do', 'vekova_skupina', 'jip_celkem', 'jip_bez_ockovani',
                   'jip_nedokoncene_ockovani', 'jip_dokoncene_ockovani', 'jip_posilujici_davka']

        df = pd.read_csv(self._url, usecols=usecols)

        df = df.rename(columns={'jip_celkem': 'hospitalizace_jip_celkem',
                                'jip_bez_ockovani': 'hospitalizace_jip_bez',
                                'jip_nedokoncene_ockovani': 'hospitalizace_jip_castecne',
                                'jip_dokoncene_ockovani': 'hospitalizace_jip_plne',
                                'jip_posilujici_davka': 'hospitalizace_jip_posilujici'})

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
