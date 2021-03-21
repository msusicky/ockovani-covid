from datetime import date

from app import db, app
from app.context import STATUS_FINISHED
from app.etl.center_metrics_etl import CenterMetricsEtl
from app.etl.cr_metrics_etl import CrMetricsEtl
from app.etl.kraj_metrics_etl import KrajMetricsEtl
from app.etl.okres_metrics_etl import OkresMetricsEtl
from app.models import Import


class MetricsEtl:
    """Base class for computing metrics."""

    def __init__(self, date_):
        self._date = date_
        self._import_id = self._find_import_id()

        self._center_metrics_etl = CenterMetricsEtl(self._date, self._import_id)
        self._okres_metrics_etl = OkresMetricsEtl(self._date, self._import_id)
        self._kraj_metrics_etl = KrajMetricsEtl(self._date, self._import_id)
        self._cr_metrics_etl = CrMetricsEtl(self._date, self._import_id)

    def compute_all(self):
        try:
            self._center_metrics_etl.compute_all()
            self._okres_metrics_etl.compute_all()
            self._kraj_metrics_etl.compute_all()
            self._cr_metrics_etl.compute_all()
        except Exception as e:
            app.logger.error(e)
            db.session.rollback()
            return False

        db.session.commit()
        return True

    def _find_import_id(self):
        id_ = db.session.query(Import.id) \
            .filter(Import.date == self._date, Import.status == STATUS_FINISHED) \
            .first()

        if id_ is None:
            raise Exception("No data for date: '{0}'.".format(self._date))

        return id_[0]


if __name__ == '__main__':
    etl = MetricsEtl(date.today())
    etl.compute_all()