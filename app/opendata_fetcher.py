import sys

import requests

from app import db, app
from app.models import OckovaciMisto, OckovaniSpotreba, OckovaniDistribuce


class OpenDataFetcher:
    CENTERS_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/prehled-ockovacich-mist.json'
    USED_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-spotreba.json'
    DISTRIBUTED_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-distribuce.json'

    def fetch_all(self):
        self.fetch_centers()
        self.fetch_used()
        self.fetch_distributed()

    def fetch_centers(self):
        """
        It will fetch vaccination centers
        @return:
        """
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
                nrpzs_kod=format(record['nrpzs_kod'], '011d'),
                minimalni_kapacita=record['minimalni_kapacita'],
                bezbarierovy_pristup=record['bezbarierovy_pristup']
            ))

        db.session.commit()

        app.logger.info('Fetching vaccination centers finished.')

    def fetch_used(self):
        """
        Fetch vacination data from opendata.
        https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-spotreba.csv
        @return:
        """
        response = requests.get(url=self.USED_API)
        data = response.json()['data']

        for record in data:
            db.session.merge(OckovaniSpotreba(
                datum=record['datum'],
                ockovaci_misto_id=record['ockovaci_misto_id'],
                ockovaci_misto_nazev=record['ockovaci_misto_nazev'],
                kraj_nuts_kod=record['kraj_nuts_kod'],
                kraj_nazev=record['kraj_nazev'],
                ockovaci_latka=record['ockovaci_latka'],
                vyrobce=record['vyrobce'],
                pouzite_ampulky=record['pouzite_ampulky'],
                znehodnocene_ampulky=record['znehodnocene_ampulky'],
            ))

        db.session.commit()

        app.logger.info('Fetching used vaccines finished.')

    def fetch_distributed(self):
        """
        Fetch distribution files from opendata.
        https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-distribuce.csv
        @return:
        """
        response = requests.get(url=self.DISTRIBUTED_API)
        data = response.json()['data']

        for record in data:
            db.session.merge(OckovaniDistribuce(
                datum=record['datum'],
                ockovaci_misto_id=record['ockovaci_misto_id'],
                ockovaci_misto_nazev=record['ockovaci_misto_nazev'],
                kraj_nuts_kod=record['kraj_nuts_kod'],
                kraj_nazev=record['kraj_nazev'],
                cilove_ockovaci_misto_id=record['cilove_ockovaci_misto_id'],
                cilove_ockovaci_misto_nazev=record['cilove_ockovaci_misto_nazev'],
                cilovy_kraj_kod=record['cilovy_kraj_kod'],
                cilovy_kraj_nazev=record['cilovy_kraj_nazev'],
                ockovaci_latka=record['ockovaci_latka'],
                vyrobce=record['vyrobce'],
                akce=record['akce'],
                pocet_ampulek=record['pocet_ampulek'],
            ))

        db.session.commit()

        app.logger.info('Fetching distributed vaccines finished.')


if __name__ == '__main__':
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print('Invalid option.')
        exit(1)

    argument = arguments[0]

    fetcher = OpenDataFetcher()

    if argument == 'centers':
        fetcher.fetch_centers()
    elif argument == 'used':
        fetcher.fetch_used()
    elif argument == 'distributed':
        fetcher.fetch_distributed()
    else:
        print('Invalid option.')
        exit(1)
