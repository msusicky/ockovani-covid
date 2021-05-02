import numpy as np
import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto


class CentersFetcher(Fetcher):
    """
    Class for updating vaccination centers table.
    """

    CENTERS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/prehled-ockovacich-mist.csv'

    def __init__(self):
        super().__init__(OckovaciMisto.__tablename__, self.CENTERS_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url, dtype={'nrpzs_kod': 'object'})

        df['operacni_status'] = df['operacni_status'].fillna(False).astype('bool')
        df['bezbarierovy_pristup'] = df['bezbarierovy_pristup'].fillna(False).astype('bool')
        df['latitude'] = df['latitude'].replace({np.nan: None})
        df['longitude'] = df['longitude'].replace({np.nan: None})
        df['nrpzs_kod'] = df['nrpzs_kod'].str.zfill(11)

        # set all centers disabled to disable centers removed from the list
        db.session.query(OckovaciMisto).update({OckovaciMisto.status: False})

        for idx, row in df.iterrows():
            db.session.merge(OckovaciMisto(
                id=row['ockovaci_misto_id'],
                nazev=row['ockovaci_misto_nazev'],
                okres_id=row['okres_nuts_kod'],
                status=row['operacni_status'],
                adresa=row['ockovaci_misto_adresa'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                nrpzs_kod=row['nrpzs_kod'],
                minimalni_kapacita=row['minimalni_kapacita'],
                bezbarierovy_pristup=row['bezbarierovy_pristup']
            ))

        db.session.commit()
