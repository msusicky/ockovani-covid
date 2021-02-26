import configparser
import time
from datetime import datetime, timedelta

import requests

from app import db, app
from app.models import OckovaciMisto, Import, VolnaMistaDen, VolnaMistaCas


class ReservaticFetcher:
    """
    It is responsible for fetching data from the Reservatic platform.
    """
    RESERVATIC_API = 'https://reservatic.com/public_services/{}/public_operations/{}/hours?date={}'
    DAYS = 10

    _session = None
    _centers = []
    _import = None

    def __init__(self):
        self._session = requests.session()
        config = configparser.RawConfigParser()
        config.read('session.ini')
        for key in config['DEFAULT']:
            self._session.cookies.set(key, config['DEFAULT'][key])

        self._init_centers()

    def fetch_free_capacities(self):
        self._import = Import(status='RUNNING')
        db.session.add(self._import)
        db.session.commit()

        start_day = datetime.today().date()
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
            self._import.status = 'FAILED'
        else:
            app.logger.info('Fetch successful')
            self._import.status = 'FINISHED'
        finally:
            db.session.commit()

    def _init_centers(self):
        self._centers = db.session.query(OckovaciMisto)\
            .filter(OckovaciMisto.service_id != None, OckovaciMisto.operation_id != None, OckovaciMisto.status == True)\
            .all()

    def _fetch_free_capacities_day(self, day):
        for center in self._centers:
            self._fetch_free_capacities_day_center(day, center)
            time.sleep(1)

    def _fetch_free_capacities_day_center(self, day, center):
        response = self._call_api(day, center)

        if response is None:
            return

        response_json = response.json()

        free_total = 0

        for item in response_json:
            free = item['free_people']
            free_total += free

            volna_mista_cas = VolnaMistaCas(
                import_id = self._import.id,
                misto_id = center.id,
                datum = day,
                cas = item['label'],
                start = datetime.fromisoformat(item['starts_at']),
                volna_mista = free,
                place_id = item['place_id'],
                user_service_id = item['user_service_id']
            )
            db.session.add(volna_mista_cas)

        volna_mista_den = VolnaMistaDen(
            import_id = self._import.id,
            misto_id = center.id,
            datum = day,
            volna_mista = free_total,
            data = response.text
        )
        db.session.add(volna_mista_den)
        app.logger.info(volna_mista_den)

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
    fetcher = ReservaticFetcher()
    fetcher.fetch_free_capacities()
