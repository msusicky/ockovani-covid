import os
from datetime import date, datetime
from typing import Optional

import requests
from dateutil.relativedelta import relativedelta
from pandas import DataFrame

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto, OckovaniRezervace


class ReservationsFetcherApi(Fetcher):
    """
    Class for updating reservations table.
    """

    API_URL = 'https://api.reservatic.com/api/nakit/v2/'
    VACCINE_SERVICES = 'vaccine_services/stats/'

    def __init__(self):
        super().__init__(OckovaniRezervace.__tablename__, self.API_URL + self.VACCINE_SERVICES, check_date=False)

    def get_modified_date(self) -> Optional[datetime]:
        return datetime.today()

    def fetch(self, import_id: int) -> None:
        token = os.environ.get('ODL_RESERVATIC_API')
        if token is None:
            raise ValueError("ODL_RESERVATIC_API variable is empty")

        ocms = db.session.query(OckovaciMisto) \
            .order_by(OckovaciMisto.id) \
            .all()

        # create the right date interval
        week_before = datetime.now() + relativedelta(days=-7)
        date_from = week_before.strftime('%Y-%m-%d')
        month_after = datetime.now() + relativedelta(days=31)
        date_to = month_after.strftime('%Y-%m-%d')

        for ocm in ocms:
            '''iterate through all centers'''
            center = ocm.id

            request_url = self._url + '{}?date_from={}&date_to={}'.format(center, date_from, date_to)
            r = requests.get(request_url, headers={'api_token': '{}'.format(token)}, verify=False)

            if r.status_code == 404:
                # Place not found
                continue

            df = DataFrame(r.json())

            '''Iterate through the result'''
            '''Create rows'''

            for idx, row in df.iterrows():
                ''' #sample
                {
                    "date": "2021-10-01",
                    "available_slots": 32,
                    "reservations_count": 0,
                    "vaccine_id": 1,
                    "vaccine_round": "v1"
                }
                '''
                db.session.add(OckovaniRezervace(
                    datum=row['date'],
                    ockovaci_misto_id=center,
                    volna_kapacita=row['available_slots'] - row['reservations_count'],
                    maximalni_kapacita=row['available_slots'],
                    kalendar_ockovani=row['vaccine_round'].upper(),
                    import_id=import_id
                ))
        db.session.commit()
