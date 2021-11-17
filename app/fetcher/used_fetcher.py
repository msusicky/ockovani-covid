import pandas as pd

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import OckovaniSpotreba, OckovaciMisto


class UsedFetcher(Fetcher):
    """
    Class for updating used vaccines table.
    """

    USED_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-spotreba.csv'

    def __init__(self):
        super().__init__(OckovaniSpotreba.__tablename__, self.USED_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df.rename(columns={'ockovaci_misto_kod': 'ockovaci_misto_id'})

        df['kraj_nuts_kod'] = df['kraj_nuts_kod'].fillna('-')

        df['pouzite_davky'] = df['pouzite_davky'].fillna(0).astype('int')
        df['znehodnocene_davky'] = df['znehodnocene_davky'].fillna(0).astype('int')

        df = df.groupby(['datum', 'ockovaci_misto_id', 'ockovaci_latka', 'vyrobce'], dropna=False).sum().reset_index()

        # filter out missing centers
        size = len(df)
        mista_ids = [r[0] for r in db.session.query(OckovaciMisto.id).all()]
        df = df[df['ockovaci_misto_id'].isin(mista_ids)]

        if size > len(df):
            app.logger.warning("Some centers doesn't exist - {} rows skipped.".format(size - len(df)))

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
