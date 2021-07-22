from datetime import datetime
from typing import Optional

import pandas as pd

from app import db
from app.fetcher.fetcher import Fetcher
from app.models import DodavkaVakcin


class SuppliesFetcher(Fetcher):
    """
    Class for updating vaccines supplies table.
    """

    SUPPLIES_CSV = 'https://docs.google.com/spreadsheets/d/1pGOSkXgtTkaTbAMsvgO_3FAvHX-Z7rJrvRtNm8wOviQ/export?format=csv&id=1pGOSkXgtTkaTbAMsvgO_3FAvHX-Z7rJrvRtNm8wOviQ&gid=0'

    def __init__(self):
        super().__init__(DodavkaVakcin.__tablename__, self.SUPPLIES_CSV, check_date=False)

    def get_modified_date(self) -> Optional[datetime]:
        return None

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df = df[['Měsíc', 'Pfizer', 'Moderna', 'AZ', 'CureVac', 'Janssen', 'Novavax', 'GSK']]
        df = df.dropna(subset=['Měsíc'])

        df['Měsíc'] = df['Měsíc'].replace({'/1/': '/'}, regex=True)
        df['datum'] = pd.to_datetime(df['Měsíc'], format='%m/%Y')
        df = df.drop('Měsíc', axis=1)

        df = df.rename(columns={'AZ': 'AstraZeneca'})

        df['Pfizer'] = df['Pfizer'].replace({',': ''}, regex=True).astype('int')
        df['Moderna'] = df['Moderna'].replace({',': ''}, regex=True).astype('int')
        df['AstraZeneca'] = df['AstraZeneca'].replace({',': ''}, regex=True).astype('int')
        df['CureVac'] = df['CureVac'].replace({',': ''}, regex=True).astype('int')
        df['Janssen'] = df['Janssen'].replace({',': ''}, regex=True).astype('int')
        df['Novavax'] = df['Novavax'].replace({',': ''}, regex=True).astype('int')
        df['GSK'] = df['GSK'].replace({',': ''}, regex=True).astype('int')

        df = df.melt(id_vars=['datum'],
                     value_vars=['Pfizer', 'Moderna', 'AstraZeneca', 'CureVac', 'Janssen', 'Novavax', 'GSK'],
                     var_name='vyrobce', value_name='pocet')

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
