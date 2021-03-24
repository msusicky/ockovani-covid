from datetime import timedelta

from sqlalchemy import func, case, text, or_, and_

from app import db, app, queries
from app.models import OckovaciMisto, OckovaciMistoMetriky, OckovaniRegistrace, OckovaniRezervace, OckovaniLide, \
    OckovaniDistribuce, OckovaniSpotreba


class CenterMetricsEtl:
    """Class for computing metrics for vaccination centers."""

    def __init__(self, date_, import_id):
        self._date = date_
        self._import_id = import_id

    def compute(self, metric):
        if metric == 'all':
            self._compute_registrations()
            self._compute_reservations()
            self._compute_vaccinated()
            self._compute_distributed()
            self._compute_used()
            self._compute_derived()
            self._compute_deltas()
        elif metric == 'registrations':
            self._compute_registrations()
        elif metric == 'reservations':
            self._compute_reservations()
        elif metric == 'vaccinated':
            self._compute_vaccinated()
        elif metric == 'distributed':
            self._compute_distributed()
        elif metric == 'used':
            self._compute_used()
        elif metric == 'derived':
            self._compute_derived()
        elif metric == 'deltas':
            self._compute_deltas()
        else:
            raise Exception("Invalid metric argument.")

    def _compute_registrations(self):
        """Computes metrics based on registrations dataset for each vaccination center."""
        registrations = db.session.query(
            OckovaciMisto.id, func.coalesce(func.sum(OckovaniRegistrace.pocet), 0).label('registrace_celkem'),
            func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == False, OckovaniRegistrace.pocet)], else_=0)), 0).label("registrace_fronta")
        ).outerjoin(OckovaniRegistrace, and_(OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id, OckovaniRegistrace.import_id == self._import_id)) \
            .group_by(OckovaciMisto.id) \
            .all()

        for registration in registrations:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=registration.id,
                datum=self._date,
                registrace_celkem=registration.registrace_celkem,
                registrace_fronta=registration.registrace_fronta
            ))

        app.logger.info('Computing vaccination centers metrics - registrations finished.')

    def _compute_reservations(self):
        """Computes metrics based on reservations dataset for each vaccination center."""
        reservations = db.session.query(
            OckovaciMisto.id,
            func.coalesce(func.sum(OckovaniRezervace.maximalni_kapacita - OckovaniRezervace.volna_kapacita), 0).label('rezervace_celkem'),
            func.coalesce(func.sum(case([(OckovaniRezervace.datum >= self._date, OckovaniRezervace.maximalni_kapacita - OckovaniRezervace.volna_kapacita)], else_=0)), 0).label("rezervace_cekajici"),
            func.coalesce(func.sum(case([(and_(OckovaniRezervace.datum >= self._date, OckovaniRezervace.kalendar_ockovani == 'V1'), OckovaniRezervace.maximalni_kapacita - OckovaniRezervace.volna_kapacita)], else_=0)), 0).label("rezervace_cekajici_1"),
            func.coalesce(func.sum(case([(and_(OckovaniRezervace.datum >= self._date, OckovaniRezervace.kalendar_ockovani == 'V2'), OckovaniRezervace.maximalni_kapacita - OckovaniRezervace.volna_kapacita)], else_=0)), 0).label("rezervace_cekajici_2"),
            func.coalesce(func.sum(case([(OckovaniRezervace.datum == self._date, OckovaniRezervace.maximalni_kapacita)], else_=0)), 0).label("rezervace_kapacita"),
            func.coalesce(func.sum(case([(and_(OckovaniRezervace.datum == self._date, OckovaniRezervace.kalendar_ockovani == 'V1'), OckovaniRezervace.maximalni_kapacita)], else_=0)), 0).label("rezervace_kapacita_1"),
            func.coalesce(func.sum(case([(and_(OckovaniRezervace.datum == self._date, OckovaniRezervace.kalendar_ockovani == 'V2'), OckovaniRezervace.maximalni_kapacita)], else_=0)), 0).label("rezervace_kapacita_2"),
            func.min(case([(and_(OckovaniRezervace.datum >= self._date, OckovaniRezervace.kalendar_ockovani == 'V1', OckovaniRezervace.volna_kapacita > 0), OckovaniRezervace.datum)], else_=None)).label("rezervace_nejblizsi_volno")
        ).outerjoin(OckovaniRezervace, and_(OckovaciMisto.id == OckovaniRezervace.ockovaci_misto_id, OckovaniRezervace.import_id == self._import_id)) \
            .group_by(OckovaciMisto.id) \
            .all()

        for reservation in reservations:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=reservation.id,
                datum=self._date,
                rezervace_celkem=reservation.rezervace_celkem,
                rezervace_cekajici=reservation.rezervace_cekajici,
                rezervace_cekajici_1=reservation.rezervace_cekajici_1,
                rezervace_cekajici_2=reservation.rezervace_cekajici_2,
                rezervace_kapacita=reservation.rezervace_kapacita,
                rezervace_kapacita_1=reservation.rezervace_kapacita_1,
                rezervace_kapacita_2=reservation.rezervace_kapacita_2,
                rezervace_nejblizsi_volno=reservation.rezervace_nejblizsi_volno
            ))

        app.logger.info('Computing vaccination centers metrics - reservations finished.')

    def _compute_vaccinated(self):
        """Computes metrics based on vaccinated people dataset for each vaccination center."""
        vaccinated = db.session.query(OckovaciMisto.id, func.coalesce(func.sum(OckovaniLide.pocet), 0).label('ockovani_pocet_davek'),
                                      func.coalesce(func.sum(case([(OckovaniLide.poradi_davky == 1, OckovaniLide.pocet)], else_=0)), 0).label('ockovani_pocet_castecne'),
                                      func.coalesce(func.sum(case([(OckovaniLide.poradi_davky == 2, OckovaniLide.pocet)], else_=0)), 0).label('ockovani_pocet_plne')) \
            .outerjoin(OckovaniLide, and_(OckovaciMisto.nrpzs_kod == OckovaniLide.zarizeni_kod, OckovaniLide.datum < self._date)) \
            .filter(OckovaciMisto.nrpzs_kod.in_(queries.unique_nrpzs_subquery())) \
            .group_by(OckovaciMisto.id) \
            .all()

        for vacc in vaccinated:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=vacc.id,
                datum=self._date,
                ockovani_pocet_davek=vacc.ockovani_pocet_davek,
                ockovani_pocet_castecne=vacc.ockovani_pocet_castecne,
                ockovani_pocet_plne=vacc.ockovani_pocet_plne
            ))

        app.logger.info('Computing vaccination centers metrics - vaccinated people finished.')

    def _compute_distributed(self):
        """Computes metrics based on distributed vaccines dataset for each vaccination center."""
        distributed = db.session.query(
            OckovaciMisto.id, (
                    func.coalesce(func.sum(case([(and_(OckovaciMisto.id == OckovaniDistribuce.ockovaci_misto_id, OckovaniDistribuce.akce == 'Příjem'), OckovaniDistribuce.pocet_davek)], else_=0)), 0)
                    + func.coalesce(func.sum(case([(and_(OckovaciMisto.id == OckovaniDistribuce.cilove_ockovaci_misto_id, OckovaniDistribuce.akce == 'Výdej'), OckovaniDistribuce.pocet_davek)], else_=0)), 0)
                    - func.coalesce(func.sum(case([(and_(OckovaciMisto.id == OckovaniDistribuce.ockovaci_misto_id, OckovaniDistribuce.akce == 'Výdej'), OckovaniDistribuce.pocet_davek)], else_=0)), 0))
                .label('vakciny_prijate_pocet')
        ).outerjoin(OckovaniDistribuce, and_(
            or_(OckovaciMisto.id == OckovaniDistribuce.ockovaci_misto_id, OckovaciMisto.id == OckovaniDistribuce.cilove_ockovaci_misto_id),
            OckovaniDistribuce.datum < self._date
        )) \
            .group_by(OckovaciMisto.id) \
            .all()

        for dist in distributed:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=dist.id,
                datum=self._date,
                vakciny_prijate_pocet=dist.vakciny_prijate_pocet
            ))

        app.logger.info('Computing vaccination centers metrics - distributed vaccines finished.')

    def _compute_used(self):
        """Computes metrics based on used vaccines dataset for each vaccination center."""
        used = db.session.query(
            OckovaciMisto.id,
            func.coalesce(func.sum(OckovaniSpotreba.pouzite_davky), 0).label('vakciny_ockovane_pocet'),
            func.coalesce(func.sum(OckovaniSpotreba.znehodnocene_davky), 0).label('vakciny_znicene_pocet')
        ).outerjoin(OckovaniSpotreba, and_(OckovaciMisto.id == OckovaniSpotreba.ockovaci_misto_id, OckovaniSpotreba.datum < self._date)) \
            .group_by(OckovaciMisto.id) \
            .all()

        for use in used:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=use.id,
                datum=self._date,
                vakciny_ockovane_pocet=use.vakciny_ockovane_pocet,
                vakciny_znicene_pocet=use.vakciny_znicene_pocet
            ))

        app.logger.info('Computing vaccination centers metrics - used vaccines finished.')

    def _compute_derived(self):
        """Computes metrics derived from the previous metrics for each vaccination center."""
        avg_waiting = db.session.query(
            OckovaciMisto.id,
            (func.sum((OckovaniRegistrace.datum_rezervace - OckovaniRegistrace.datum) * OckovaniRegistrace.pocet)
             / func.sum(OckovaniRegistrace.pocet)).label('registrace_prumer_cekani'),
        ).join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum_rezervace >= self._date - timedelta(7)) \
            .group_by(OckovaciMisto.id) \
            .all()

        for wait in avg_waiting:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=wait.id,
                datum=self._date,
                registrace_prumer_cekani=wait.registrace_prumer_cekani
            ))

        avg_queue_waiting = db.session.query(
            OckovaciMisto.id,
            (func.sum((self._date - OckovaniRegistrace.datum) * OckovaniRegistrace.pocet)
             / func.sum(OckovaniRegistrace.pocet)).label('registrace_fronta_prumer_cekani'),
        ).join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.rezervace == False) \
            .group_by(OckovaciMisto.id) \
            .all()

        for queue_wait in avg_queue_waiting:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=queue_wait.id,
                datum=self._date,
                registrace_fronta_prumer_cekani=queue_wait.registrace_fronta_prumer_cekani
            ))

        est_waiting = db.session.query("id", "registrace_odhad_cekani").from_statement(text(
            """
            select id, 7.0 * sum(case when rezervace = false then pocet else 0 end) 
                / nullif(sum(case when rezervace = true and datum_rezervace >= :datum_7 then pocet else 0 end), 0)
                 registrace_odhad_cekani
            from ockovaci_mista
            join ockovani_registrace on id = ockovaci_misto_id
            where import_id = :import_id
            group by (id)
            """
        )).params(datum_7=self._date - timedelta(7), import_id=self._import_id) \
            .all()

        for wait in est_waiting:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=wait.id,
                datum=self._date,
                registrace_odhad_cekani=wait.registrace_odhad_cekani
            ))

        success_ratio_7 = db.session.query(
            OckovaciMisto.id,
            (1.0 * func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0)), 0)
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_tydenni_uspesnost')
        ).join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(7)) \
            .group_by(OckovaciMisto.id) \
            .all()

        for ratio in success_ratio_7:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=ratio.id,
                datum=self._date,
                registrace_tydenni_uspesnost=ratio.registrace_tydenni_uspesnost
            ))

        success_ratio_14 = db.session.query(
            OckovaciMisto.id,
            (1.0 * func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0)), 0)
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_14denni_uspesnost')
        ).join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(14)) \
            .group_by(OckovaciMisto.id) \
            .all()

        for ratio in success_ratio_14:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=ratio.id,
                datum=self._date,
                registrace_14denni_uspesnost=ratio.registrace_14denni_uspesnost
            ))

        success_ratio_30 = db.session.query(
            OckovaciMisto.id,
            (1.0 * func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0)), 0)
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_30denni_uspesnost')
        ).join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(30)) \
            .group_by(OckovaciMisto.id) \
            .all()

        for ratio in success_ratio_30:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=ratio.id,
                datum=self._date,
                registrace_30denni_uspesnost=ratio.registrace_30denni_uspesnost
            ))

        vacc_est_waiting = db.session.query(
            OckovaciMisto.id,
            (7.0 * (OckovaciMistoMetriky.registrace_fronta + OckovaciMistoMetriky.rezervace_cekajici)
             / case([(func.sum(OckovaniLide.pocet) > 0, func.sum(OckovaniLide.pocet))], else_=None)).label('ockovani_odhad_cekani')
        ).join(OckovaciMistoMetriky, OckovaciMisto.id == OckovaciMistoMetriky.misto_id) \
            .join(OckovaniLide, OckovaciMisto.nrpzs_kod == OckovaniLide.zarizeni_kod) \
            .filter(OckovaciMistoMetriky.datum == self._date) \
            .filter(OckovaciMisto.nrpzs_kod.in_(queries.unique_nrpzs_subquery())) \
            .filter(OckovaniLide.datum < self._date, OckovaniLide.datum >= self._date - timedelta(7)) \
            .group_by(OckovaciMisto.id, OckovaciMistoMetriky.registrace_fronta, OckovaciMistoMetriky.rezervace_cekajici) \
            .all()

        for wait in vacc_est_waiting:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=wait.id,
                datum=self._date,
                ockovani_odhad_cekani=wait.ockovani_odhad_cekani
            ))

        vacc_skladem = db.session.query(
            OckovaciMisto.id, (OckovaciMistoMetriky.vakciny_prijate_pocet - OckovaciMistoMetriky.vakciny_ockovane_pocet
                               - OckovaciMistoMetriky.vakciny_znicene_pocet).label('vakciny_skladem_pocet')
        ).join(OckovaciMistoMetriky, OckovaciMisto.id == OckovaciMistoMetriky.misto_id) \
            .filter(OckovaciMistoMetriky.datum == self._date) \
            .group_by(OckovaciMisto.id, OckovaciMistoMetriky.vakciny_prijate_pocet, OckovaciMistoMetriky.vakciny_ockovane_pocet,
                      OckovaciMistoMetriky.vakciny_znicene_pocet) \
            .all()

        for vacc in vacc_skladem:
            db.session.merge(OckovaciMistoMetriky(
                misto_id=vacc.id,
                datum=self._date,
                vakciny_skladem_pocet=vacc.vakciny_skladem_pocet
            ))

        app.logger.info('Computing vaccination centers metrics - derived metrics finished.')

    def _compute_deltas(self):
        """Computes deltas for previous metrics for each vaccination center."""
        db.session.execute(text(
            """
            update ockovaci_mista_metriky t
            set rezervace_celkem_zmena_den = t0.rezervace_celkem - t1.rezervace_celkem,
                rezervace_cekajici_zmena_den = t0.rezervace_cekajici - t1.rezervace_cekajici,
                rezervace_cekajici_1_zmena_den = t0.rezervace_cekajici_1 - t1.rezervace_cekajici_1,
                rezervace_cekajici_2_zmena_den = t0.rezervace_cekajici_2 - t1.rezervace_cekajici_2,
                rezervace_kapacita_zmena_den = t0.rezervace_kapacita - t1.rezervace_kapacita,
                rezervace_kapacita_1_zmena_den = t0.rezervace_kapacita_1 - t1.rezervace_kapacita_1,
                rezervace_kapacita_2_zmena_den = t0.rezervace_kapacita_2 - t1.rezervace_kapacita_2,
                registrace_celkem_zmena_den = t0.registrace_celkem - t1.registrace_celkem,
                registrace_fronta_zmena_den = t0.registrace_fronta - t1.registrace_fronta,
                registrace_tydenni_uspesnost_zmena_den = t0.registrace_tydenni_uspesnost - t1.registrace_tydenni_uspesnost,
                registrace_14denni_uspesnost_zmena_den = t0.registrace_14denni_uspesnost - t1.registrace_14denni_uspesnost,
                registrace_30denni_uspesnost_zmena_den = t0.registrace_30denni_uspesnost - t1.registrace_30denni_uspesnost,
                registrace_prumer_cekani_zmena_den = t0.registrace_prumer_cekani - t1.registrace_prumer_cekani,
                registrace_odhad_cekani_zmena_den = t0.registrace_odhad_cekani - t1.registrace_odhad_cekani,
                registrace_fronta_prumer_cekani_zmena_den = t0.registrace_fronta_prumer_cekani - t1.registrace_fronta_prumer_cekani,
                ockovani_pocet_davek_zmena_den = t0.ockovani_pocet_davek - t1.ockovani_pocet_davek,
                ockovani_pocet_castecne_zmena_den = t0.ockovani_pocet_castecne - t1.ockovani_pocet_castecne,
                ockovani_pocet_plne_zmena_den = t0.ockovani_pocet_plne - t1.ockovani_pocet_plne,
                ockovani_odhad_cekani_zmena_den = t0.ockovani_odhad_cekani - t1.ockovani_odhad_cekani,
                vakciny_prijate_pocet_zmena_den = t0.vakciny_prijate_pocet - t1.vakciny_prijate_pocet,
                vakciny_ockovane_pocet_zmena_den = t0.vakciny_ockovane_pocet - t1.vakciny_ockovane_pocet,
                vakciny_znicene_pocet_zmena_den = t0.vakciny_znicene_pocet - t1.vakciny_znicene_pocet,
                vakciny_skladem_pocet_zmena_den = t0.vakciny_skladem_pocet - t1.vakciny_skladem_pocet
            from ockovaci_mista_metriky t0 
            join ockovaci_mista_metriky t1
            on t0.misto_id = t1.misto_id
            where t.misto_id = t0.misto_id and t.datum = :datum and t0.datum = :datum and t1.datum = :datum_1  
            """
        ), {'datum': self._date, 'datum_1': self._date - timedelta(1)})

        db.session.execute(text(
            """
            update ockovaci_mista_metriky t
            set rezervace_celkem_zmena_tyden = t0.rezervace_celkem - t7.rezervace_celkem,
                rezervace_cekajici_zmena_tyden = t0.rezervace_cekajici - t7.rezervace_cekajici,
                rezervace_cekajici_1_zmena_tyden = t0.rezervace_cekajici_1 - t7.rezervace_cekajici_1,
                rezervace_cekajici_2_zmena_tyden = t0.rezervace_cekajici_2 - t7.rezervace_cekajici_2,
                rezervace_kapacita_zmena_tyden = t0.rezervace_kapacita - t7.rezervace_kapacita,
                rezervace_kapacita_1_zmena_tyden = t0.rezervace_kapacita_1 - t7.rezervace_kapacita_1,
                rezervace_kapacita_2_zmena_tyden = t0.rezervace_kapacita_2 - t7.rezervace_kapacita_2,
                registrace_celkem_zmena_tyden = t0.registrace_celkem - t7.registrace_celkem,
                registrace_fronta_zmena_tyden = t0.registrace_fronta - t7.registrace_fronta,
                registrace_tydenni_uspesnost_zmena_tyden = t0.registrace_tydenni_uspesnost - t7.registrace_tydenni_uspesnost,
                registrace_14denni_uspesnost_zmena_tyden = t0.registrace_14denni_uspesnost - t7.registrace_14denni_uspesnost,
                registrace_30denni_uspesnost_zmena_tyden = t0.registrace_30denni_uspesnost - t7.registrace_30denni_uspesnost,
                registrace_prumer_cekani_zmena_tyden = t0.registrace_prumer_cekani - t7.registrace_prumer_cekani,
                registrace_odhad_cekani_zmena_tyden = t0.registrace_odhad_cekani - t7.registrace_odhad_cekani,
                registrace_fronta_prumer_cekani_zmena_tyden = t0.registrace_fronta_prumer_cekani - t7.registrace_fronta_prumer_cekani,
                ockovani_pocet_davek_zmena_tyden = t0.ockovani_pocet_davek - t7.ockovani_pocet_davek,
                ockovani_pocet_castecne_zmena_tyden = t0.ockovani_pocet_castecne - t7.ockovani_pocet_castecne,
                ockovani_pocet_plne_zmena_tyden = t0.ockovani_pocet_plne - t7.ockovani_pocet_plne,
                ockovani_odhad_cekani_zmena_tyden = t0.ockovani_odhad_cekani - t7.ockovani_odhad_cekani,
                vakciny_prijate_pocet_zmena_tyden = t0.vakciny_prijate_pocet - t7.vakciny_prijate_pocet,
                vakciny_ockovane_pocet_zmena_tyden = t0.vakciny_ockovane_pocet - t7.vakciny_ockovane_pocet,
                vakciny_znicene_pocet_zmena_tyden = t0.vakciny_znicene_pocet - t7.vakciny_znicene_pocet,
                vakciny_skladem_pocet_zmena_tyden = t0.vakciny_skladem_pocet - t7.vakciny_skladem_pocet
            from ockovaci_mista_metriky t0 
            join ockovaci_mista_metriky t7
            on t0.misto_id = t7.misto_id
            where t.misto_id = t0.misto_id and t.datum = :datum and t0.datum = :datum and t7.datum = :datum_7  
            """
        ), {'datum': self._date, 'datum_7': self._date - timedelta(7)})

        app.logger.info('Computing vaccination centers metrics - deltas finished.')
