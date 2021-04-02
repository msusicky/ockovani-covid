import os

import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaniLideProfese


class VaccinatedProfessionsFetcher(Fetcher):
    """
    Class for updating vaccinated professions table.
    """

    VACCINATED_PROFESSIONS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-profese.csv'

    def __init__(self):
        path = os.environ.get('ODL_VACCINATED_ENH')
        super().__init__(OckovaniLideProfese.__tablename__,
                         path if path is not None and os.path.exists(path) else self.VACCINATED_PROFESSIONS_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url, dtype={'zarizeni_kod': 'object'})

        if 'orp_bydl_kod' in df:
            df['orp_bydl_kod'] = df['orp_bydliste_kod'].astype(str).str[:4]
            orp_kraj = pd.read_sql_query('select uzis_orp orp_bydl_kod, kraj_nuts kraj_bydl_nuts from obce_orp',
                                         db.engine)
            df = pd.merge(df, orp_kraj, how='left')
            df = df.drop('orp_bydliste_kod', axis=1)
            df = df.rename(columns={'kraj_kod': 'kraj_nuts_kod', 'datum_vakcinace': 'datum'})
        else:
            df['vekova_skupina'] = 'N/A'
            df['kraj_bydl_nuts'] = 'N/A'

        df = df.groupby(['datum', 'vakcina', 'kraj_nuts_kod', 'zarizeni_kod', 'poradi_davky', 'vekova_skupina',
                         'kraj_bydl_nuts', 'indikace_zdravotnik', 'indikace_socialni_sluzby', 'indikace_ostatni',
                         'indikace_pedagog', 'indikace_skolstvi_ostatni']) \
            .size() \
            .reset_index(name='pocet')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
