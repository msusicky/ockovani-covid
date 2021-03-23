from datetime import timedelta

from sqlalchemy import func, case, text

from app import db, app
from app.models import OckovaciMisto, OckovaciMistoMetriky, OckovaniRegistrace, Okres, OkresMetriky, Populace


class OkresMetricsEtl:
    """Class for computing metrics for okres."""

    def __init__(self, date_, import_id):
        self._date = date_
        self._import_id = import_id

    def compute(self, metric):
        if metric == 'all':
            self._compute_population()
            self._compute_registrations()
            self._compute_reservations()
            self._compute_distributed()
            self._compute_used()
            self._compute_derived()
            self._compute_deltas()
        elif metric == 'registrations':
            self._compute_registrations()
        elif metric == 'reservations':
            self._compute_reservations()
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

    def _compute_population(self):
        """Computes metrics based on population for each okres."""
        population = db.session.query(
            Okres.id, func.sum(Populace.pocet).label('pocet_obyvatel_celkem'),
            func.sum(case([(Populace.vek >= 18, Populace.pocet)], else_=0)).label('pocet_obyvatel_dospeli')
        ).join(Populace, Populace.orp_kod == Okres.id) \
            .group_by(Okres.id)

        for pop in population:
            db.session.merge(OkresMetriky(
                okres_id=pop.id,
                datum=self._date,
                pocet_obyvatel_celkem=pop.pocet_obyvatel_celkem,
                pocet_obyvatel_dospeli=pop.pocet_obyvatel_dospeli
            ))

        app.logger.info('Computing okres metrics - population finished.')

    def _compute_registrations(self):
        """Computes metrics based on registrations dataset for each okres."""
        registrations = db.session.query(
            Okres.id, func.sum(OckovaciMistoMetriky.registrace_celkem).label('registrace_celkem'),
            func.sum(OckovaciMistoMetriky.registrace_fronta).label("registrace_fronta")
        ).join(OckovaciMisto, (OckovaciMisto.okres_id == Okres.id)) \
            .join(OckovaciMistoMetriky, OckovaciMistoMetriky.misto_id == OckovaciMisto.id) \
            .filter(OckovaciMistoMetriky.datum == self._date) \
            .group_by(Okres.id) \
            .all()

        for registration in registrations:
            db.session.merge(OkresMetriky(
                okres_id=registration.id,
                datum=self._date,
                registrace_celkem=registration.registrace_celkem,
                registrace_fronta=registration.registrace_fronta
            ))

        app.logger.info('Computing okres metrics - registrations finished.')

    def _compute_reservations(self):
        """Computes metrics based on reservations dataset for each okres."""
        reservations = db.session.query(
            Okres.id, func.sum(OckovaciMistoMetriky.rezervace_celkem).label('rezervace_celkem'),
            func.sum(OckovaciMistoMetriky.rezervace_cekajici).label("rezervace_cekajici"),
            func.sum(OckovaciMistoMetriky.rezervace_cekajici_1).label("rezervace_cekajici_1"),
            func.sum(OckovaciMistoMetriky.rezervace_cekajici_2).label("rezervace_cekajici_2"),
            func.sum(OckovaciMistoMetriky.rezervace_kapacita).label("rezervace_kapacita"),
            func.sum(OckovaciMistoMetriky.rezervace_kapacita_1).label("rezervace_kapacita_1"),
            func.sum(OckovaciMistoMetriky.rezervace_kapacita_2).label("rezervace_kapacita_2"),
            func.min(OckovaciMistoMetriky.rezervace_nejblizsi_volno).label('rezervace_nejblizsi_volno')
        ).join(OckovaciMisto, (OckovaciMisto.okres_id == Okres.id)) \
            .join(OckovaciMistoMetriky, OckovaciMistoMetriky.misto_id == OckovaciMisto.id) \
            .filter(OckovaciMistoMetriky.datum == self._date) \
            .group_by(Okres.id) \
            .all()

        for reservation in reservations:
            db.session.merge(OkresMetriky(
                okres_id=reservation.id,
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

        app.logger.info('Computing okres metrics - reservations finished.')

    def _compute_distributed(self):
        """Computes metrics based on distributed vaccines dataset for each okres."""
        distributed = db.session.query("okres_id", "vakciny_prijate_pocet").from_statement(text(
            """
            select m.okres_id okres_id, ( 
                coalesce(sum(case
                    when akce = 'Příjem' 
                        and d.ockovaci_misto_id in (select m1.id from ockovaci_mista m1 where m1.okres_id = m.okres_id) 
                    then pocet_davek
                    else 0 end
                ), 0) 
                + coalesce(sum(case
                    when akce = 'Výdej' 
                        and d.cilove_ockovaci_misto_id in (select m2.id from ockovaci_mista m2 where m2.okres_id = m.okres_id) 
                    then pocet_davek 
                    else 0 end
                ), 0) 
                - coalesce(sum(case 
                    when akce = 'Výdej' 
                        and d.ockovaci_misto_id in (select m3.id from ockovaci_mista m3 where m3.okres_id = m.okres_id) 
                        and d.cilove_ockovaci_misto_id != '' 
                    then pocet_davek 
                    else 0 end
                ), 0) 
            ) vakciny_prijate_pocet
            from ockovaci_mista m
            left join ockovani_distribuce d on (d.ockovaci_misto_id = m.id or d.cilove_ockovaci_misto_id = m.id)
            group by (m.okres_id)
            """
        )).all()

        for dist in distributed:
            db.session.merge(OkresMetriky(
                okres_id=dist.okres_id,
                datum=self._date,
                vakciny_prijate_pocet=dist.vakciny_prijate_pocet
            ))

        app.logger.info('Computing okres metrics - distributed vaccines finished.')

    def _compute_used(self):
        """Computes metrics based on used vaccines dataset for each okres."""
        used = db.session.query(
            Okres.id, func.sum(OckovaciMistoMetriky.vakciny_ockovane_pocet).label('vakciny_ockovane_pocet'),
            func.sum(OckovaciMistoMetriky.vakciny_znicene_pocet).label("vakciny_znicene_pocet")
        ).join(OckovaciMisto, (OckovaciMisto.okres_id == Okres.id)) \
            .join(OckovaciMistoMetriky, OckovaciMistoMetriky.misto_id == OckovaciMisto.id) \
            .filter(OckovaciMistoMetriky.datum == self._date) \
            .group_by(Okres.id) \
            .all()

        for use in used:
            db.session.merge(OkresMetriky(
                okres_id=use.id,
                datum=self._date,
                vakciny_ockovane_pocet=use.vakciny_ockovane_pocet,
                vakciny_znicene_pocet=use.vakciny_znicene_pocet
            ))

        app.logger.info('Computing okres metrics - used vaccines finished.')

    def _compute_derived(self):
        """Computes metrics derived from the previous metrics for each okres."""
        avg_waiting = db.session.query(
            Okres.id,
            (func.sum((OckovaniRegistrace.datum_rezervace - OckovaniRegistrace.datum) * OckovaniRegistrace.pocet)
             / func.sum(OckovaniRegistrace.pocet)).label('registrace_prumer_cekani'),
        ).join(OckovaciMisto, (OckovaciMisto.okres_id == Okres.id)) \
            .join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum_rezervace >= self._date - timedelta(7)) \
            .group_by(Okres.id) \
            .all()

        for wait in avg_waiting:
            db.session.merge(OkresMetriky(
                okres_id=wait.id,
                datum=self._date,
                registrace_prumer_cekani=wait.registrace_prumer_cekani
            ))

        avg_queue_waiting = db.session.query(
            Okres.id,
            (func.sum((self._date - OckovaniRegistrace.datum) * OckovaniRegistrace.pocet)
             / func.sum(OckovaniRegistrace.pocet)).label('registrace_fronta_prumer_cekani'),
        ).join(OckovaciMisto, (OckovaciMisto.okres_id == Okres.id)) \
            .join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.rezervace == False) \
            .group_by(Okres.id) \
            .all()

        for queue_wait in avg_queue_waiting:
            db.session.merge(OkresMetriky(
                okres_id=queue_wait.id,
                datum=self._date,
                registrace_fronta_prumer_cekani=queue_wait.registrace_fronta_prumer_cekani
            ))

        success_ratio_7 = db.session.query(
            Okres.id,
            (1.0 * func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0)), 0)
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_tydenni_uspesnost')
        ).join(OckovaciMisto, (OckovaciMisto.okres_id == Okres.id)) \
            .join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(7)) \
            .group_by(Okres.id) \
            .all()

        for ratio in success_ratio_7:
            db.session.merge(OkresMetriky(
                okres_id=ratio.id,
                datum=self._date,
                registrace_tydenni_uspesnost=ratio.registrace_tydenni_uspesnost
            ))

        success_ratio_14 = db.session.query(
            Okres.id,
            (1.0 * func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0)), 0)
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_14denni_uspesnost')
        ).join(OckovaciMisto, (OckovaciMisto.okres_id == Okres.id)) \
            .join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(14)) \
            .group_by(Okres.id) \
            .all()

        for ratio in success_ratio_14:
            db.session.merge(OkresMetriky(
                okres_id=ratio.id,
                datum=self._date,
                registrace_14denni_uspesnost=ratio.registrace_14denni_uspesnost
            ))

        success_ratio_30 = db.session.query(
            Okres.id,
            (1.0 * func.coalesce(func.sum(case([(OckovaniRegistrace.rezervace == True, OckovaniRegistrace.pocet)], else_=0)), 0)
             / case([(func.sum(OckovaniRegistrace.pocet) == 0, None)], else_=func.sum(OckovaniRegistrace.pocet))).label('registrace_30denni_uspesnost')
        ).join(OckovaciMisto, (OckovaciMisto.okres_id == Okres.id)) \
            .join(OckovaniRegistrace, OckovaciMisto.id == OckovaniRegistrace.ockovaci_misto_id) \
            .filter(OckovaniRegistrace.import_id == self._import_id) \
            .filter(OckovaniRegistrace.datum >= self._date - timedelta(30)) \
            .group_by(Okres.id) \
            .all()

        for ratio in success_ratio_30:
            db.session.merge(OkresMetriky(
                okres_id=ratio.id,
                datum=self._date,
                registrace_30denni_uspesnost=ratio.registrace_30denni_uspesnost
            ))

        app.logger.info('Computing okres metrics - derived metrics finished.')

    def _compute_deltas(self):
        """Computes deltas for previous metrics for each okres."""
        db.session.execute(text(
            """
            update okresy_metriky t
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
                registrace_fronta_prumer_cekani_zmena_den = t0.registrace_fronta_prumer_cekani - t1.registrace_fronta_prumer_cekani,
                vakciny_prijate_pocet_zmena_den = t0.vakciny_prijate_pocet - t1.vakciny_prijate_pocet,
                vakciny_ockovane_pocet_zmena_den = t0.vakciny_ockovane_pocet - t1.vakciny_ockovane_pocet,
                vakciny_znicene_pocet_zmena_den = t0.vakciny_znicene_pocet - t1.vakciny_znicene_pocet
            from okresy_metriky t0 
            join okresy_metriky t1
            on t0.okres_id = t1.okres_id
            where t.okres_id = t0.okres_id and t.datum = :datum and t0.datum = :datum and t1.datum = :datum_1  
            """
        ), {'datum': self._date, 'datum_1': self._date - timedelta(1)})

        db.session.execute(text(
            """
            update okresy_metriky t
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
                registrace_fronta_prumer_cekani_zmena_tyden = t0.registrace_fronta_prumer_cekani - t7.registrace_fronta_prumer_cekani,
                vakciny_prijate_pocet_zmena_tyden = t0.vakciny_prijate_pocet - t7.vakciny_prijate_pocet,
                vakciny_ockovane_pocet_zmena_tyden = t0.vakciny_ockovane_pocet - t7.vakciny_ockovane_pocet,
                vakciny_znicene_pocet_zmena_tyden = t0.vakciny_znicene_pocet - t7.vakciny_znicene_pocet
            from okresy_metriky t0 
            join okresy_metriky t7
            on t0.okres_id = t7.okres_id
            where t.okres_id = t0.okres_id and t.datum = :datum and t0.datum = :datum and t7.datum = :datum_7  
            """
        ), {'datum': self._date, 'datum_7': self._date - timedelta(7)})

        app.logger.info('Computing okres metrics - deltas finished.')
