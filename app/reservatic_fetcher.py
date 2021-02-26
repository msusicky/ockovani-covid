import json
import sys
import time
from datetime import datetime, date, timedelta

import requests
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

from app import db
from app.models import Kapacita, OckovaciMisto, Dny, ImportLog

import configparser


class FreespaceFetcher:
    """
    It is responsible for fetching data from the Reservatic plaftform.
    """
    RESERVATIC_API = 'https://reservatic.com/public_services/{}/public_operations/{}/hours?date={}'
    DAYS = 10

    session = None
    current_import_id = 0


    def __init__(self):
        self.session = requests.session()
        config = configparser.RawConfigParser()
        config.read('session.ini')
        for key in config['DEFAULT']:
            self.session.cookies.set(key, config['DEFAULT'][key])

        self._init_current_import_id()

    def fetch_free_capacity(self):
        centers = self._find_centers()
        days

    def _init_current_import_id(self):
        prev_import_id = db.query(func.max(ImportLog.import_id)).first()[0]
        self.current_import_id = 0 if prev_import_id is None else int(prev_import_id) + 1

    def _find_centers(self):
        return db.session.query(OckovaciMisto)\
            .filter(OckovaciMisto.service_id is not None, OckovaciMisto.okres is not None)\
            .all()



    def fetch_reservatic_misto_call(self, service_id, operation_id, vacc_date):
        """

        @param service_id:
        @param operation_id:
        @param vacc_date: Date that we'd like to fetch
        @return:
        """
        url = 'https://reservatic.com/public_services/{}/public_operations/{}/hours?date={}'.format(service_id,
                                                                                                    operation_id,
                                                                                                    vacc_date)
        data = ''
        print(url)
        response_api = self.http_session.get(url, data=data, headers={"Content-Type": "application/json"})

        return response_api




    def fetch_reservatic_misto(self, misto_id, vacc_date, service_id=None, operation_id=None):
        """
        It fetches necessary info from misto_id -> table ockovaci_misto and executes fetch for it.
        Result will be stored in DB
        @param misto_id: Misto that we'd like to fetch
        @return:
        """

        if service_id is None:
            misto_parameters = self.session.query(OckovaciMisto).from_statement(
                text(
                    "SELECT om.misto_id, om.nazev, om.service_id, om.operation_id, om.place_id, om.mesto FROM ockovaci_misto om WHERE misto_id=:misto_param"
                )
            ).params(misto_param=misto_id).all()
            service_id = misto_parameters[0].service_id
            operation_id = misto_parameters[0].operation_id

        try:
            api_response = self.fetch_reservatic_misto_call(service_id, operation_id, vacc_date)
            if api_response.status_code == 200:
                item_dict = json.loads(api_response.text)
                pocet = 0
                for item in item_dict:
                    pocet += item['free_people']
                raw_data_response = api_response.text
            else:
                pocet = None
                raw_data_response = None
        except:
            print('Connection Error')
            pocet = None
            raw_data_response = None

        new_row = Kapacita(misto_id=misto_id, datum=vacc_date, raw_data=raw_data_response, pocet_mist=pocet,
                           datum_ziskani=datetime.now(), import_id=self.current_import_id)
        print('Pocet mist: ' + str(new_row.pocet_mist))
        self.session.add(new_row)
        self.session.commit()

    def fetch_reservatic(self):
        """
        It will run fetch for all vacc. places for all dates from dny table.
        Get all dates from dny
        Get all places from OckovaciMista
        Run fetchMisto in loop
        @param vacc_date:
        @return:
        """
        dny_all = self.get_days()
        # print(dny_all)
        places_all = self.get_places()
        # print(places_all)

        # Writing this attempt
        new_row = ImportLog(import_id=self.current_import_id, spusteni=datetime.now(), status='RUNNING')
        print(new_row)
        self.session.add(new_row)
        self.session.commit()

        try:
            for day in dny_all:
                for place in places_all:
                    self.fetch_reservatic_misto(place.misto_id, day.datum, place.service_id, place.operation_id)
                    time.sleep(1)
            # TODO It is necessary to finish this run -> nehance DB
        except Exception as e:
            print(e)
            new_row.status = 'FAILED'
        else:
            new_row.status = 'FINISHED'
        finally:
            self.session.commit()


if __name__ == '__main__':
    fetcher = FreespaceFetcher()
    fetcher.fetch_free_capacity()
