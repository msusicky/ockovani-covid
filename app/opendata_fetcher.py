import sys

import requests

from app import db
from app.models import OckovaciMisto


class OpendataFetcher:
    CENTERS_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/prehled-ockovacich-mist.json'
    USED_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-spotreba.json'
    DISTRIBUTED_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-distribuce.json'

    def fetch_all(self):
        self.fetch_centers()
        self.fetch_used()
        self.fetch_distributed()

    def fetch_centers(self):
        response = requests.get(url=self.CENTERS_API)
        data = response.json()['data']

        for record in data:
            db.session.merge(OckovaciMisto(
                id=record['ockovaci_misto_id'],
                nazev=record['ockovaci_misto_nazev'],
                okres_id=record['okres_nuts_kod'],
                status=record['operacni_status'],
                adresa=record['ockovaci_misto_adresa'],
                latitude=record['latitude'],
                longitude=record['longitude'],
                minimalni_kapacita=record['minimalni_kapacita'],
                bezbarierovy_pristup=record['bezbarierovy_pristup']
            ))

        db.session.commit()

    def fetch_used(self):
        pass # todo

    def fetch_distributed(self):
        pass # todo


if __name__ == '__main__':
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print('Invalid option.')
        exit(1)

    argument = arguments[0]

    fetcher = OpendataFetcher()

    if argument == 'centers':
        fetcher.fetch_centers()
    elif argument == 'used':
        fetcher.fetch_used()
    elif argument == 'distributed':
        fetcher.fetch_distributed()
    else:
        print('Invalid option.')
        exit(1)