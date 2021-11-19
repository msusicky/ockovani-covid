import os
from datetime import datetime
from typing import Optional

import requests
import urllib3
from dateutil.relativedelta import relativedelta
from pandas import DataFrame
from sqlalchemy import func, text

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto, OckovaniRezervace, Import


class ReservationsApiFetcher(Fetcher):
    """
    Class for updating reservations table.
    """

    API_URL = 'https://api.reservatic.com/api/nakit/v2/'
    # API_URL = 'https://dev.reservatic.com/api/nakit/v2/'
    VACCINE_SERVICES = 'vaccine_services/stats/'

    def __init__(self):
        super().__init__(OckovaniRezervace.__tablename__, self.API_URL + self.VACCINE_SERVICES, historized=True)
        urllib3.disable_warnings()

    def get_modified_time(self) -> Optional[datetime]:
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
        not_found = 0
        empty = 0

        last_import_id = db.session.query(func.max(Import.id)).filter(Import.status == 'FINISHED').one()

        # Create all rows first
        db.session.execute(text(
            """INSERT INTO public.ockovani_rezervace
                (datum, ockovaci_misto_id, volna_kapacita, maximalni_kapacita, kalendar_ockovani, import_id)
                SELECT datum, ockovaci_misto_id, volna_kapacita, maximalni_kapacita, kalendar_ockovani 
                FROM ockovani_rezervace"""
        ), {'import_id': import_id, 'last_import_id': last_import_id})

        for ocm in ocms:
            '''iterate through all centers'''
            center = ocm.id

            request_url = self._url + '{}?date_from={}&date_to={}'.format(center, date_from, date_to)
            r = requests.get(request_url, headers={'Api-Token': '{}'.format(token)}, verify=False)

            if r.status_code == 404:
                # Place not found
                not_found += 1
                continue

            response_data = r.json()

            if len(response_data) == 0:
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
                    ockovaci_misto_id=center,
                    volna_kapacita=row['available_slots'],
                    maximalni_kapacita=row['available_slots'] + row['reservations_count'],
                    kalendar_ockovani=row['vaccine_round'].upper(),
                    import_id=import_id
                ))

        app.logger.warning("Not able to find {} centers and {} responses were empty.".format(not_found, empty))
        db.session.commit()
