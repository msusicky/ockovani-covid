import pandas as pd

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto, OckovaniRegistrace


class RegistrationsFetcher(Fetcher):
    """
    Class for updating registrations table.
    """

    REGISTRATIONS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-registrace.csv'

    def __init__(self):
        super().__init__(OckovaniRegistrace.__tablename__, self.REGISTRATIONS_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df.drop(['ockovaci_misto_nazev', 'kraj_nuts_kod', 'kraj_nazev'], axis=1)

        df['rezervace'] = df['rezervace'].fillna(False).astype('bool')
        df['datum_rezervace'] = df['datum_rezervace'].fillna('1970-01-01')

        df = df.groupby(df.columns.tolist(), dropna=False).size().reset_index(name='pocet')

        df['import_id'] = import_id

        # filter out missing centers
        size = len(df)
        mista_ids = [r[0] for r in db.session.query(OckovaciMisto.id).all()]
        df = df[df['ockovaci_misto_id'].isin(mista_ids)]

        if size > len(df):
            app.logger.warn("Some centers doesn't exist - {} rows skipped.".format(size - len(df)))

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
