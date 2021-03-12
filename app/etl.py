from datetime import timedelta, date

from sqlalchemy import func, case, text, or_, and_

from app import db, app, queries
from app.models import OckovaciMisto, OckovaciMistoMetriky, OckovaniRegistrace, OckovaniRezervace, Import, \
    OckovaniLide, OckovaniDistribuce, OckovaniSpotreba


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
            self._compute_vaccination_centers_used()
            self._compute_vaccination_centers_waiting()
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
            .filter(OckovaciMisto.nrpzs_kod.in_(queries.unique_nrpzs_subquery())) \
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
            func.sum(case([(and_(OckovaciMisto.id == OckovaniDistribuce.ockovaci_misto_id, OckovaniDistribuce.akce == 'Výdej'), 0)], else_=OckovaniDistribuce.pocet_davek)).label('vakciny_prijate_pocet'),
            func.sum(case([(and_(OckovaciMisto.id == OckovaniDistribuce.ockovaci_misto_id, OckovaniDistribuce.akce == 'Výdej'), OckovaniDistribuce.pocet_davek)], else_=0)).label('vakciny_vydane_pocet')
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
                vakciny_prijate_pocet=dist.vakciny_prijate_pocet,
                vakciny_vydane_pocet=dist.vakciny_vydane_pocet
            ))

        app.logger.info('Computing vaccination centers metrics - distributed vaccines finished.')

    def _compute_vaccination_centers_used(self):
        distributed = db.session.query(
            OckovaciMisto.id,
            func.sum(OckovaniSpotreba.pouzite_davky).label('vakciny_ockovane_pocet'),
            func.sum(OckovaniSpotreba.znehodnocene_davky).label('vakciny_znicene_pocet')
        ).join(OckovaniSpotreba, OckovaciMisto.id == OckovaniSpotreba.ockovaci_misto_id) \
            .filter(OckovaniSpotreba.datum < self._date) \
            .group_by(OckovaciMisto.id) \
            .all()

        for dist in distributed:
            db.session.merge(OckovaciMistoMetriky(
                id=dist.id,
                datum=self._date,
                vakciny_ockovane_pocet=dist.vakciny_ockovane_pocet,
                vakciny_znicene_pocet=dist.vakciny_znicene_pocet
            ))

        app.logger.info('Computing vaccination centers metrics - used vaccines finished.')

    def _compute_vaccination_centers_waiting(self):
        avg_waiting = db.session.query(
            OckovaciMisto.id,
            func.avg(OckovaniRegistrace.datum_rezervace - OckovaniRegistrace.datum).label('registrace_prumer_cekani'),
        ).join(OckovaniRegistrace, (OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id)) \
            .filter(OckovaniRegistrace.import_id == self._find_import_id()) \
            .filter(OckovaniRegistrace.datum_rezervace >= self._date - timedelta(7)) \
            .group_by(OckovaciMisto.id) \
            .all()

        for wait in avg_waiting:
            db.session.merge(OckovaciMistoMetriky(
                id=wait.id,
                datum=self._date,
                registrace_prumer_cekani=wait.registrace_prumer_cekani
            ))

        est_waiting = db.session.query(
            OckovaciMisto.id,
            (7.0 * func.sum(case([(OckovaniRegistrace.rezervace == False, OckovaniRegistrace.pocet)], else_=0))
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_odhad_cekani')
        ).join(OckovaniRegistrace, (OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id)) \
            .join(OckovaniLide, (OckovaciMisto.nrpzs_kod == OckovaniLide.zarizeni_kod)) \
            .filter(OckovaniRegistrace.import_id == self._find_import_id()) \
            .filter(OckovaniLide.datum < self._date) \
            .filter(OckovaniLide.datum >= self._date - timedelta(7)) \
            .filter(OckovaciMisto.nrpzs_kod.in_(queries.unique_nrpzs_subquery())) \
            .group_by(OckovaciMisto.id) \
            .all()

        for wait in est_waiting:
            db.session.merge(OckovaciMistoMetriky(
                id=wait.id,
                datum=self._date,
                registrace_odhad_cekani=wait.registrace_odhad_cekani
            ))

        success_ratio = db.session.query(
            OckovaciMisto.id,
            (1.0 * func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0))
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_tydenni_uspesnost')
        ).join(OckovaniRegistrace, (OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id)) \
            .filter(OckovaniRegistrace.import_id == self._find_import_id()) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(7)) \
            .group_by(OckovaciMisto.id) \
            .all()

        for rate in success_ratio:
            db.session.merge(OckovaciMistoMetriky(
                id=rate.id,
                datum=self._date,
                registrace_tydenni_uspesnost=rate.registrace_tydenni_uspesnost
            ))

        app.logger.info('Computing vaccination centers metrics - waiting time finished.')

    def _compute_vaccination_centers_deltas(self):
        db.session.execute(text(
            """
            update ockovaci_mista_metriky t
            set rezervace_celkem_zmena_den = t0.rezervace_celkem - t1.rezervace_celkem,
                rezervace_cekajici_zmena_den = t0.rezervace_cekajici - t1.rezervace_cekajici,
                registrace_celkem_zmena_den = t0.registrace_celkem - t1.registrace_celkem,
                registrace_fronta_zmena_den = t0.registrace_fronta - t1.registrace_fronta,
                registrace_tydenni_uspesnost_zmena_den = t0.registrace_tydenni_uspesnost - t1.registrace_tydenni_uspesnost,
                registrace_prumer_cekani_zmena_den = t0.registrace_prumer_cekani - t1.registrace_prumer_cekani,
                registrace_odhad_cekani_zmena_den = t0.registrace_odhad_cekani - t1.registrace_odhad_cekani,
                ockovani_pocet_zmena_den = t0.ockovani_pocet - t1.ockovani_pocet,
                vakciny_prijate_pocet_zmena_den = t0.vakciny_prijate_pocet - t1.vakciny_prijate_pocet,
                vakciny_vydane_pocet_zmena_den = t0.vakciny_vydane_pocet - t1.vakciny_vydane_pocet,
                vakciny_ockovane_pocet_zmena_den = t0.vakciny_ockovane_pocet - t1.vakciny_ockovane_pocet,
                vakciny_znicene_pocet_zmena_den = t0.vakciny_znicene_pocet - t1.vakciny_znicene_pocet
            from ockovaci_mista_metriky t0 
            join ockovaci_mista_metriky t1
            on t0.id = t1.id
            where t.id = t0.id and t.datum = :datum and t0.datum = :datum and t1.datum = :datum_1  
            """
        ), {'datum': self._date, 'datum_1': self._date - timedelta(1)})

        db.session.execute(text(
            """
            update ockovaci_mista_metriky t
            set ockovani_pocet_zmena_tyden = t0.ockovani_pocet - t7.ockovani_pocet,
                vakciny_prijate_pocet_zmena_tyden = t0.vakciny_prijate_pocet - t7.vakciny_prijate_pocet,
                vakciny_vydane_pocet_zmena_tyden = t0.vakciny_vydane_pocet - t7.vakciny_vydane_pocet,
                vakciny_ockovane_pocet_zmena_tyden = t0.vakciny_ockovane_pocet - t7.vakciny_ockovane_pocet,
                vakciny_znicene_pocet_zmena_tyden = t0.vakciny_znicene_pocet - t7.vakciny_znicene_pocet
            from ockovaci_mista_metriky t0 
            join ockovaci_mista_metriky t7
            on t0.id = t7.id
            where t.id = t0.id and t.datum = :datum and t0.datum = :datum and t7.datum = :datum_7  
            """
        ), {'datum': self._date, 'datum_7': self._date - timedelta(7)})

        app.logger.info('Computing vaccination centers metrics - deltas finished.')

    def compute_districts(self):
        return True

    def compute_regions(self):
        return True

    def _find_import_id(self):
        id_ = db.session.query(Import.id) \
            .filter(Import.date == self._date, Import.status == queries.STATUS_FINISHED) \
            .first()[0]
        return -1 if id_ is None else id_


if __name__ == '__main__':
    etl = Etl(date.today())
    etl.compute_all()