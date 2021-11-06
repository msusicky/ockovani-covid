import os
from datetime import datetime
from typing import Optional

import requests
from pandas import DataFrame

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto, ProvozniDoba, OckovaciMistoDetail


class OpeningHoursFetcher(Fetcher):
    """
    Class for updating opening hours table.
    """

    API_URL = 'https://cfa.uzis.cz/api/v1/'
    OPENING_HOURS = 'vaccination-center/{}/opening-hours/'

    def __init__(self):
        super().__init__(ProvozniDoba.__tablename__, self.API_URL + self.OPENING_HOURS)

    def get_modified_time(self) -> Optional[datetime]:
        return datetime.today()

    def fetch(self, import_id: int) -> None:
        user = os.environ.get('CFA_USER')
        password = os.environ.get('CFA_PASS')

        # select only walkin centers
        mista = db.session.query(OckovaciMisto.id) \
            .join(OckovaciMistoDetail) \
            .filter(OckovaciMistoDetail.typ == 'WALKIN') \
            .all()
        mista_ids = [r[0] for r in mista]

        self._truncate()

        for id in mista_ids:
            r = requests.get(self._url.format(id), auth=(user, password))
            df = DataFrame(r.json()['results'])

            if df.empty:
                continue

            df = df.groupby(['weekday', 'from_hour', 'to_hour']).min().reset_index()

            for idx, row in df.iterrows():
                db.session.add(ProvozniDoba(
                    ockovaci_misto_id=id,
                    den=row['weekday'],
                    od=row['from_hour'],
                    do=row['to_hour']
            ))

        db.session.commit()
