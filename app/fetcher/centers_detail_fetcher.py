import os
from datetime import datetime
from typing import Optional

import requests
from pandas import DataFrame

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto, OckovaciMistoDetail


class CentersDetailFetcher(Fetcher):
    """
    Class for updating vaccination centers detail table.
    """

    API_URL = 'https://cfa.uzis.cz/api/v1/'
    CENTERS_LIST = 'vaccination-center/'

    def __init__(self):
        super().__init__(OckovaciMistoDetail.__tablename__, self.API_URL + self.CENTERS_LIST, check_date=False)

    def get_modified_date(self) -> Optional[datetime]:
        return datetime.today()

    def fetch(self, import_id: int) -> None:
        user = os.environ.get('CFA_USER')
        password = os.environ.get('CFA_PASS')

        r = requests.get(self._url, auth=(user, password))
        df = DataFrame(r.json()['results'])

        # filter out missing centers
        size = len(df)
        mista_ids = [r[0] for r in db.session.query(OckovaciMisto.id).all()]
        df = df[df['id'].isin(mista_ids)]

        if size > len(df):
            app.logger.warning("Some centers doesn't exist - {} rows skipped.".format(size - len(df)))

        for idx, row in df.iterrows():
            vakciny = [vaccine['name'] for vaccine in row['vaccine_type']]

            db.session.merge(OckovaciMistoDetail(
                ockovaci_misto_id=row['id'],
                typ=row['center_type_name'],
                deti=row['children'],
                drive_in=row['drive_in'],
                upresneni_polohy=row['location_additional_info'],
                platba_karta=row['card_payment'],
                platba_hotovost=row['cash_payment'],
                telefon=row['contact_phone_number'],
                email=row['email_1'],
                odkaz=row['url_link'],
                poznamka=row['comment'],
                verejna_poznamka=row['public_comment'],
                vakciny=vakciny,
                presun_2davky_nepovolen=row['v2_term_change_not_supported'],
                presun_2davky_linka=row['v2_term_change_1221'],
                presun_2davky_centrum=row['v2_term_change_vaccination_center'],
                presun_2davky_telefon=row['v2_term_change_vaccination_center_phone'],
                presun_2davky_email=row['v2_term_change_vaccination_center_email'],
                presun_2davky_online=row['v2_term_change_online_request'],
                presun_2davky_poznamka=row['v2_term_change_comment']
            ))

        db.session.commit()
