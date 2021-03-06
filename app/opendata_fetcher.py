import sys

import requests
import pandas as pd

from app import db, app
from app.models import Import, OckovaciMisto, OckovaniSpotreba, OckovaniDistribuce, OckovaniLide, OckovaniRezervace, \
    OckovaniRegistrace


class OpenDataFetcher:
    CENTERS_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/prehled-ockovacich-mist.json'
    USED_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-spotreba.json'
    DISTRIBUTED_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-distribuce.json'
    VACCINATED_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovaci-mista.csv'
    REGISTRATION_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-registrace.csv'
    RESERVATION_API = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-rezervace.csv'

    _import = None

    def fetch_all(self):
        self._import = Import(status='RUNNING')
        db.session.add(self._import)
        db.session.commit()

        try:
            self._fetch_centers()
            self._fetch_used()
            self._fetch_distributed()
            self._fetch_vaccinated()
            self._fetch_registrations()
            self._fetch_reservations()
        except Exception as e:
            app.logger.error('Fetch failed')
            app.logger.error(e)
            self._import.status = 'FAILED'
        else:
            app.logger.info('Fetch successful')
            self._import.status = 'FINISHED'
        finally:
            db.session.commit()

    def _fetch_centers(self):
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

        app.logger.info('Fetching vaccination centers finished.')

    def _fetch_used(self):
        """
        Fetch vacination data from opendata.
        https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-spotreba.csv
        @return:
        """
        response = requests.get(url=self.USED_API)
        data = response.json()['data']

        db.session.query(OckovaniSpotreba).delete()

        for record in data:
            datum = record['datum']
            ockovaci_misto_id = record['ockovaci_misto_id']
            ockovaci_misto_nazev = record['ockovaci_misto_nazev']
            kraj_nuts_kod = record['kraj_nuts_kod']
            kraj_nazev = record['kraj_nazev']
            ockovaci_latka = record['ockovaci_latka']
            vyrobce = record['vyrobce']
            pouzite_ampulky = record['pouzite_ampulky']
            znehodnocene_ampulky = record['znehodnocene_ampulky']
            pouzite_davky = record['pouzite_davky']
            znehodnocene_davky = record['znehodnocene_davky']

            spotreba = db.session.query(OckovaniSpotreba) \
                .filter(OckovaniSpotreba.datum == datum,
                        OckovaniSpotreba.ockovaci_misto_id == ockovaci_misto_id,
                        OckovaniSpotreba.ockovaci_latka == ockovaci_latka) \
                .one_or_none()

            if spotreba is None:
                db.session.add(OckovaniSpotreba(
                    datum=datum,
                    ockovaci_misto_id=ockovaci_misto_id,
                    ockovaci_misto_nazev=ockovaci_misto_nazev,
                    kraj_nuts_kod=kraj_nuts_kod,
                    kraj_nazev=kraj_nazev,
                    ockovaci_latka=ockovaci_latka,
                    vyrobce=vyrobce,
                    pouzite_ampulky=pouzite_ampulky,
                    znehodnocene_ampulky=znehodnocene_ampulky,
                    pouzite_davky=pouzite_davky,
                    znehodnocene_davky=znehodnocene_davky
                ))
            else:
                spotreba.pouzite_ampulky += pouzite_ampulky
                spotreba.znehodnocene_ampulky += znehodnocene_ampulky
                spotreba.pouzite_davky += pouzite_davky
                spotreba.znehodnocene_davky += znehodnocene_davky
                db.session.merge(spotreba)

        app.logger.info('Fetching used vaccines finished.')

    def _fetch_distributed(self):
        """
        Fetch distribution files from opendata.
        https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-distribuce.csv
        @return:
        """
        response = requests.get(url=self.DISTRIBUTED_API)
        data = response.json()['data']

        db.session.query(OckovaniDistribuce).delete()

        for record in data:
            datum = record['datum']
            ockovaci_misto_id = record['ockovaci_misto_id']
            ockovaci_misto_nazev = record['ockovaci_misto_nazev']
            kraj_nuts_kod = record['kraj_nuts_kod']
            kraj_nazev = record['kraj_nazev']
            cilove_ockovaci_misto_id = record['cilove_ockovaci_misto_id']
            cilove_ockovaci_misto_nazev = record['cilove_ockovaci_misto_nazev']
            cilovy_kraj_kod = record['cilovy_kraj_kod']
            cilovy_kraj_nazev = record['cilovy_kraj_nazev']
            ockovaci_latka = record['ockovaci_latka']
            vyrobce = record['vyrobce']
            akce = record['akce']
            pocet_ampulek = record['pocet_ampulek']
            pocet_davek = record['pocet_davek']

            distribuce = db.session.query(OckovaniDistribuce) \
                .filter(OckovaniDistribuce.datum == datum,
                        OckovaniDistribuce.ockovaci_misto_id == ockovaci_misto_id,
                        OckovaniDistribuce.cilove_ockovaci_misto_id == cilove_ockovaci_misto_id,
                        OckovaniDistribuce.ockovaci_latka == ockovaci_latka,
                        OckovaniDistribuce.akce == akce) \
                .one_or_none()

            if distribuce is None:
                db.session.add(OckovaniDistribuce(
                    datum=datum,
                    ockovaci_misto_id=ockovaci_misto_id,
                    ockovaci_misto_nazev=ockovaci_misto_nazev,
                    kraj_nuts_kod=kraj_nuts_kod,
                    kraj_nazev=kraj_nazev,
                    cilove_ockovaci_misto_id=cilove_ockovaci_misto_id,
                    cilove_ockovaci_misto_nazev=cilove_ockovaci_misto_nazev,
                    cilovy_kraj_kod=cilovy_kraj_kod,
                    cilovy_kraj_nazev=cilovy_kraj_nazev,
                    ockovaci_latka=ockovaci_latka,
                    vyrobce=vyrobce,
                    akce=akce,
                    pocet_ampulek=pocet_ampulek,
                    pocet_davek=pocet_davek
                ))
            else:
                distribuce.pocet_ampulek += pocet_ampulek
                distribuce.pocet_davek += pocet_davek
                db.session.merge(distribuce)

        app.logger.info('Fetching distributed vaccines finished.')

    def _fetch_vaccinated(self):
        """
        Fetch distribution files from opendata.
        https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovaci-mista.csv
        @return:
        """
        data = pd.read_csv(self.VACCINATED_API)

        d = data.groupby(["datum", "vakcina", "kraj_nuts_kod", "kraj_nazev", "zarizeni_kod", "zarizeni_nazev",
                          "poradi_davky", "vekova_skupina"]).size().reset_index(name='counts')

        db.session.query(OckovaniLide).delete()

        for row in d.itertuples(index=False):
            db.session.add(OckovaniLide(
                datum=row[0],
                vakcina=row[1],
                kraj_nuts_kod=row[2],
                kraj_nazev=row[3],
                zarizeni_kod=row[4],
                zarizeni_nazev=row[5],
                poradi_davky=row[6],
                vekova_skupina=row[7],
                pocet=row[8]
            ))

        app.logger.info('Fetching vaccinated people finished.')

    def _fetch_registrations(self):
        """
        Fetch registrations from opendata.
        https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-registrace.csv
        @return:
        """

        data = pd.read_csv(self.REGISTRATION_API)

        df = data.drop(["ockovaci_misto_nazev", "kraj_nuts_kod", "kraj_nazev"], axis=1)
        df['rezervace'] = df['rezervace'].fillna(False)
        df['datum_rezervace'] = df['datum_rezervace'].fillna('1970-01-01')
        df = df.groupby(
            ["datum", "ockovaci_misto_id", "vekova_skupina", "povolani", "stat", "rezervace", "datum_rezervace"]) \
            .size() \
            .reset_index(name='counts')

        mista_result = db.session.query(OckovaciMisto.id).all()
        mista_ids = [id for id, in mista_result]

        for row in df.itertuples(index=False):
            misto_id = row[1]

            if misto_id not in mista_ids:
                app.logger.warn("Center: '%s' doesn't exist" % (misto_id))
                continue

            db.session.add(OckovaniRegistrace(
                datum=row[0],
                ockovaci_misto_id=misto_id,
                vekova_skupina=row[2],
                povolani=row[3],
                stat=row[4],
                rezervace=row[5],
                datum_rezervace=row[6],
                pocet=row[7],
                import_=self._import
            ))

        app.logger.info('Fetching registrations finished.')

    def _fetch_reservations(self):
        """
        Fetch reservations from opendata.
        https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-rezervace.csv
        @return:
        """
        data = pd.read_csv(self.RESERVATION_API)

        df = data.drop(["ockovaci_misto_nazev", "kraj_nuts_kod", "kraj_nazev"], axis=1)

        mista_result = db.session.query(OckovaciMisto.id).all()
        mista_ids = [id for id, in mista_result]

        for row in df.itertuples(index=False):
            misto_id = row[1]

            if misto_id not in mista_ids:
                app.logger.warn("Center: '%s' doesn't exist" % (misto_id))
                continue

            db.session.add(OckovaniRezervace(
                datum=row[0],
                ockovaci_misto_id=misto_id,
                volna_kapacita=row[2],
                maximalni_kapacita=row[3],
                kalendar_ockovani=row[4],
                import_=self._import
            ))

        app.logger.info('Fetching reservations finished.')


if __name__ == '__main__':
    arguments = sys.argv[1:]
    if len(arguments) != 1:
        print('Invalid option.')
        exit(1)

    argument = arguments[0]

    fetcher = OpenDataFetcher()

    if argument == 'centers':
        fetcher._fetch_centers()
    elif argument == 'used':
        fetcher._fetch_used()
    elif argument == 'distributed':
        fetcher._fetch_distributed()
    elif argument == 'vaccinated':
        fetcher._fetch_vaccinated()
    elif argument == 'registrations_reservations':
        fetcher._import = Import(status='RUNNING')
        db.session.add(fetcher._import)
        db.session.commit()
        fetcher._fetch_registrations()
        fetcher._fetch_reservations()
        fetcher._import.status = 'FINISHED'

    else:
        print('Invalid option.')
        exit(1)

    db.session.commit()
