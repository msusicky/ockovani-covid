from datetime import date

import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import ZdravotnickeStredisko


class HealthFacilitiesNrpzsFetcher(Fetcher):
    """
    Class for updating health facilities NRPZS table.
    """

    today = date.today()
    FACILITIES_CSV = f'https://nrpzs.uzis.cz/res/file/export/export-{today.strftime("%Y")}-{today.strftime("%m")}.csv'

    def __init__(self):
        super().__init__(ZdravotnickeStredisko.__tablename__, self.FACILITIES_CSV, check_date=False)

    def fetch(self, import_id: int) -> None:
        usecols = ['ZdravotnickeZarizeniId', 'PCZ', 'PCDP', 'NazevCely', 'ZdravotnickeZarizeniKod', 'DruhZarizeniKod',
                   'DruhZarizeni', 'Obec', 'Psc', 'Ulice', 'CisloDomovniOrientacni', 'Kraj', 'KrajKod', 'Okres',
                   'OkresKod', 'PoskytovatelTelefon', 'PoskytovatelEmail', 'PoskytovatelWeb', 'GPS']
        dtype = {'ZdravotnickeZarizeniKod': 'object', 'Psc': 'object', 'PoskytovatelTelefon': 'object'}

        df = pd.read_csv(self.FACILITIES_CSV, sep=';', encoding='cp1250', usecols=usecols, dtype=dtype)

        df = df.rename(columns={'ZdravotnickeZarizeniId': 'zdravotnicke_zarizeni_id', 'PCZ': 'pcz', 'PCDP': 'pcdp',
                                'NazevCely': 'nazev_cely', 'ZdravotnickeZarizeniKod': 'zdravotnicke_zarizeni_kod',
                                'DruhZarizeniKod': 'druh_zarizeni_kod', 'DruhZarizeni': 'druh_zarizeni', 'Obec': 'obec',
                                'Psc': 'psc', 'Ulice': 'ulice', 'CisloDomovniOrientacni': 'cislo_domu', 'Kraj': 'kraj',
                                'KrajKod': 'kraj_kod', 'Okres': 'okres', 'OkresKod': 'okres_kod',
                                'PoskytovatelTelefon': 'telefon', 'PoskytovatelEmail': 'email',
                                'PoskytovatelWeb': 'web'})

        df['nrpzs_kod'] = df['zdravotnicke_zarizeni_kod'].str[:-3]
        df[['latitude', 'longitude']] = df['GPS'].str.split(" ", n=2, expand=True)

        df = df.drop('GPS', axis=1)

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
