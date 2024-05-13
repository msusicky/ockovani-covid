from datetime import date

from app import db, app
from app.context import get_import_date
from app.models import CrMetriky, Import


class Verifier:
    @staticmethod
    def verify_data():
        import_ = db.session.query(Import) \
            .filter(Import.date == date.today(), Import.status == 'FINISHED') \
            .one_or_none()

        if import_ is None:
            app.logger.error(f'No full data import found for today.')
            return False

        metrics = db.session.query(CrMetriky.registrace_celkem_zmena_den, CrMetriky.ockovani_pocet_davek_zmena_den) \
            .filter(CrMetriky.datum == get_import_date()) \
            .one_or_none()

        if metrics is None:
            app.logger.error(f'Metrics not found for today.')
            return False

        # if metrics.registrace_celkem_zmena_den is not None and metrics.registrace_celkem_zmena_den <= 0:
        #     app.logger.error(f'Verify data - failed - registrations count is lower or equal than yesterday ({metrics.registrace_celkem_zmena_den}).')
        #     return False

        if metrics.ockovani_pocet_davek_zmena_den is not None and metrics.ockovani_pocet_davek_zmena_den < 0:
            app.logger.error(f'Verify data - failed - vaccinated doses count is lower than yesterday ({metrics.ockovani_pocet_davek_zmena_den}).')
            return False

        app.logger.info('Verify data - successful.')
        return True
