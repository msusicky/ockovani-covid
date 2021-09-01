import os
from datetime import date

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

    API_URL = 'https://dev.reservatic.com/api/nakit/v2/'
    VACCINE_SERVICES = 'vaccine_services/stats/'

    def __init__(self):
        super().__init__(OckovaniRezervace.__tablename__, self.API_URL + self.VACCINE_SERVICES, check_date=False)

    def fetch(self, import_id: int) -> None:
        token = os.environ.get('ODL_RESERVATIC_API')

        ocms = db.session.query(OckovaciMisto) \
            .order_by(OckovaciMisto.id) \
            .all()

        # create the right date interval
        week_before = date.now() + relativedelta(days=-7)
        date_from = week_before.strftime('%Y-%m-%d')
        month_after = date.now() + relativedelta(days=31)
        date_to = month_after.strftime('%Y-%m-%d')

        for ocm in ocms:
            '''iterate through all centers'''
            # center='4c050cd4-6edf-4b4b-8034-8b731978b216'
            center = ocm.id

            self._url = self._url + '{}?date_from={}&date_to={}'.format(center, week_before, month_after)
            r = requests.get(self._url, headers={'Authorization': 'api_token ' + token}, verify=False)
            df = DataFrame(r.json()['results'])

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
                    datum=date,
                    ockovaci_misto_id=center,
                    volna_kapacita=available_slots - reservations_count,
                    maximalni_kapacita=available_slots,
                    kalendar_ockovani=upper(vaccine_round),
                    import_id= ?
                ))
        db.session.commit()
