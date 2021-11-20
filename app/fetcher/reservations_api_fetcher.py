import os
from datetime import datetime
from typing import Optional

import requests
import urllib3
from dateutil.relativedelta import relativedelta
from pandas import DataFrame
from sqlalchemy import or_

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto, OckovaniRezervace


class ReservationsApiFetcher(Fetcher):
    """
    Class for updating reservations table.
    """

    API_URL = 'https://api.reservatic.com/api/nakit/v2/'
    # API_URL = 'https://dev.reservatic.com/api/nakit/v2/'
    VACCINE_SERVICES = 'vaccine_services/stats/'

    def __init__(self, full_update: bool = True):
        super().__init__(OckovaniRezervace.__tablename__, self.API_URL + self.VACCINE_SERVICES)
        self._full_update = full_update
        self._token = os.environ.get('ODL_RESERVATIC_API')
        if self._token is None:
            raise ValueError("ODL_RESERVATIC_API variable is empty")
        urllib3.disable_warnings()

    def get_modified_time(self) -> Optional[datetime]:
        return datetime.today()

    def fetch(self, import_id: int) -> None:
        ocms = db.session.query(OckovaciMisto.id) \
            .filter(or_(OckovaciMisto.status == True, self._full_update)) \
            .order_by(OckovaciMisto.id) \
            .all()

        ocm_ids = [ocm[0] for ocm in ocms]

        date_from = self._count_date_from()
        date_to = self._count_date_to()

        not_found = 0
        empty = 0

        for ocm_id in ocm_ids:
            '''iterate through all centers'''
            request_url = self._url + f'{ocm_id}?date_from={date_from}&date_to={date_to}'
            response = requests.get(request_url, headers={'Api-Token': '{}'.format(self._token)}, verify=False)

            if response.status_code == 404:
                # center not found
                not_found += 1
                continue

            response_data = response.json()

            if len(response_data) == 0:
                # no calendar
                empty += 1
                continue

            df = DataFrame(response_data)

            # There are multiple calendars - per each vaccine type one -> grouping
            df = df.groupby(['date', 'vaccine_round'], dropna=True) \
                .sum() \
                .reset_index()

            for idx, row in df.iterrows():
                # TODO: vaccine_id is not saved nowadays, then grouping should be removed

                db.session.merge(OckovaniRezervace(
                    datum=row['date'],
                    ockovaci_misto_id=ocm_id,
                    volna_kapacita=row['available_slots'],
                    maximalni_kapacita=row['available_slots'] + row['reservations_count'],
                    kalendar_ockovani=row['vaccine_round'].upper()
                ))

        app.logger.warning("Not able to find {} centers and {} responses were empty.".format(not_found, empty))
        db.session.commit()

    def _count_date_from(self) -> str:
        days = -7 if self._full_update else 0
        return (datetime.now() + relativedelta(days=days)).strftime('%Y-%m-%d')

    def _count_date_to(self) -> str:
        days = 31
        return (datetime.now() + relativedelta(days=days)).strftime('%Y-%m-%d')
