import os

import pandas as pd
import requests

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaniLideProfese


class VaccinatedProfessionsFetcher(Fetcher):
    """
    Class for updating vaccinated professions table.
    """

    VACCINATED_PROFESSIONS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-profese.csv'

    def __init__(self):
        url = os.environ.get('ODL_VACCINATED_ENH')
        super().__init__(OckovaniLideProfese.__tablename__,
                         url if url is not None and requests.head(url).status_code == 200 else self.VACCINATED_PROFESSIONS_CSV)

    def fetch(self, import_id: int) -> None:
        usecols = ['datum', 'datum_vakcinace', 'vakcina', 'kraj_nuts_kod', 'kraj_kod', 'orp_bydliste_kod',
                   'zarizeni_kod', 'poradi_davky', 'vekova_skupina', 'bezpecnostni_infrastruktura',
                   'chronicke_onemocneni']

        df = pd.read_csv(self._url, dtype={'zarizeni_kod': 'object'},
                         usecols=lambda c: c.startswith('indikace_') or c in usecols)

        df = df.rename(columns={'kraj_kod': 'kraj_nuts_kod', 'datum_vakcinace': 'datum',
                                'bezpecnostni_infrastruktura': 'indikace_bezpecnostni_infrastruktura',
                                'chronicke_onemocneni': 'indikace_chronicke_onemocneni'})

        df['orp_bydl_kod'] = df['orp_bydliste_kod'].astype(str).str[:4]

        df['zarizeni_kod'] = df['zarizeni_kod'].str.zfill(11)

        df['indikace_zdravotnik'] = df['indikace_zdravotnik'].fillna(False).astype('bool')
        df['indikace_socialni_sluzby'] = df['indikace_socialni_sluzby'].fillna(False).astype('bool')
        df['indikace_ostatni'] = df['indikace_ostatni'].fillna(False).astype('bool')
        df['indikace_pedagog'] = df['indikace_pedagog'].fillna(False).astype('bool')
        df['indikace_skolstvi_ostatni'] = df['indikace_skolstvi_ostatni'].fillna(False).astype('bool')
        df['indikace_bezpecnostni_infrastruktura'] = df['indikace_bezpecnostni_infrastruktura'].fillna(False).astype('bool')
        df['indikace_chronicke_onemocneni'] = df['indikace_chronicke_onemocneni'].fillna(False).astype('bool')

        orp = pd.read_sql_query('select uzis_orp orp_bydl_kod, kraj_nuts kraj_bydl_nuts from obce_orp', db.engine)
        df = pd.merge(df, orp, how='left')
        df['kraj_bydl_nuts'] = df['kraj_bydl_nuts'].fillna('-')

        df = df[['datum', 'vakcina', 'kraj_nuts_kod', 'zarizeni_kod', 'poradi_davky', 'vekova_skupina',
                 'kraj_bydl_nuts', 'indikace_zdravotnik', 'indikace_socialni_sluzby', 'indikace_ostatni',
                 'indikace_pedagog', 'indikace_skolstvi_ostatni', 'indikace_bezpecnostni_infrastruktura',
                 'indikace_chronicke_onemocneni']]

        df = df.groupby(df.columns.tolist(), dropna=False).size().reset_index(name='pocet')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
