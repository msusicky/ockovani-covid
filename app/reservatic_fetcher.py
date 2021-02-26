import configparser
import time
from datetime import datetime, timedelta

import requests
from sqlalchemy import func

from app import db, app
from app.models import OckovaciMisto, Import, VolnaMistaDen, VolnaMistaCas


class FreespaceFetcher:
    """
    It is responsible for fetching data from the Reservatic plaftform.
    """
    RESERVATIC_API = 'https://reservatic.com/public_services/{}/public_operations/{}/hours?date={}'
    DAYS = 10

    _session = None
    _current_import_id = 0
    _centers = []

    def __init__(self):
        self._session = requests.session()
        config = configparser.RawConfigParser()
        config.read('session.ini')
        for key in config['DEFAULT']:
            self._session.cookies.set(key, config['DEFAULT'][key])

        self._init_current_import_id()
        self._init_centers()

    def fetch_free_capacities(self):
        new_import = Import(id=self._current_import_id, status='RUNNING')
        db.session.add(new_import)
        db.session.commit()

        start_day = datetime.today()
        end_day = start_day + timedelta(self.DAYS)
        delta = timedelta(1)
        day = start_day

        try:
            while day < end_day:
                self._fetch_free_capacities_day(day)
                day += delta
        except Exception as e:
            app.logger.error('Fetch failed')
            app.logger.error(e)
            new_import.status = 'FAILED'
        else:
            app.logger.info('Fetch successful')
            new_import.status = 'FINISHED'
        finally:
            db.session.commit()

    def _init_current_import_id(self):
        prev_import_id = db.session.query(func.max(Import.id)).first()[0]
        self._current_import_id = 0 if prev_import_id is None else int(prev_import_id) + 1

    def _init_centers(self):
        self._centers = db.session.query(OckovaciMisto)\
            .filter(OckovaciMisto.service_id is not None, OckovaciMisto.operation_id is not None)\
            .all()

    def _fetch_free_capacities_day(self, day):
        for center in self._centers:
            self._fetch_free_capacities_day_center(day, center)
            time.sleep(1)

    def _fetch_free_capacities_day_center(self, day, center):
        response = self._call_api(day, center)

        if response is None:
            return

        db.session.add(VolnaMistaDen(
            import_id = self._current_import_id,
            misto_id = center.id,
            datum = day,
            data = response.text
        ))

        response_json = response.json()

        for item in response_json:
            volna_mista = VolnaMistaCas(
                import_id = self._current_import_id,
                misto_id = center.id,
                datum = day,
                cas = item['label'],
                start = item['start_at'],
                volna_mista = item['free_people'],
                place_id = item['place_id'],
                user_service_id = item['user_service_id']
            )
            db.session.add(volna_mista)
            app.logger.info(volna_mista)

    def _call_api(self, day, center):
        try:
            url = self.RESERVATIC_API.format(center.service_id, center.operation_id, day)
            app.logger.info(url)
            response = self._session.get(url)
            status = response.status_code
            if status == 200:
                return response
            else:
                app.logger.warning('Response error code: {}' % status)
        except:
            app.logger.warning('Connection error')

        return None


if __name__ == '__main__':
    fetcher = FreespaceFetcher()
    fetcher.fetch_free_capacities()
