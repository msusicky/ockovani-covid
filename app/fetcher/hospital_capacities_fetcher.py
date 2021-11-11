import pandas as pd

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import OckovaniSpotreba, OckovaciMisto, KapacityNemocnic


class HospitalCapacitiesFetcher(Fetcher):
    """
    Class for updating capacities in hospitals.
    """

    USED_CSV = 'https://dip.mzcr.cz/api/v1/kapacity-intenzivni-pece-zdravotnicke-zarizeni-10-2021.csv'

    def __init__(self):
        super().__init__(KapacityNemocnic.__tablename__, self.USED_CSV)

    def fetch(self, import_id: int) -> None:
        df = pd.read_csv(self._url)

        df['luzka_standard_kyslik_kapacita_volna_covid_pozitivni'] = df[
            'luzka_standard_kyslik_kapacita_volna_covid_pozitivni'].fillna('0').astype('int')
        df['luzka_standard_kyslik_kapacita_volna_covid_negativni'] = df[
            'luzka_standard_kyslik_kapacita_volna_covid_negativni'].fillna('0').astype('int')
        df['luzka_standard_kyslik_kapacita_celkem'] = df[
            'luzka_standard_kyslik_kapacita_celkem'].fillna('0').astype('int')
        df['luzka_hfno_cpap_kapacita_volna_covid_pozitivni'] = df[
            'luzka_hfno_cpap_kapacita_volna_covid_pozitivni'].fillna('0').astype('int')
        df['luzka_hfno_cpap_kapacita_volna_covid_negativni'] = df[
            'luzka_hfno_cpap_kapacita_volna_covid_negativni'].fillna('0').astype('int')
        df['luzka_hfno_cpap_kapacita_celkem'] = df[
            'luzka_hfno_cpap_kapacita_celkem'].fillna('0').astype('int')
        df['luzka_upv_niv_kapacita_volna_covid_pozitivni'] = df[
            'luzka_upv_niv_kapacita_volna_covid_pozitivni'].fillna('0').astype('int')
        df['luzka_upv_niv_kapacita_volna_covid_negativni'] = df[
            'luzka_upv_niv_kapacita_volna_covid_negativni'].fillna('0').astype('int')
        df['luzka_upv_niv_kapacita_celkem'] = df[
            'luzka_upv_niv_kapacita_celkem'].fillna('0').astype('int')
        df['inf_luzka_kyslik_kapacita_volna_covid_pozitivni'] = df[
            'inf_luzka_kyslik_kapacita_volna_covid_pozitivni'].fillna('0').astype('int')
        df['inf_luzka_kyslik_kapacita_volna_covid_negativni'] = df[
            'inf_luzka_kyslik_kapacita_volna_covid_negativni'].fillna('0').astype('int')
        df['inf_luzka_kyslik_kapacita_celkem'] = df[
            'inf_luzka_kyslik_kapacita_celkem'].fillna('0').astype('int')
        df['inf_luzka_hfno_kapacita_volna_covid_pozitivni'] = df[
            'inf_luzka_hfno_kapacita_volna_covid_pozitivni'].fillna('0').astype('int')
        df['inf_luzka_hfno_kapacita_volna_covid_negativni'] = df[
            'inf_luzka_hfno_kapacita_volna_covid_negativni'].fillna('0').astype('int')
        df['inf_luzka_hfno_kapacita_celkem'] = df[
            'inf_luzka_hfno_kapacita_celkem'].fillna('0').astype('int')
        df['inf_luzka_upv_kapacita_volna_covid_pozitivni'] = df[
            'inf_luzka_upv_kapacita_volna_covid_pozitivni'].fillna('0').astype('int')
        df['inf_luzka_upv_kapacita_volna_covid_negativni'] = df[
            'inf_luzka_upv_kapacita_volna_covid_negativni'].fillna('0').astype('int')
        df['inf_luzka_upv_kapacita_celkem'] = df[
            'inf_luzka_upv_kapacita_celkem'].fillna('0').astype('int')
        df['ventilatory_operacni_sal_kapacita_volna'] = df[
            'ventilatory_operacni_sal_kapacita_volna'].fillna('0').astype('int')
        df['ventilatory_operacni_sal_kapacita_celkem'] = df[
            'ventilatory_operacni_sal_kapacita_celkem'].fillna('0').astype('int')
        df['ecmo_kapacita_volna'] = df[
            'ecmo_kapacita_volna'].fillna('0').astype('int')
        df['ecmo_kapacita_celkem'] = df[
            'ecmo_kapacita_celkem'].fillna('0').astype('int')
        df['cvvhd_kapacita_volna'] = df[
            'cvvhd_kapacita_volna'].fillna('0').astype('int')
        df['cvvhd_kapacita_celkem'] = df[
            'cvvhd_kapacita_celkem'].fillna('0').astype('int')
        df['ventilatory_prenosne_kapacita_volna'] = df[
            'ventilatory_prenosne_kapacita_volna'].fillna('0').astype('int')
        df['ventilatory_prenosne_kapacita_celkem'] = df[
            'ventilatory_prenosne_kapacita_celkem'].fillna('0').astype('int')

        df = df.drop('kraj_nazev', axis=1)

        self._truncate()

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
