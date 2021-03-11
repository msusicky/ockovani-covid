from datetime import date, timedelta

from sqlalchemy import func, case, text

from app import db, app
from app.models import OckovaciMisto, OckovaciMistoMetriky, OckovaniRegistrace


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
            .filter(OckovaniRegistrace.datum < self._date) \
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
        #     id=id,
        #     datum=self._today,
        #     rezervace_celkem=None,
        #     rezervace_celkem_zmena_den=None,
        #     rezervace_cekajici=None,
        #     rezervace_cekajici_zmena_den=None,
        #     registrace_celkem=None,
        #     registrace_celkem_zmena_den=None,
        #     registrace_fronta=None,
        #     registrace_fronta_zmena_den=None,
        #     registrace_tydenni_uspesnost=None,
        #     registrace_tydenni_uspesnost_zmena_den=None,
        #     registrace_prumerne_cekani=None,
        #     registrace_prumerne_cekani_zmena_den=None,
        #     ockovani_pocet=None,
        #     ockovani_pocet_zmena_den=None,
        #     ockovani_pocet_zmena_tyden=None,
        #     vakciny_prijate_pocet=None,
        #     vakciny_prijate_pocet_zmena_den=None,
        #     vakciny_prijate_pocet_zmena_tyden=None
        # ))

        app.logger.info('Computing vaccination centers metrics - registrations finished.')

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


if __name__ == '__main__':
    etl = Etl()
    etl.compute_all()