import json
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import db, Kapacita, OckovaciMisto, Dny, ImportLog
from datetime import date
import requests


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
                    "SELECT * FROM ockovaci_misto WHERE misto_id=:misto_param"
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
                           datum_ziskani=date.today().strftime('%Y-%m-%d'), import_id=self.import_id_last + 1)
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
                "SELECT den_id, datum FROM dny"
            )
        ).all()
        # print(dny_all)
        places_all = self.session.query(OckovaciMisto).from_statement(
            text(
                "SELECT misto_id, service_id, operation_id FROM ockovaci_misto"
            )
        ).all()
        # print(places_all)

        self.init_last_import_id()

        for i in dny_all:
            for j in places_all:
                self.fetch_misto(j.misto_id, i.datum, j.service_id, j.operation_id)
                time.sleep(1)
        # TODO It is necessary to write this run to the run_log, probably the fact that it is running as well
        new_row = ImportLog(import_id=self.import_id_last + 1, spusteni=date.now())
        print(self.session.add(new_row))
        self.session.commit()

    def init_last_import_id(self):
        try:
            self.import_id_last = self.session.query(ImportLog).from_statement(text(
                "SELECT max(spusteni) FROM import_log")).first()
        except:
            self.import_id_last = '-1'


if __name__ == '__main__':
    fetcher = FreespaceFetcher()
    fetcher.fetch_all()
