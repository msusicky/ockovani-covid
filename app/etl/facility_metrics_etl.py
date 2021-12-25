from datetime import timedelta

from sqlalchemy import func, text

from app import db, app
from app.models import OckovaciMistoMetriky, OckovaniLide


class FacilityMetricsEtl:
    """Class for computing metrics for health facilities."""

    def __init__(self, date_, import_id):
        self._date = date_
        self._import_id = import_id

    def compute(self, metric):
        if metric == 'all':
            self._compute_vaccinated()
            self._compute_deltas()
        elif metric == 'vaccinated':
            self._compute_vaccinated()
        elif metric == 'deltas':
            self._compute_deltas()
        else:
            raise Exception("Invalid metric argument.")

    def _compute_vaccinated(self):
        """Computes metrics based on vaccinated people dataset for each health facility."""
        vaccinated = db.session.query(OckovaniLide.zarizeni_kod, func.coalesce(func.sum(OckovaniLide.pocet), 0).label('ockovani_pocet_davek')) \
            .group_by(OckovaniLide.zarizeni_kod) \
            .all()

        for vacc in vaccinated:
            db.session.merge(OckovaciMistoMetriky(
                zarizeni_id=vacc.zarizeni_kod,
                datum=self._date,
                ockovani_pocet_davek=vacc.ockovani_pocet_davek
            ))

        app.logger.info('Computing health facilities metrics - vaccinated people finished.')

    def _compute_deltas(self):
        """Computes deltas for previous metrics for each health facility."""
        db.session.execute(text(
            """
            update zarizeni_metriky t
            set ockovani_pocet_davek_zmena_den = t0.ockovani_pocet_davek - t1.ockovani_pocet_davek,
            from zarizeni_metriky t0 
            join zarizeni_metriky t1
            on t0.zarizeni_id = t1.zarizeni_id
            where t.zarizeni_id = t0.zarizeni_id and t.datum = :datum and t0.datum = :datum and t1.datum = :datum_1  
            """
        ), {'datum': self._date, 'datum_1': self._date - timedelta(1)})

        db.session.execute(text(
            """
            update zarizeni_metriky t
            set ockovani_pocet_davek_zmena_tyden = t0.ockovani_pocet_davek - t7.ockovani_pocet_davek,
            from zarizeni_metriky t0 
            join zarizeni_metriky t7
            on t0.zarizeni_id = t7.zarizeni_id
            where t.zarizeni_id = t0.zarizeni_id and t.datum = :datum and t0.datum = :datum and t7.datum = :datum_7  
            """
        ), {'datum': self._date, 'datum_7': self._date - timedelta(7)})

        app.logger.info('Computing health facilities metrics - deltas finished.')
