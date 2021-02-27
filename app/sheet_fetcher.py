import configparser

import gspread as gspread

from app import db
from app.models import OckovaciMisto


class SheetFetcher:
    SHEET_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/prehled-ockovacich-mist.json'

    _table_key = None
    _gc = None

    def __init__(self):
        config = configparser.RawConfigParser()
        config.read('config.ini')
        self._table_key = config['google_table']['key']

        self._gc = gspread.service_account(filename='google_key.json')

    def fetch_centers(self):
        wks = self._gc.open_by_key(self._table_key).sheet1
        data = wks.get_all_records()

        for record in data:
            service_id = record['service_id']
            operation_id = record['operation_id']
            odkaz = record['odkaz']

            if service_id != '' and operation_id != '':
                db.session.merge(OckovaciMisto(
                    id = record['id'],
                    service_id = service_id,
                    operation_id = operation_id,
                    odkaz = odkaz if odkaz != '' else None
                ))

        db.session.commit()


if __name__ == '__main__':
    fetcher = SheetFetcher()
    fetcher.fetch_centers()