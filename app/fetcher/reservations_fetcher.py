import pandas as pd

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto, OckovaniRezervace


class ReservationsFetcher(Fetcher):
    """
    Class for updating reservations table.
    """

    RESERVATIONS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-rezervace.csv'

    def __init__(self):
        super().__init__(OckovaniRezervace.__tablename__, self.RESERVATIONS_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df.drop(['ockovaci_misto_nazev', 'kraj_nuts_kod', 'kraj_nazev'], axis=1)

        df['import_id'] = import_id

        # filter out missing centers
        size = len(df)
        mista_ids = [r[0] for r in db.session.query(OckovaciMisto.id).all()]
        df = df[df['ockovaci_misto_id'].isin(mista_ids)]

        if size > len(df):
            app.logger.warn("Some centers doesn't exist - {} rows skipped.".format(size - len(df)))

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
