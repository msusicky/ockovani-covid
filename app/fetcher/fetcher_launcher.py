import sys
import time
from datetime import date, datetime

from app import app, db
from app.fetcher.centers_api_fetcher import CentersApiFetcher
from app.fetcher.centers_fetcher import CentersFetcher
from app.fetcher.deaths_fetcher import DeathsFetcher
from app.fetcher.deaths_vaccinated_fetcher import DeathsVaccinatedFetcher
from app.fetcher.distributed_fetcher import DistributedFetcher
from app.fetcher.fetcher import Fetcher
from app.fetcher.health_facilities_fetcher import HealthFacilitiesFetcher
from app.fetcher.hospitalized_icu_vaccinated_fetcher import HospitalizedIcuVaccinatedFetcher
from app.fetcher.hospitalized_vaccinated_fetcher import HospitalizedVaccinatedFetcher
from app.fetcher.infected_65_vaccinated_fetcher import Infected65VaccinatedFetcher
from app.fetcher.infected_fetcher import InfectedFetcher
from app.fetcher.infected_vaccinated_fetcher import InfectedVaccinatedFetcher
from app.fetcher.municipal_characteristics_fetcher import MunicipalCharacteristicsFetcher
from app.fetcher.opening_hours_fetcher import OpeningHoursFetcher
from app.fetcher.orp_situation_fetcher import OrpSituationFetcher
from app.fetcher.registrations_fetcher import RegistrationsFetcher
from app.fetcher.reservations_fetcher import ReservationsFetcher
from app.fetcher.reservations_api_fetcher import ReservationsApiFetcher
from app.fetcher.supplies_fetcher import SuppliesFetcher
from app.fetcher.used_fetcher import UsedFetcher
from app.fetcher.hospital_analysis_fetcher import HospitalAnalysisFetcher
from app.fetcher.vaccinated_fetcher import VaccinatedFetcher
from app.models import Import


class FetcherLauncher:

    ATTEMPTS_COUNT = 15
    ATTEMPTS_MIN_DURATION = 300 # 5 minutes

    def __init__(self):
        self._fetchers = []
        self._import = None
        self._last_modified = None
        self._historization_needed = False

    def fetch(self, dataset: str) -> bool:
        self._init_fetchers(dataset)
        self._historization_needed = self._is_historization_needed()
        self._init_import()

        try:
            for i in range(1, self.ATTEMPTS_COUNT + 1):
                app.logger.info(f'Attempt {i} started.')
                start = time.time()

                for f in self._fetchers:
                    if not f.finished and self._check_modified_time(f):
                        self._fetch(f)

                if self._all_finished():
                    app.logger.info(f'Attempt {i} finished - all fetchers finished.')
                    break
                elif i == self.ATTEMPTS_COUNT:
                    raise Exception('All attempts used, new data not available.')

                app.logger.info(f'Attempt {i} finished - some fetchers skipped.')
                self._wait(self.ATTEMPTS_MIN_DURATION - (time.time() - start))

        except Exception as e:
            app.logger.error(e)
            self._set_import_failed()
            return False

        self._set_import_finished()
        return True

    def _init_fetchers(self, dataset: str) -> None:
        if dataset == 'all':
            # self._fetchers.append(CentersFetcher()) - replaced by CentersApiFetcher
            self._fetchers.append(CentersApiFetcher())
            # self._fetchers.append(OpeningHoursFetcher())
            self._fetchers.append(HealthFacilitiesFetcher())
            self._fetchers.append(DistributedFetcher())
            self._fetchers.append(UsedFetcher())
            self._fetchers.append(RegistrationsFetcher())
            # self._fetchers.append(ReservationsFetcher()) - replaced by ReservationsApiFetcher
            self._fetchers.append(ReservationsApiFetcher())
            self._fetchers.append(VaccinatedFetcher())
            self._fetchers.append(InfectedFetcher())
            self._fetchers.append(DeathsFetcher())
            self._fetchers.append(MunicipalCharacteristicsFetcher())
            self._fetchers.append(OrpSituationFetcher())
            # self._fetchers.append(HospitalAnalysisFetcher()) - not needed
            # self._fetchers.append(SuppliesFetcher()) - data not updated anymore
            self._fetchers.append(InfectedVaccinatedFetcher())
            self._fetchers.append(Infected65VaccinatedFetcher())
            self._fetchers.append(DeathsVaccinatedFetcher())
            self._fetchers.append(HospitalizedVaccinatedFetcher())
            self._fetchers.append(HospitalizedIcuVaccinatedFetcher())
        elif dataset == 'centers':
            self._fetchers.append(CentersFetcher())
        elif dataset == 'centers_api':
            self._fetchers.append(CentersApiFetcher())
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
        elif dataset == 'reservations_api':
            self._fetchers.append(ReservationsApiFetcher())
        elif dataset == 'vaccinated':
            self._fetchers.append(VaccinatedFetcher())
        elif dataset == 'infected':
            self._fetchers.append(InfectedFetcher())
        elif dataset == 'deaths':
            self._fetchers.append(DeathsFetcher())
        elif dataset == 'municipal_characteristics':
            self._fetchers.append(MunicipalCharacteristicsFetcher())
        elif dataset == 'orp_situation':
            self._fetchers.append(OrpSituationFetcher())
        elif dataset == 'hospital_analysis':
            self._fetchers.append(HospitalAnalysisFetcher())
        elif dataset == 'supplies':
            self._fetchers.append(SuppliesFetcher())
        elif dataset == 'infected_vaccinated':
            self._fetchers.append(InfectedVaccinatedFetcher())
        elif dataset == 'infected_65_vaccinated':
            self._fetchers.append(Infected65VaccinatedFetcher())
        elif dataset == 'deaths_vaccinated':
            self._fetchers.append(DeathsVaccinatedFetcher())
        elif dataset == 'hospitalized_vaccinated':
            self._fetchers.append(HospitalizedVaccinatedFetcher())
        elif dataset == 'hospitalized_icu_vaccinated':
            self._fetchers.append(HospitalizedIcuVaccinatedFetcher())
        else:
            raise Exception('Invalid dataset argument.')

    def _is_historization_needed(self) -> bool:
        for f in self._fetchers:
            if f.historized:
                return True
        return False

    def _init_import(self) -> None:
        if self._historization_needed:
            # delete previous today's import if exists
            db.session.query(Import).filter(Import.date == date.today()).delete()

            self._import = Import(status='RUNNING')
            self._import.date = date.today()
            db.session.add(self._import)
            db.session.commit()

            app.logger.info(f'New import record with id {self._import.id} created.')

        else:
            app.logger.info(f'New import record not needed.')

    def _check_modified_time(self, fetcher: Fetcher) -> bool:
        modified_time = fetcher.get_modified_time()

        if modified_time.date() < date.today():
            app.logger.info(f"Fetcher '{type(fetcher).__name__}' modified time: '{modified_time}' - no new data.")
            return False

        app.logger.info(f"Fetcher '{type(fetcher).__name__}' modified time: '{modified_time}' - ok.")

        self._last_modified = modified_time \
            if self._last_modified is None or self._last_modified < modified_time \
            else self._last_modified

        return True

    def _fetch(self, fetcher: Fetcher) -> None:
        start = time.time()
        app.logger.info(f"Fetcher '{type(fetcher).__name__}' started.")
        fetcher.fetch(self._import.id if self._import.id else None)
        fetcher.finished = True
        app.logger.info(f"Fetcher '{type(fetcher).__name__}' finished in {(time.time() - start):.1f} s.")

    def _all_finished(self) -> bool:
        for f in self._fetchers:
            if not f.finished and f.check_date:
                return False
        return True

    def _wait(self, duration: time) -> None:
        if duration > 0:
            app.logger.info(f'Waiting {duration:.0f} s before the next attempt.')
            time.sleep(duration)

    def _set_import_failed(self) -> None:
        if self._historization_needed:
            self._import.status = 'FAILED'
            self._import.end = datetime.now()
            self._import.last_modified = self._last_modified
            db.session.commit()

    def _set_import_finished(self) -> None:
        if self._historization_needed:
            self._import.status = 'FINISHED'
            self._import.end = datetime.now()
            self._import.last_modified = self._last_modified
            db.session.commit()


if __name__ == '__main__':
    fetcher = FetcherLauncher()
    fetcher.fetch(sys.argv[1])
