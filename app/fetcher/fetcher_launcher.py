import sys
import time
from datetime import date, datetime

from app import app, db
from app.fetcher.centers_fetcher import CentersFetcher
from app.fetcher.distributed_fetcher import DistributedFetcher
from app.fetcher.registrations_fetcher import RegistrationsFetcher
from app.fetcher.reservations_fetcher import ReservationsFetcher
from app.fetcher.used_fetcher import UsedFetcher
from app.fetcher.vaccinated_fetcher import VaccinatedFetcher
from app.fetcher.vaccinated_professions_fetcher import VaccinatedProfessionsFetcher
from app.models import Import


class FetcherLauncher:

    def __init__(self):
        self._fetchers = []
        self._import = None
        self._last_modified_date = None

    def fetch(self, dataset: str) -> bool:
        try:
            self._init_fetchers(dataset)
            self._check_modified_dates()
            self._init_import()
            self._fetch()
        except Exception as e:
            app.logger.error(e)
            self._set_import_failed()
            return False

        self._set_import_finished()
        return True

    def _init_fetchers(self, dataset: str) -> None:
        if dataset == 'all':
            self._fetchers.append(CentersFetcher())
            self._fetchers.append(DistributedFetcher())
            self._fetchers.append(UsedFetcher())
            self._fetchers.append(RegistrationsFetcher())
            self._fetchers.append(ReservationsFetcher())
            self._fetchers.append(VaccinatedFetcher())
            self._fetchers.append(VaccinatedProfessionsFetcher())
        elif dataset == 'centers':
            self._fetchers.append(CentersFetcher())
        elif dataset == 'distributed':
            self._fetchers.append(DistributedFetcher())
        elif dataset == 'used':
            self._fetchers.append(UsedFetcher())
        elif dataset == 'registrations':
            self._fetchers.append(RegistrationsFetcher())
        elif dataset == 'reservations':
            self._fetchers.append(ReservationsFetcher())
        elif dataset == 'vaccinated':
            self._fetchers.append(VaccinatedFetcher())
        elif dataset == 'vaccinated_professions':
            self._fetchers.append(VaccinatedProfessionsFetcher())

    def _check_modified_dates(self) -> None:
        modified_dates = []

        for fetcher in self._fetchers:
            modified_date = fetcher.get_modified_date()
            app.logger.info("Fetcher '{}' modified date: '{}'.".format(type(fetcher).__name__, modified_date))
            if modified_date.date() < date.today():
                raise Exception("Fetcher '{}' returned modified date older than today.", type(fetcher).__name__)

            modified_dates.append(modified_date)

        self._last_modified_date = max(modified_dates)

    def _fetch(self) -> None:
        for fetcher in self._fetchers:
            start = time.time()
            app.logger.info("Fetcher '{}' started.".format(type(fetcher).__name__))
            fetcher.fetch(self._import.id)
            app.logger.info("Fetcher '{}' finished in {:.1f} s.".format(type(fetcher).__name__, time.time() - start))

    def _init_import(self) -> None:
        self._import = Import(status='RUNNING')
        db.session.add(self._import)
        db.session.commit()

    def _set_import_failed(self) -> None:
        self._import.status = 'FAILED'
        self._import.end = datetime.now()
        db.session.commit()

    def _set_import_finished(self) -> None:
        # delete previous today's import if exists
        db.session.query(Import).filter(Import.date == self._last_modified_date.date()).delete()

        self._import.status = 'FINISHED'
        self._import.end = datetime.now()
        self._import.last_modified = self._last_modified_date
        self._import.date = self._last_modified_date.date()
        db.session.commit()


if __name__ == '__main__':
    fetcher = FetcherLauncher()
    fetcher.fetch(sys.argv[1])
