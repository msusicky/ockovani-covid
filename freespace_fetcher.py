import json
import sys
import time
from datetime import datetime, date

import requests
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

from models import Kapacita, OckovaciMisto, Dny, ImportLog


class FreespaceFetcher:
    """
    It is responsible for fetching data from the Reservatic plaftform.
    API point: https://reservatic.com/public_services/411747/public_operations/5971/hours?date=2021-4-09
    """
    session = ''
    import_id_last = -1

    def __init__(self):
        some_engine = create_engine('postgresql://ockovani:ockovani2021@localhost:5432/ockovani')
        Session = sessionmaker(bind=some_engine)
        self.session = Session()
        self.init_last_import_id()

    def fetch(self, service_id, operation_id, vacc_date):
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
        response_api = requests.get(url, data=data, headers={"Content-Type": "application/json"})

        return response_api

    def fetch_misto(self, misto_id, vacc_date, service_id=None, operation_id=None):
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
            api_response = self.fetch(service_id, operation_id, vacc_date)
            if api_response.status_code == 200:
                item_dict = json.loads(api_response.text)
                pocet = len(item_dict)
                raw_data_response = api_response.text
            else:
                pocet = None
                raw_data_response = None
        except:
            print('Connection Error')
            pocet = None
            raw_data_response = None

        new_row = Kapacita(misto_id=misto_id, datum=vacc_date, raw_data=raw_data_response, pocet_mist=pocet,
                           datum_ziskani=datetime.now(), import_id=int(self.import_id_last) + 1)
        # TODO import_id should be filled correctly
        print(self.session.add(new_row))
        self.session.commit()

    def fetch_all(self):
        """
        It will run fetch for all vacc. places for all dates from dny table.
        Get all dates from dny
        Get all places from OckovaciMista
        Run fetchMisto in loop
        @param vacc_date:
        @return:
        """
        dny_all = self.session.query(Dny).from_statement(
            text(
                "SELECT den_id, datum FROM dny ",
                "WHERE datum BETWEEN NOW()::date AND (NOW() + INTERVAL '29 days')::date"
            )
        ).all()
        # print(dny_all)
        places_all = self.session.query(OckovaciMisto).from_statement(
            text(
                "SELECT misto_id, service_id, operation_id FROM ockovaci_misto"
            )
        ).all()
        # print(places_all)

        # Writing this attempt
        new_row = ImportLog(import_id=int(self.import_id_last) + 1, spusteni=datetime.now(), status='RUNNING')
        print(self.session.add(new_row))
        self.session.commit()

        try:
            for day in dny_all:
                for place in places_all:
                    self.fetch_misto(place.misto_id, day.datum, place.service_id, place.operation_id)
                    time.sleep(1)
            # TODO It is necessary to finish this run -> nehance DB
        except:
            new_row.status = 'FAILED'
        else:
            new_row.status = 'FINISHED'
        finally:
            self.session.commit()

    def init_last_import_id(self):
        res = self.session.query(func.max(ImportLog.import_id)).first()[0]
        if res is None:
            self.import_id_last = '-1'
        else:
            self.import_id_last = res

    def fetch_covtest(self):
        """
        Fetching free spaces from the covtest.cz website.
        @return:
        """
        for region_id in range(15, 28):
            url = 'https://www.covtest.cz/Index?handler=Calendar&regionId={}&type=16'.format(region_id)
            # print(url)
            freespaces_response_api = requests.get(url, data='', headers={"Content-Type": "application/json"})
            if freespaces_response_api.status_code == 200:
                free_places = json.loads(freespaces_response_api.text)
                if len(free_places) > 0:
                    # iterate through freespaces
                    self.scrape_region(free_places, freespaces_response_api, region_id)

        return 0

    def scrape_region(self, free_places, freespaces_response_api, region_id):
        """
        Investigate all places in the region.
        @param free_places:
        @param freespaces_response_api:
        @param region_id:
        @return:
        """
        for place in free_places:

            url_place = 'https://covtest.cz/Index?handler=Place&regionId={}&date={}&type=16'.format(
                region_id,
                place[
                    'date'])
            # print(url_place)
            capacities = requests.get(url_place, data='', headers={"Content-Type": "application/json"})
            if capacities.status_code == 200:
                places_list = json.loads(capacities.text)
                for free_space in places_list:
                    print(free_space)
                    # Sample {'id': '995902bc-6243-419d-962e-fbe99d97bb2d', 'day': '2021-01-21T00:00:00', 'name': 'Očkování', 'companyName': 'Nemocnice TGM Hodonín', 'capacity': 7}


if __name__ == '__main__':
    fetcher = FreespaceFetcher()
    arguments = sys.argv[1:]
    if arguments[0] == "covtest":
        fetcher.fetch_covtest()
    else:
        fetcher.fetch_all()
