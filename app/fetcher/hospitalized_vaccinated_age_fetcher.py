import modin.pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import HospitalizaceOckovaniVek


class HospitalizedVaccinatedAgeFetcher(Fetcher):
    """
    Class for updating hospitalized with age table.
    """

    HOSPITALIZED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-hospitalizace-tyden.csv'

    def __init__(self):
        super().__init__(HospitalizaceOckovaniVek.__tablename__, self.HOSPITALIZED_CSV)

    def fetch(self, import_id: int) -> None:
        usecols = ['tyden', 'tyden_od', 'tyden_do', 'vekova_skupina', 'hospitalizovani_celkem',
                   'hospitalizovani_bez_ockovani', 'hospitalizovani_nedokoncene_ockovani',
                   'hospitalizovani_dokoncene_ockovani', 'hospitalizovani_posilujici_davka']

        df = pd.read_csv(self._url, usecols=usecols)

        df = df.rename(columns={'hospitalizovani_celkem': 'hospitalizace_celkem',
                                'hospitalizovani_bez_ockovani': 'hospitalizace_bez',
                                'hospitalizovani_nedokoncene_ockovani': 'hospitalizace_castecne',
                                'hospitalizovani_dokoncene_ockovani': 'hospitalizace_plne',
                                'hospitalizovani_posilujici_davka': 'hospitalizace_posilujici'})

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
