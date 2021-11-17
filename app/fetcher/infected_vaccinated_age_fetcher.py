import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import NakazeniOckovaniVek


class InfectedVaccinatedAgeFetcher(Fetcher):
    """
    Class for updating infected with age table.
    """

    INFECTED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-pozitivni-tyden.csv'

    def __init__(self):
        super().__init__(NakazeniOckovaniVek.__tablename__, self.INFECTED_CSV)

    def fetch(self, import_id: int) -> None:
        usecols = ['tyden', 'tyden_od', 'tyden_do', 'vekova_skupina', 'pozitivni_celkem', 'pozitivni_bez_ockovani',
                   'pozitivni_nedokoncene_ockovani', 'pozitivni_dokoncene_ockovani', 'pozitivni_posilujici_davka']

        df = pd.read_csv(self._url, usecols=usecols)

        df = df.rename(columns={'pozitivni_celkem': 'nakazeni_celkem',
                                'pozitivni_bez_ockovani': 'nakazeni_bez',
                                'pozitivni_nedokoncene_ockovani': 'nakazeni_castecne',
                                'pozitivni_dokoncene_ockovani': 'nakazeni_plne',
                                'pozitivni_posilujici_davka': 'nakazeni_posilujici'})

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
