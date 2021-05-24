from app import db, app
from app.context import get_import_date
from app.models import CrMetriky


class Verifier:
    @staticmethod
    def verify_data():
        metrics = db.session.query(CrMetriky.registrace_celkem_zmena_den, CrMetriky.ockovani_pocet_davek_zmena_den) \
            .filter(CrMetriky.datum == get_import_date()) \
            .one()

        if metrics.registrace_celkem_zmena_den is not None and metrics.registrace_celkem_zmena_den <= 0:
            app.logger.error('Verify data - failed - registrations count is lower or equal than yesterday.')
            return False

        if metrics.ockovani_pocet_davek_zmena_den is not None and metrics.ockovani_pocet_davek_zmena_den <= 0:
            app.logger.error('Verify data - failed - vaccinated doses count is lower or equal than yesterday.')
            return False

        app.logger.info('Verify data - successful.')
        return True
