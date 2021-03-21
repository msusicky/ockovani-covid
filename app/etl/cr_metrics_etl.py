from datetime import timedelta

from sqlalchemy import func, case, text

from app import db, app
from app.models import OckovaciMistoMetriky, OckovaniRegistrace, OckovaniLide, Populace, CrMetriky, OckovaniDistribuce


class CrMetricsEtl:
    """Class for computing metrics for whole Czech republic."""

    def __init__(self, date_, import_id):
        self._date = date_
        self._import_id = import_id

    def compute_all(self):
        self._compute_cr_population()
        self._compute_cr_registrations()
        self._compute_cr_reservations()
        self._compute_cr_vaccinated()
        self._compute_cr_distributed()
        self._compute_cr_used()
        self._compute_cr_derived()
        self._compute_cr_deltas()

    def _compute_cr_population(self):
        """Computes metrics based on population for cr."""
        population = db.session.query(
            func.sum(Populace.pocet).label('pocet_obyvatel_celkem'),
            func.sum(case([(Populace.vek >= 18, Populace.pocet)], else_=0)).label('pocet_obyvatel_dospeli')
        ).filter(Populace.orp_kod == 'CZ0') \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            pocet_obyvatel_celkem=population.pocet_obyvatel_celkem,
            pocet_obyvatel_dospeli=population.pocet_obyvatel_dospeli
        ))

        app.logger.info('Computing cr metrics - population finished.')

    def _compute_cr_registrations(self):
        """Computes metrics based on registrations dataset for cr."""
        registrations = db.session.query(
            func.sum(OckovaciMistoMetriky.registrace_celkem).label('registrace_celkem'),
            func.sum(OckovaciMistoMetriky.registrace_fronta).label("registrace_fronta")
        ).filter(OckovaciMistoMetriky.datum == self._date) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            registrace_celkem=registrations.registrace_celkem,
            registrace_fronta=registrations.registrace_fronta
        ))

        app.logger.info('Computing cr metrics - registrations finished.')

    def _compute_cr_reservations(self):
        """Computes metrics based on reservations dataset for cr."""
        reservations = db.session.query(
            func.sum(OckovaciMistoMetriky.rezervace_celkem).label('rezervace_celkem'),
            func.sum(OckovaciMistoMetriky.rezervace_cekajici).label("rezervace_cekajici"),
            func.sum(OckovaciMistoMetriky.rezervace_kapacita).label("rezervace_kapacita"),
            func.sum(OckovaciMistoMetriky.rezervace_kapacita_1).label("rezervace_kapacita_1")
        ).filter(OckovaciMistoMetriky.datum == self._date) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            rezervace_celkem=reservations.rezervace_celkem,
            rezervace_cekajici=reservations.rezervace_cekajici,
            rezervace_kapacita=reservations.rezervace_kapacita,
            rezervace_kapacita_1=reservations.rezervace_kapacita_1
        ))

        app.logger.info('Computing cr metrics - reservations finished.')

    def _compute_cr_vaccinated(self):
        """Computes metrics based on vaccinated people dataset for cr."""
        vaccinated = db.session.query(
            func.coalesce(func.sum(OckovaniLide.pocet), 0).label('ockovani_pocet_davek'),
            func.coalesce(func.sum(case([(OckovaniLide.poradi_davky == 1, OckovaniLide.pocet)], else_=0)), 0).label('ockovani_pocet_castecne'),
            func.coalesce(func.sum(case([(OckovaniLide.poradi_davky == 2, OckovaniLide.pocet)], else_=0)), 0).label('ockovani_pocet_plne')
        ).filter(OckovaniLide.datum < self._date) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            ockovani_pocet_davek=vaccinated.ockovani_pocet_davek,
            ockovani_pocet_castecne=vaccinated.ockovani_pocet_castecne,
            ockovani_pocet_plne=vaccinated.ockovani_pocet_plne
        ))

        app.logger.info('Computing cr metrics - vaccinated people finished.')

    def _compute_cr_distributed(self):
        """Computes metrics based on distributed vaccines dataset for cr."""
        distributed = db.session.query(
            func.sum(case([(OckovaniDistribuce.akce == 'Příjem', OckovaniDistribuce.pocet_davek)], else_=0)).label('vakciny_prijate_pocet')
        ).filter(OckovaniDistribuce.datum < self._date) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            vakciny_prijate_pocet=distributed.vakciny_prijate_pocet
        ))

        app.logger.info('Computing cr metrics - distributed vaccines finished.')

    def _compute_cr_used(self):
        """Computes metrics based on used vaccines dataset for cr."""
        used = db.session.query(
            func.sum(OckovaciMistoMetriky.vakciny_ockovane_pocet).label('vakciny_ockovane_pocet'),
            func.sum(OckovaciMistoMetriky.vakciny_znicene_pocet).label("vakciny_znicene_pocet")
        ).filter(OckovaciMistoMetriky.datum == self._date) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            vakciny_ockovane_pocet=used.vakciny_ockovane_pocet,
            vakciny_znicene_pocet=used.vakciny_znicene_pocet
        ))

        app.logger.info('Computing cr metrics - used vaccines finished.')

    def _compute_cr_derived(self):
        """Computes metrics derived from the previous metrics for cr."""
        avg_waiting = db.session.query(
            (func.sum((OckovaniRegistrace.datum_rezervace - OckovaniRegistrace.datum) * OckovaniRegistrace.pocet)
             / func.sum(OckovaniRegistrace.pocet)).label('registrace_prumer_cekani'),
        ).filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum_rezervace >= self._date - timedelta(7)) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            registrace_prumer_cekani=avg_waiting.registrace_prumer_cekani
        ))

        avg_queue_waiting = db.session.query(
            (func.sum((self._date - OckovaniRegistrace.datum) * OckovaniRegistrace.pocet)
             / func.sum(OckovaniRegistrace.pocet)).label('registrace_fronta_prumer_cekani'),
        ).filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.rezervace == False) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            registrace_fronta_prumer_cekani=avg_queue_waiting.registrace_fronta_prumer_cekani
        ))

        success_ratio_7 = db.session.query(
            (1.0 * func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0)), 0)
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_tydenni_uspesnost')
        ).filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(7)) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            registrace_tydenni_uspesnost=success_ratio_7.registrace_tydenni_uspesnost
        ))

        success_ratio_14 = db.session.query(
            (1.0 * func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0)), 0)
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_14denni_uspesnost')
        ).filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(14)) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            registrace_14denni_uspesnost=success_ratio_14.registrace_14denni_uspesnost
        ))

        success_ratio_30 = db.session.query(
            (1.0 * func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0)), 0)
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_30denni_uspesnost')
        ).filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(30)) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            registrace_30denni_uspesnost=success_ratio_30.registrace_30denni_uspesnost
        ))

        vacc_skladem = db.session.query(
            (CrMetriky.vakciny_prijate_pocet - CrMetriky.ockovani_pocet_davek - CrMetriky.vakciny_znicene_pocet).label('vakciny_skladem_pocet')
        ).filter(CrMetriky.datum == self._date) \
            .one()

        db.session.merge(CrMetriky(
            datum=self._date,
            vakciny_skladem_pocet=vacc_skladem.vakciny_skladem_pocet
        ))

        app.logger.info('Computing cr metrics - derived metrics finished.')

    def _compute_cr_deltas(self):
        """Computes deltas for previous metrics for cr."""
        db.session.execute(text(
            """
            update cr_metriky t
            set rezervace_celkem_zmena_den = t0.rezervace_celkem - t1.rezervace_celkem,
                rezervace_cekajici_zmena_den = t0.rezervace_cekajici - t1.rezervace_cekajici,
                rezervace_kapacita_zmena_den = t0.rezervace_kapacita - t1.rezervace_kapacita,
                rezervace_kapacita_1_zmena_den = t0.rezervace_kapacita_1 - t1.rezervace_kapacita_1,
                registrace_celkem_zmena_den = t0.registrace_celkem - t1.registrace_celkem,
                registrace_fronta_zmena_den = t0.registrace_fronta - t1.registrace_fronta,
                registrace_tydenni_uspesnost_zmena_den = t0.registrace_tydenni_uspesnost - t1.registrace_tydenni_uspesnost,
                registrace_14denni_uspesnost_zmena_den = t0.registrace_14denni_uspesnost - t1.registrace_14denni_uspesnost,
                registrace_30denni_uspesnost_zmena_den = t0.registrace_30denni_uspesnost - t1.registrace_30denni_uspesnost,
                registrace_prumer_cekani_zmena_den = t0.registrace_prumer_cekani - t1.registrace_prumer_cekani,
                registrace_fronta_prumer_cekani_zmena_den = t0.registrace_fronta_prumer_cekani - t1.registrace_fronta_prumer_cekani,
                ockovani_pocet_davek_zmena_den = t0.ockovani_pocet_davek - t1.ockovani_pocet_davek,
                ockovani_pocet_castecne_zmena_den = t0.ockovani_pocet_castecne - t1.ockovani_pocet_castecne,
                ockovani_pocet_plne_zmena_den = t0.ockovani_pocet_plne - t1.ockovani_pocet_plne,
                vakciny_prijate_pocet_zmena_den = t0.vakciny_prijate_pocet - t1.vakciny_prijate_pocet,
                vakciny_ockovane_pocet_zmena_den = t0.vakciny_ockovane_pocet - t1.vakciny_ockovane_pocet,
                vakciny_znicene_pocet_zmena_den = t0.vakciny_znicene_pocet - t1.vakciny_znicene_pocet,
                vakciny_skladem_pocet_zmena_den = t0.vakciny_skladem_pocet - t1.vakciny_skladem_pocet
            from cr_metriky t0 
            cross join cr_metriky t1
            where t.datum = :datum and t0.datum = :datum and t1.datum = :datum_1  
            """
        ), {'datum': self._date, 'datum_1': self._date - timedelta(1)})

        db.session.execute(text(
            """
            update cr_metriky t
            set rezervace_celkem_zmena_tyden = t0.rezervace_celkem - t7.rezervace_celkem,
                rezervace_cekajici_zmena_tyden = t0.rezervace_cekajici - t7.rezervace_cekajici,
                rezervace_kapacita_zmena_tyden = t0.rezervace_kapacita - t7.rezervace_kapacita,
                rezervace_kapacita_1_zmena_tyden = t0.rezervace_kapacita_1 - t7.rezervace_kapacita_1,
                registrace_celkem_zmena_tyden = t0.registrace_celkem - t7.registrace_celkem,
                registrace_fronta_zmena_tyden = t0.registrace_fronta - t7.registrace_fronta,
                registrace_tydenni_uspesnost_zmena_tyden = t0.registrace_tydenni_uspesnost - t7.registrace_tydenni_uspesnost,
                registrace_14denni_uspesnost_zmena_tyden = t0.registrace_14denni_uspesnost - t7.registrace_14denni_uspesnost,
                registrace_30denni_uspesnost_zmena_tyden = t0.registrace_30denni_uspesnost - t7.registrace_30denni_uspesnost,
                registrace_prumer_cekani_zmena_tyden = t0.registrace_prumer_cekani - t7.registrace_prumer_cekani,
                registrace_fronta_prumer_cekani_zmena_tyden = t0.registrace_fronta_prumer_cekani - t7.registrace_fronta_prumer_cekani,
                ockovani_pocet_davek_zmena_tyden = t0.ockovani_pocet_davek - t7.ockovani_pocet_davek,
                ockovani_pocet_castecne_zmena_tyden = t0.ockovani_pocet_castecne - t7.ockovani_pocet_castecne,
                ockovani_pocet_plne_zmena_tyden = t0.ockovani_pocet_plne - t7.ockovani_pocet_plne,
                vakciny_prijate_pocet_zmena_tyden = t0.vakciny_prijate_pocet - t7.vakciny_prijate_pocet,
                vakciny_ockovane_pocet_zmena_tyden = t0.vakciny_ockovane_pocet - t7.vakciny_ockovane_pocet,
                vakciny_znicene_pocet_zmena_tyden = t0.vakciny_znicene_pocet - t7.vakciny_znicene_pocet,
                vakciny_skladem_pocet_zmena_tyden = t0.vakciny_skladem_pocet - t7.vakciny_skladem_pocet
            from cr_metriky t0 
            cross join cr_metriky t7
            where t.datum = :datum and t0.datum = :datum and t7.datum = :datum_7  
            """
        ), {'datum': self._date, 'datum_7': self._date - timedelta(7)})

        app.logger.info('Computing cr metrics - deltas finished.')
