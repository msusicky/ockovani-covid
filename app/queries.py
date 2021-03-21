from datetime import date, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import func

from app import db
from app.context import get_import_date, get_import_id
from app.models import OckovaciMisto


def unique_nrpzs_subquery():
    return db.session.query(OckovaciMisto.nrpzs_kod) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.nrpzs_kod) \
        .having(func.count(OckovaciMisto.nrpzs_kod) == 1) \
        .subquery()


def count_vaccines_center(center_id):
    mista = pd.read_sql_query(
        """
        select ockovaci_mista.id ockovaci_misto_id, ockovaci_mista.nazev, okres_id, kraj_id 
        from ockovaci_mista join okresy on ockovaci_mista.okres_id=okresy.id
        where ockovaci_mista.id='{}';
        """.format(center_id),
        db.engine
    )

    prijato = pd.read_sql_query(
        """
        select ockovaci_misto_id, vyrobce, sum(pocet_davek) prijato
        from ockovani_distribuce 
        where akce = 'Příjem' and ockovaci_misto_id = '{}' and datum < '{}'
        group by (ockovaci_misto_id, vyrobce);
        """.format(center_id, get_import_date()),
        db.engine
    )

    prijato_odjinud = pd.read_sql_query(
        """
        select cilove_ockovaci_misto_id ockovaci_misto_id, vyrobce, sum(pocet_davek) prijato_odjinud
        from ockovani_distribuce 
        where akce = 'Výdej' and cilove_ockovaci_misto_id = '{}' and datum < '{}'
        group by (cilove_ockovaci_misto_id, vyrobce);
        """.format(center_id, get_import_date()),
        db.engine
    )

    vydano = pd.read_sql_query(
        """
        select ockovaci_misto_id, vyrobce, sum(pocet_davek) vydano
        from ockovani_distribuce 
        where akce = 'Výdej' and ockovaci_misto_id = '{}' and datum < '{}'  
        group by (ockovaci_misto_id, vyrobce);
        """.format(center_id, get_import_date()),
        db.engine
    )

    spotreba = pd.read_sql_query(
        """
        select ockovaci_misto_id, vyrobce, sum(pouzite_davky) pouzito, sum(znehodnocene_davky) znehodnoceno
        from ockovani_spotreba 
        where ockovaci_misto_id = '{}' and datum < '{}'
        group by (ockovaci_misto_id, vyrobce);
        """.format(center_id, get_import_date()),
        db.engine
    )

    vyrobci = pd.read_sql_query(
        """
        select distinct(vyrobce)
        from ockovani_distribuce;
        """,
        db.engine
    )

    mista_key = mista
    mista_key['join'] = 0
    vyrobci_key = vyrobci
    vyrobci_key['join'] = 0

    res = mista_key.merge(vyrobci_key).drop('join', axis=1)

    res = pd.merge(res, prijato, how="left")
    res = pd.merge(res, prijato_odjinud, how="left")
    res = pd.merge(res, vydano, how="left")
    res = pd.merge(res, spotreba, how="left")

    res['prijato'] = res['prijato'].fillna(0).astype('int')
    res['prijato_odjinud'] = res['prijato_odjinud'].fillna(0).astype('int')
    res['vydano'] = res['vydano'].fillna(0).astype('int')
    res['pouzito'] = res['pouzito'].fillna(0).astype('int')
    res['znehodnoceno'] = res['znehodnoceno'].fillna(0).astype('int')

    res['prijato_celkem'] = res['prijato'] + res['prijato_odjinud'] - res['vydano']
    res['skladem'] = res['prijato_celkem'] - res['pouzito'] - res['znehodnoceno']

    res = res.groupby(by=['vyrobce'], as_index=False).sum().sort_values(by=['vyrobce'])

    return res


def count_vaccines_kraj(kraj_id):
    mista = pd.read_sql_query(
        """
        select ockovaci_mista.id ockovaci_misto_id, ockovaci_mista.nazev, kraj_id 
        from ockovaci_mista join okresy on ockovaci_mista.okres_id=okresy.id
        where kraj_id='{}';
        """.format(kraj_id),
        db.engine
    )
    mista_ids = ','.join("'" + misto + "'" for misto in mista['ockovaci_misto_id'].tolist())

    prijato = pd.read_sql_query(
        """
        select ockovaci_misto_id, vyrobce, sum(pocet_davek) prijato
        from ockovani_distribuce 
        where akce = 'Příjem' and ockovaci_misto_id in ({}) and datum < '{}'
        group by (ockovaci_misto_id, vyrobce);
        """.format(mista_ids, get_import_date()),
        db.engine
    )

    prijato_odjinud = pd.read_sql_query(
        """
        select cilove_ockovaci_misto_id ockovaci_misto_id, vyrobce, sum(pocet_davek) prijato_odjinud
        from ockovani_distribuce 
        where akce = 'Výdej' and cilove_ockovaci_misto_id in ({}) and ockovaci_misto_id not in({}) and datum < '{}'
        group by (cilove_ockovaci_misto_id, vyrobce);
        """.format(mista_ids, mista_ids, get_import_date()),
        db.engine
    )

    vydano = pd.read_sql_query(
        """
        select ockovaci_misto_id, vyrobce, sum(pocet_davek) vydano
        from ockovani_distribuce 
        where akce = 'Výdej' and ockovaci_misto_id in ({}) and cilove_ockovaci_misto_id not in({}) and cilove_ockovaci_misto_id != '' and datum < '{}'  
        group by (ockovaci_misto_id, vyrobce);
        """.format(mista_ids, mista_ids, get_import_date()),
        db.engine
    )

    spotreba = pd.read_sql_query(
        """
        select ockovaci_misto_id, vyrobce, sum(znehodnocene_davky) znehodnoceno
        from ockovani_spotreba 
        where ockovaci_misto_id in ({}) and datum < '{}'
        group by (ockovaci_misto_id, vyrobce);
        """.format(mista_ids, get_import_date()),
        db.engine
    )

    ockovano = pd.read_sql_query(
        """
        select kraj_nuts_kod kraj_id, sum(pocet) ockovano,
            case 
                when vakcina = 'COVID-19 Vaccine AstraZeneca' then 'AstraZeneca'
                when vakcina = 'COVID-19 Vaccine Moderna' then 'Moderna'
                when vakcina = 'Comirnaty' then 'Pfizer'
            else 'ostatní' end vyrobce
        from ockovani_lide
        where kraj_nuts_kod = '{}' and datum < '{}'
        group by kraj_nuts_kod, vakcina
        """.format(kraj_id, get_import_date()),
        db.engine
    )

    vyrobci = pd.read_sql_query(
        """
        select distinct(vyrobce)
        from ockovani_distribuce;
        """,
        db.engine
    )

    mista_key = mista
    mista_key['join'] = 0
    vyrobci_key = vyrobci
    vyrobci_key['join'] = 0

    res = mista_key.merge(vyrobci_key).drop('join', axis=1)

    res = pd.merge(res, prijato, how="left")
    res = pd.merge(res, prijato_odjinud, how="left")
    res = pd.merge(res, vydano, how="left")
    res = pd.merge(res, spotreba, how="left")

    res['prijato'] = res['prijato'].fillna(0).astype('int')
    res['prijato_odjinud'] = res['prijato_odjinud'].fillna(0).astype('int')
    res['vydano'] = res['vydano'].fillna(0).astype('int')
    res['znehodnoceno'] = res['znehodnoceno'].fillna(0).astype('int')

    res = res.groupby(by=['kraj_id', 'vyrobce'], as_index=False).sum()

    res = pd.merge(res, ockovano, how="left")

    res['ockovano'] = res['ockovano'].fillna(0).astype('int')

    res['prijato_celkem'] = res['prijato'] + res['prijato_odjinud'] - res['vydano']
    res['skladem'] = res['prijato_celkem'] - res['ockovano'] - res['znehodnoceno']

    res = res.groupby(by=['vyrobce'], as_index=False).sum().sort_values(by=['vyrobce'])

    return res


def count_vaccines_cr():
    prijato = pd.read_sql_query(
        """
        select vyrobce, sum(pocet_davek) prijato
        from ockovani_distribuce
        where akce = 'Příjem' and datum < '{}'
        group by (vyrobce);
        """.format(get_import_date()),
        db.engine
    )

    spotreba = pd.read_sql_query(
        """
        select vyrobce, sum(znehodnocene_davky) znehodnoceno
        from ockovani_spotreba 
        where datum < '{}'
        group by (vyrobce);
        """.format(get_import_date()),
        db.engine
    )

    ockovano = pd.read_sql_query(
        """
        select sum(pocet) ockovano,
            case 
                when vakcina = 'COVID-19 Vaccine AstraZeneca' then 'AstraZeneca'
                when vakcina = 'COVID-19 Vaccine Moderna' then 'Moderna'
                when vakcina = 'Comirnaty' then 'Pfizer'
                else 'ostatní' end vyrobce
        from ockovani_lide
        where datum < '{}'
        group by vakcina
        """.format(get_import_date()),
        db.engine
    )

    res = pd.merge(prijato, spotreba, how="left")

    res['prijato'] = res['prijato'].fillna(0).astype('int')
    res['znehodnoceno'] = res['znehodnoceno'].fillna(0).astype('int')

    res = res.groupby(by=['vyrobce'], as_index=False).sum()

    res = pd.merge(res, ockovano, how="left")

    res['ockovano'] = res['ockovano'].fillna(0).astype('int')

    res['prijato_celkem'] = res['prijato']
    res['skladem'] = res['prijato_celkem'] - res['ockovano'] - res['znehodnoceno']

    res = res.groupby(by=['vyrobce'], as_index=False).sum().sort_values(by=['vyrobce'])

    return res


def count_registrations(filter_column, filter_value):
    mista = pd.read_sql_query(
        """
        select ockovaci_mista.id ockovaci_misto_id from ockovaci_mista join okresy on ockovaci_mista.okres_id=okresy.id
        where {}='{}';
        """.format(filter_column, filter_value),
        db.engine
    )
    mista_ids = ','.join("'" + misto + "'" for misto in mista['ockovaci_misto_id'].tolist())

    df = pd.read_sql_query(
        """
        select *
        from ockovani_registrace
        where import_id = {} and ockovaci_misto_id in({})
        """.format(get_import_id(), mista_ids),
        db.engine
    )

    df['dnes'] = get_import_date()
    df['datum_rezervace_fix'] = df['datum_rezervace'].where(df['datum_rezervace'] != date(1970, 1, 1))
    df['fronta_pocet'] = df[['pocet']].where(df['rezervace'] == False).fillna(0).astype('int')
    df['fronta_cekani'] = (df['dnes'] - df['datum']).astype('timedelta64[ns]').dt.days
    df['fronta_pocet_x_cekani'] = df['fronta_pocet'] * df['fronta_cekani']
    df['registrace_7'] = df[['pocet']].where(df['datum'] >= get_import_date() - timedelta(7))
    df['registrace_7_rez'] = df[['pocet']].where((df['rezervace'] == True) & (df['datum'] >= get_import_date() - timedelta(7)))
    # df['registrace_14'] = df[['pocet']].where(df['datum'] >= get_import_date() - timedelta(14))
    # df['registrace_14_rez'] = df[['pocet']].where((df['rezervace'] == True) & (df['datum'] >= get_import_date() - timedelta(14)))
    # df['registrace_30'] = df[['pocet']].where(df['datum'] >= get_import_date() - timedelta(30))
    # df['registrace_30_rez'] = df[['pocet']].where((df['rezervace'] == True) & (df['datum'] >= get_import_date() - timedelta(30)))
    df['rezervace_7_cekani'] = (df['datum_rezervace_fix'] - df['datum']).astype('timedelta64[ns]').dt.days
    df['rezervace_7_pocet'] = df[['pocet']].where((df['rezervace'] == True) & (df['datum_rezervace_fix'] >= get_import_date() - timedelta(7)))
    df['rezervace_7_pocet_x_cekani'] = df['rezervace_7_cekani'] * df['rezervace_7_pocet']

    df = df.groupby(['vekova_skupina', 'povolani']).sum()

    df['uspesnost_7'] = ((df['registrace_7_rez'] / df['registrace_7']) * 100).replace({np.nan: None})
    # df['uspesnost_14'] = ((df['registrace_14_rez'] / df['registrace_14']) * 100).replace({np.nan: None})
    # df['uspesnost_30'] = ((df['registrace_30_rez'] / df['registrace_30']) * 100).replace({np.nan: None})
    df['registrace_7'] = df['registrace_7'].astype('int')
    df['registrace_7_rez'] = df['registrace_7_rez'].astype('int')
    # df['registrace_14'] = df['registrace_14'].astype('int')
    # df['registrace_14_rez'] = df['registrace_14_rez'].astype('int')
    # df['registrace_30'] = df['registrace_30'].astype('int')
    # df['registrace_30_rez'] = df['registrace_30_rez'].astype('int')
    df['fronta_prumer_cekani'] = ((df['fronta_pocet_x_cekani'] / df['fronta_pocet']) / 7).replace({np.nan: None})
    df['rezervace_prumer_cekani'] = ((df['rezervace_7_pocet_x_cekani'] / df['rezervace_7_pocet']) / 7).replace({np.nan: None})

    return df.reset_index().sort_values(by=['vekova_skupina', 'povolani'])