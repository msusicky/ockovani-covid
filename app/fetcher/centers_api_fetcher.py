import os
from datetime import datetime
from typing import Optional

import numpy as np
import requests
from pandas import DataFrame

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto


class CentersApiFetcher(Fetcher):
    """
    Class for updating vaccination centers and vaccination centers detail table.
    """

    API_URL = 'https://cfa.uzis.cz/api/v1/'
    CENTERS_LIST = 'vaccination-center/'

    def __init__(self):
        super().__init__(OckovaciMisto.__tablename__, self.API_URL + self.CENTERS_LIST)

    def get_modified_time(self) -> Optional[datetime]:
        return datetime.today()

    def fetch(self, import_id: int) -> None:
        user = os.environ.get('CFA_USER')
        password = os.environ.get('CFA_PASS')

        r = requests.get(self._url, auth=(user, password))
        df = DataFrame(r.json()['results'])

        df['district_nuts4_code'] = df['district_nuts4_code'].replace({'': None})
        df['latitude'] = df['latitude'].replace({np.nan: None})
        df['longitude'] = df['longitude'].replace({np.nan: None})
        df['min_vaccination_capacity'] = df['min_vaccination_capacity'].replace({np.nan: None})
        df['code'] = df['code'].str.zfill(11)

        # set all centers disabled to disable centers removed from the list
        db.session.query(OckovaciMisto).update({OckovaciMisto.status: False})

        for idx, row in df.iterrows():
            id = row['id']

            vakciny = [vaccine['name'] for vaccine in row['vaccine_type']]

            vekove_skupiny = []
            if row['children']:
                vekove_skupiny.append('děti')
            if row['vaccionation_group_16']:
                vekove_skupiny.append('16-17')
            if row['vaccionation_group_18']:
                vekove_skupiny.append('18-29')
            if row['vaccionation_group_30']:
                vekove_skupiny.append('30-39')
            if row['vaccionation_group_40']:
                vekove_skupiny.append('40-49')
            if row['vaccionation_group_50']:
                vekove_skupiny.append('50-59')
            if row['vaccionation_group_60']:
                vekove_skupiny.append('60-69')
            if row['vaccionation_group_70']:
                vekove_skupiny.append('70-79')
            if row['vaccionation_group_80']:
                vekove_skupiny.append('80+')

            db.session.merge(OckovaciMisto(
                id=id,
                nazev=row['name'],
                okres_id=row['district_nuts4_code'],
                status=row['operational_status'],
                adresa=row['address'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                nrpzs_kod=row['code'],
                minimalni_kapacita=row['min_vaccination_capacity'],
                bezbarierovy_pristup=row['wheelchair_access'],
                typ=row['center_type_name'],
                vekove_skupiny=vekove_skupiny,
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
                presun_2davky_poznamka=row['v2_term_change_comment'],
                davky=row['vaccine_round']
            ))

        db.session.commit()
