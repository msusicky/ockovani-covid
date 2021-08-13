import pandas as pd
import requests
import os

from app import db, app
from app.fetcher.fetcher import Fetcher
from app.models import OckovaciMisto, OckovaniRegistrace


class RegistrationsFetcher(Fetcher):
    """
    Class for updating registrations table.
    """

    REGISTRATIONS_CSV = 'https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/ockovani-registrace.csv'

    def __init__(self):
        url = os.environ.get('ODL_REGISTRACE_ENH')
        super().__init__(OckovaniRegistrace.__tablename__,
                         url if url is not None and requests.head(
                             url).status_code == 200 else self.REGISTRATIONS_CSV)

    def fetch(self, import_id: int) -> None:
        usecols = ['datum', 'ockovaci_misto_id', 'vekova_skupina', 'povolani', 'stat', 'rezervace', 'datum_rezervace',
                   'zavora_status', 'zablokovano', 'duvod_blokace']

        df = pd.read_csv(self._url, usecols=lambda c: c in usecols)

        app.logger.info("Download of the registration dataset finished.")

        # fitler out canceled registrations
        df = df.loc[(df['zablokovano'].isna()) | (df['duvod_blokace'] == 'Ztotožněn, ale již vakcinován')]
        df = df.loc[((df['duvod_blokace'] != 'Ztotožněn, ale již vakcinován') & (df['rezervace'].isna())) | (df['rezervace'] == 1)]

        df['ockovani'] = df['duvod_blokace'].apply(lambda val: 1 if val == 'Ztotožněn, ale již vakcinován' else 0)
        df['za_zavorou'] = df['zavora_status'].apply(lambda val: True if val == 'za závorou' else False)

        df['rezervace'] = df['rezervace'].fillna(False).astype('bool')
        df['vekova_skupina'] = df['vekova_skupina'].fillna('neuvedeno')
        df['stat'] = df['stat'].fillna('neuvedeno')
        df['datum_rezervace'] = df['datum_rezervace'].fillna('1970-01-01')

        # Replace - error caused by NAKIT 11.6.2021 - #471
        df['povolani'] = df['povolani'].replace(
            ['OccupationGroupChronic2Name',
             'OccupationGroupAcademicStaffName',
             'OccupationGroupArmyName',
             'OccupationGroupChronicName',
             'OccupationGroupMedicalWorkerName',
             'OccupationGroupCriticalInfrastructureName',
             'OccupationGroupAgeName',
             'OccupationGroupTHPWorkersName',
             'OccupationGroupSelfPayerName',
             'OccupationGroupSocialWorkerName',
             'OccupationGroupNonMedicalStaffName',
             'OccupationGroupCaringPersonName',
             'OccupationGroupTeacher'],
            ['Osoba s chronickým onemocněním – druhá skupina',
             'Akademický pracovník VŠ',
             'Zaměstnanci Ministerstva obrany',
             'Osoba s chronickým onemocněním',
             'Zdravotnický pracovník dle §76 a §77 zákona 372/2011  Sb.',
             'Kritická infrastruktura',
             'Na základě dosaženého věku',
             'Technicko hospodářští pracovníci ve zdravotnických zařízeních',
             'Samoplátce',
             'Pracovník v sociálních službách',
             'Nezdravotničtí pracovníci podílející se na poskytování zdravotní péče a péče o covid-19 pozitivní osoby',
             'Osoba pečující o osobu v III. nebo IV. stupni závislosti',
             'Pedagogický pracovník/nepedagogický zaměstnanec']
            )
        df['povolani'] = df['povolani'].fillna('neuvedeno')

        df = df[['datum', 'ockovaci_misto_id', 'vekova_skupina', 'povolani', 'stat', 'rezervace', 'datum_rezervace',
                 'ockovani', 'za_zavorou']]

        df = df.groupby(df.columns.tolist(), dropna=False).size().reset_index(name='pocet')

        df['import_id'] = import_id

        # filter out missing centers
        size = len(df)
        mista_ids = [r[0] for r in db.session.query(OckovaciMisto.id).all()]
        df = df[df['ockovaci_misto_id'].isin(mista_ids)]

        if size > len(df):
            app.logger.warn("Some centers doesn't exist - {} rows skipped.".format(size - len(df)))

        df.to_sql(self._table, db.engine, if_exists='append', index=False, method=Fetcher._psql_insert_copy)
