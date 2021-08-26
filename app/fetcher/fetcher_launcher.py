import sys
import time
from datetime import date, datetime

from app import app, db
from app.fetcher.centers_detail_fetcher import CentersDetailFetcher
from app.fetcher.centers_fetcher import CentersFetcher
from app.fetcher.deaths_fetcher import DeathsFetcher
from app.fetcher.distributed_fetcher import DistributedFetcher
from app.fetcher.health_facilities_fetcher import HealthFacilitiesFetcher
from app.fetcher.infected_fetcher import InfectedFetcher
from app.fetcher.opening_hours_fetcher import OpeningHoursFetcher
from app.fetcher.registrations_fetcher import RegistrationsFetcher
from app.fetcher.reservations_fetcher import ReservationsFetcher
from app.fetcher.supplies_fetcher import SuppliesFetcher
from app.fetcher.used_fetcher import UsedFetcher
from app.fetcher.hospital_analysis_fetcher import HospitalAnalysisFetcher
from app.fetcher.vaccinated_fetcher import VaccinatedFetcher
from app.models import Import


class FetcherLauncher:

    ATTEMPTS = 10

    def __init__(self):
        self._fetchers = []
        self._import = None
        self._last_modified_date = None

    def fetch(self, dataset: str) -> bool:
        try:
            self._init_fetchers(dataset)

            for i in range(1, self.ATTEMPTS + 1):
                try:
                    self._check_modified_dates()
                    break
                except OldDataException as e:
                    if i < self.ATTEMPTS:
                        app.logger.info(
                            f'New data not available yet. Attempt {i}/{self.ATTEMPTS} failed, waiting 10 minutes...'
                        )
                        time.sleep(60)
                        for j in range(9, 0, -1):
                            app.logger.info(f'Waiting for new data, {j} minutes left...')
                            time.sleep(60)
                    else:
                        raise e

            self._init_import()

        except Exception as e:
            app.logger.error(e)
            return False

        try:
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
            self._fetchers.append(CentersDetailFetcher())
            # self._fetchers.append(OpeningHoursFetcher())
            self._fetchers.append(HealthFacilitiesFetcher())
            self._fetchers.append(DistributedFetcher())
            self._fetchers.append(UsedFetcher())
            self._fetchers.append(RegistrationsFetcher())
            self._fetchers.append(ReservationsFetcher())
            self._fetchers.append(VaccinatedFetcher())
            self._fetchers.append(InfectedFetcher())
            self._fetchers.append(DeathsFetcher())
            # self._fetchers.append(HospitalAnalysisFetcher())
            # self._fetchers.append(SuppliesFetcher())
        elif dataset == 'centers':
            self._fetchers.append(CentersFetcher())
        elif dataset == 'centers_detail':
            self._fetchers.append(CentersDetailFetcher())
        elif dataset == 'opening_hours':
            self._fetchers.append(OpeningHoursFetcher())
        elif dataset == 'health_facilities':
            self._fetchers.append(HealthFacilitiesFetcher())
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
        elif dataset == 'infected':
            self._fetchers.append(InfectedFetcher())
        elif dataset == 'deaths':
            self._fetchers.append(DeathsFetcher())
        elif dataset == 'hospital_analysis':
            self._fetchers.append(HospitalAnalysisFetcher())
        elif dataset == 'supplies':
            self._fetchers.append(SuppliesFetcher())
        else:
            raise Exception('Invalid dataset argument.')

    def _check_modified_dates(self) -> None:
        modified_dates = []

        for fetcher in self._fetchers:
            try:
                modified_date = fetcher.get_modified_date()
                app.logger.info(f"Fetcher '{type(fetcher).__name__}' modified date: '{modified_date}'.")

                if fetcher.check_date and (modified_date is None or modified_date.date() < date.today()):
                    raise OldDataException(f"Fetcher '{type(fetcher).__name__}' returned modified date older than today.")

                if modified_date is not None:
                    modified_dates.append(modified_date)

            except Exception as e:
                if fetcher.ignore_errors:
                    app.logger.warning(f"Ignoring error: '{e}'")
                else:
                    raise e

        self._last_modified_date = max(modified_dates)

    def _fetch(self) -> None:
        for fetcher in self._fetchers:
            start = time.time()
            app.logger.info(f"Fetcher '{type(fetcher).__name__}' started.")

            try:
                fetcher.fetch(self._import.id)
                app.logger.info(f"Fetcher '{type(fetcher).__name__}' finished in {(time.time() - start):.1f} s.")
            except Exception as e:
                if fetcher.ignore_errors:
                    app.logger.warning(f"Ignoring error: '{e}'")
                else:
                    raise e

    def _init_import(self) -> None:
        # delete previous today's import if exists
        db.session.query(Import).filter(Import.date == self._last_modified_date.date()).delete()

        self._import = Import(status='RUNNING')
        self._import.last_modified = self._last_modified_date
        self._import.date = self._last_modified_date.date()
        db.session.add(self._import)
        db.session.commit()

    def _set_import_failed(self) -> None:
        self._import.status = 'FAILED'
        self._import.end = datetime.now()
        db.session.commit()

    def _set_import_finished(self) -> None:
        self._import.status = 'FINISHED'
        self._import.end = datetime.now()
        db.session.commit()


class OldDataException(Exception):
    pass


if __name__ == '__main__':
    fetcher = FetcherLauncher()
    fetcher.fetch(sys.argv[1])
