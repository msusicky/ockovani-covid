from datetime import timedelta, date

from sqlalchemy import func, case, text, or_, and_

from app import db, app, queries
from app.models import OckovaciMisto, OckovaciMistoMetriky, OckovaniRegistrace, OckovaniRezervace, Import, OckovaniLide, \
    OckovaniDistribuce


class Etl:
    def __init__(self, date_):
        self._date = date_

    def compute_all(self):
        vaccination_centers_result = self.compute_vaccination_centers()
        districts_result = self.compute_districts()
        regions_result = self.compute_regions()

        return vaccination_centers_result and districts_result and regions_result

    def compute_vaccination_centers(self):
        try:
            self._compute_vaccination_centers_registrations()
            self._compute_vaccination_centers_reservations()

            self._compute_vaccination_centers_vaccinated()
            self._compute_vaccination_centers_distributed()
            self._compute_vaccination_centers_deltas()

        except Exception as e:
            app.logger.error(e)
            db.session.rollback()
            return False

        db.session.commit()
        return True

    def _compute_vaccination_centers_registrations(self):
        registrations = db.session.query(
            OckovaciMisto.id, func.sum(OckovaniRegistrace.pocet).label('registrace_celkem'),
            func.sum(case([(OckovaniRegistrace.rezervace == False, OckovaniRegistrace.pocet)], else_=0)).label("registrace_fronta")
        ).join(OckovaniRegistrace, (OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id))\
            .filter(OckovaniRegistrace.import_id == self._find_import_id()) \
            .group_by(OckovaciMisto.id) \
            .all()

        for registration in registrations:
            db.session.merge(OckovaciMistoMetriky(
                id=registration.id,
                datum=self._date,
                registrace_celkem=registration.registrace_celkem,
                registrace_fronta=registration.registrace_fronta
            ))

        # db.session.merge(OckovaciMistoMetriky(
        #     registrace_tydenni_uspesnost=None,
        #     registrace_prumerne_cekani=None,
        # ))

        app.logger.info('Computing vaccination centers metrics - registrations finished.')

    def _compute_vaccination_centers_reservations(self):
        reservations = db.session.query(
            OckovaciMisto.id,
            func.sum(OckovaniRezervace.maximalni_kapacita - OckovaniRezervace.volna_kapacita).label('rezervace_celkem'),
            func.sum(case([(OckovaniRezervace.datum >= self._date, OckovaniRezervace.maximalni_kapacita - OckovaniRezervace.volna_kapacita)], else_=0)).label("rezervace_cekajici")
        ).join(OckovaniRezervace, (OckovaciMisto.id == OckovaniRezervace.ockovaci_misto_id)) \
            .filter(OckovaniRezervace.import_id == self._find_import_id()) \
            .group_by(OckovaciMisto.id) \
            .all()

        for reservation in reservations:
            db.session.merge(OckovaciMistoMetriky(
                id=reservation.id,
                datum=self._date,
                rezervace_celkem=reservation.rezervace_celkem,
                rezervace_cekajici=reservation.rezervace_cekajici
            ))

        app.logger.info('Computing vaccination centers metrics - reservations finished.')

    def _compute_vaccination_centers_vaccinated(self):
        vaccinated = db.session.query(OckovaciMisto.id, func.sum(OckovaniLide.pocet).label('ockovani_pocet')) \
            .join(OckovaniLide, (OckovaciMisto.nrpzs_kod == OckovaniLide.zarizeni_kod)) \
            .filter(OckovaniLide.datum < self._date) \
            .group_by(OckovaciMisto.id) \
            .all()

        for vacc in vaccinated:
            db.session.merge(OckovaciMistoMetriky(
                id=vacc.id,
                datum=self._date,
                ockovani_pocet=vacc.ockovani_pocet
            ))

        app.logger.info('Computing vaccination centers metrics - vaccinated people finished.')

    def _compute_vaccination_centers_distributed(self):
        distributed = db.session.query(
            OckovaciMisto.id,
            func.sum(case([(and_(OckovaciMisto.id == OckovaniDistribuce.ockovaci_misto_id, OckovaniDistribuce.akce == 'Výdej'), -OckovaniDistribuce.pocet_davek)], else_=OckovaniDistribuce.pocet_davek)).label('vakciny_prijate_pocet')
        ).join(OckovaniDistribuce,
               or_(
                   and_(OckovaciMisto.id == OckovaniDistribuce.ockovaci_misto_id, or_(OckovaniDistribuce.akce == 'Příjem', OckovaniDistribuce.akce == 'Výdej')),
                   and_(OckovaciMisto.id == OckovaniDistribuce.cilove_ockovaci_misto_id, OckovaniDistribuce.akce == 'Výdej')
               )) \
            .filter(OckovaniDistribuce.datum < self._date) \
            .group_by(OckovaciMisto.id) \
            .all()

        for dist in distributed:
            db.session.merge(OckovaciMistoMetriky(
                id=dist.id,
                datum=self._date,
                vakciny_prijate_pocet=dist.vakciny_prijate_pocet
            ))

        app.logger.info('Computing vaccination centers metrics - distributed vaccines finished.')

    def _compute_vaccination_centers_deltas(self):
        db.session.query().from_statement(text(
            """
            update ockovaci_mista_metriky t, (
                select rezervace_celkem, rezervace_cekajici, registrace_celkem, registrace_fronta, 
                    registrace_tydenni_uspesnost, registrace_prumerne_cekani, ockovani_pocet, vakciny_prijate_pocet
                from ockovaci_mista_metriky 
                where datum = :datum_1
            ) t1, (
                select ockovani_pocet, vakciny_prijate_pocet
                from ockovaci_mista_metriky 
                where datum = :datum_7
            ) t7
            set t.rezervace_celkem_zmena_den = t.rezervace_celkem - t1.rezervace_celkem,
                t.rezervace_cekajici_zmena_den = t.rezervace_cekajici - t1.rezervace_cekajici,
                t.registrace_celkem_zmena_den = t.registrace_celkem - t1.registrace_celkem,
                t.registrace_fronta_zmena_den = t.registrace_fronta - t1.registrace_fronta,
                t.registrace_tydenni_uspesnost_zmena_den = t.registrace_tydenni_uspesnost - t1.registrace_tydenni_uspesnost,
                t.registrace_prumerne_cekani_zmena_den = t.registrace_prumerne_cekani - t1.registrace_prumerne_cekani,
                t.ockovani_pocet_zmena_den = t.ockovani_pocet - t1.ockovani_pocet,
                t.ockovani_pocet_zmena_tyden = t.ockovani_pocet - t7.ockovani_pocet,
                t.vakciny_prijate_pocet_zmena_den = t.vakciny_prijate_pocet - t1.vakciny_prijate_pocet,
                t.vakciny_prijate_pocet_zmena_tyden = t.vakciny_prijate_pocet - t7.vakciny_prijate_pocet,
            """
        )).params(datum_1=self._date-timedelta(1), datum_7=self._date-timedelta(7))

        app.logger.info('Computing vaccination centers metrics - deltas finished.')

    def compute_districts(self):
        return True

    def compute_regions(self):
        return True

    def _find_import_id(self):
        id = db.session.query(Import.id) \
            .filter(Import.date == self._date, Import.status == queries.STATUS_FINISHED) \
            .first()[0]
        return -1 if id is None else id


if __name__ == '__main__':
    etl = Etl(date.today())
    etl.compute_all()