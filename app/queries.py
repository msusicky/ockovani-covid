from datetime import date, timedelta, datetime

import numpy as np
import pandas as pd
from sqlalchemy import func, or_, and_, text

from app import db
from app.context import get_import_date, get_import_id
from app.models import OckovaciMisto, Okres, Kraj, OckovaciMistoMetriky, CrMetriky, OckovaniRegistrace, Populace, \
    PrakticiKapacity, OckovaciMistoDetail, OckovaniRezervace


def unique_nrpzs_subquery():
    """Returns unique NRPZS within all centers."""
    return db.session.query(OckovaciMisto.nrpzs_kod) \
        .group_by(OckovaciMisto.nrpzs_kod) \
        .having(func.count(OckovaciMisto.nrpzs_kod) == 1) \
        .subquery()


def unique_nrpzs_active_subquery():
    """Returns unique NRPZS within active centers."""
    return db.session.query(OckovaciMisto.nrpzs_kod) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.nrpzs_kod) \
        .having(func.count(OckovaciMisto.nrpzs_kod) == 1) \
        .subquery()


def has_unique_nrpzs(center_id):
    res = db.session.query(func.count(OckovaciMisto.id)) \
        .filter(OckovaciMisto.id == center_id)\
        .filter(or_(and_(OckovaciMisto.status == True, OckovaciMisto.nrpzs_kod.in_(unique_nrpzs_active_subquery())),
                    and_(OckovaciMisto.status == False, OckovaciMisto.nrpzs_kod.in_(unique_nrpzs_subquery())))) \
        .one()
    return res[0] == 1


def find_centers(filter_column, filter_value):
    centers = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, Okres.nazev.label("okres"),
                               Kraj.nazev.label("kraj"), OckovaciMisto.longitude, OckovaciMisto.latitude,
                               OckovaciMisto.adresa, OckovaciMisto.status, OckovaciMisto.bezbarierovy_pristup,
                               OckovaciMistoDetail.deti, OckovaciMistoDetail.typ,
                               OckovaciMistoMetriky.registrace_fronta, OckovaciMistoMetriky.registrace_prumer_cekani,
                               OckovaciMistoMetriky.ockovani_odhad_cekani,
                               OckovaciMistoMetriky.registrace_fronta_prumer_cekani,
                               OckovaciMistoMetriky.registrace_pred_zavorou) \
        .join(OckovaciMistoMetriky) \
        .join(OckovaciMistoDetail) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(filter_column == filter_value) \
        .filter(OckovaciMistoMetriky.datum == get_import_date()) \
        .filter(or_(OckovaciMisto.status == True, OckovaciMistoMetriky.registrace_fronta > 0,
                    OckovaciMistoMetriky.rezervace_cekajici > 0)) \
        .filter(OckovaciMistoDetail.typ != 'AČR') \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, Okres.id, Kraj.id, OckovaciMisto.longitude,
                  OckovaciMisto.latitude, OckovaciMisto.adresa, OckovaciMisto.status,
                  OckovaciMisto.bezbarierovy_pristup, OckovaciMistoDetail.deti, OckovaciMistoDetail.typ,
                  OckovaciMistoMetriky.registrace_fronta, OckovaciMistoMetriky.registrace_prumer_cekani,
                  OckovaciMistoMetriky.ockovani_odhad_cekani, OckovaciMistoMetriky.registrace_fronta_prumer_cekani,
                  OckovaciMistoMetriky.registrace_pred_zavorou) \
        .order_by(Kraj.nazev, Okres.nazev, OckovaciMisto.nazev) \
        .all()

    return centers


def find_third_doses_centers():
    center_ids = db.session.query(OckovaniRezervace.ockovaci_misto_id) \
        .distinct() \
        .filter(OckovaniRezervace.import_id == get_import_id()) \
        .filter(OckovaniRezervace.kalendar_ockovani == 'V3') \
        .all()

    return [center[0] for center in center_ids]


def find_free_vaccines_available():
    return db.session.query(PrakticiKapacity) \
        .filter(PrakticiKapacity.pocet_davek > 0) \
        .filter(or_(PrakticiKapacity.expirace == None, PrakticiKapacity.expirace >= datetime.today().date())) \
        .order_by(PrakticiKapacity.kraj, PrakticiKapacity.mesto, PrakticiKapacity.nazev_ordinace,
                  PrakticiKapacity.typ_vakciny) \
        .all()


def find_free_vaccines_vaccine_options():
    return db.session.query(PrakticiKapacity.typ_vakciny) \
        .filter(PrakticiKapacity.pocet_davek > 0) \
        .filter(or_(PrakticiKapacity.expirace == None, PrakticiKapacity.expirace >= datetime.today().date())) \
        .distinct(PrakticiKapacity.typ_vakciny) \
        .order_by(PrakticiKapacity.typ_vakciny) \
        .all()


def find_free_vaccines_kraj_options():
    return db.session.query(PrakticiKapacity.kraj) \
        .filter(PrakticiKapacity.pocet_davek > 0) \
        .filter(or_(PrakticiKapacity.expirace == None, PrakticiKapacity.expirace >= datetime.today().date())) \
        .distinct(PrakticiKapacity.kraj) \
        .order_by(PrakticiKapacity.kraj) \
        .all()


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

    vyrobci = pd.read_sql_query("select vyrobce from vakciny;", db.engine)

    mista_key = mista
    mista_key['join'] = 0
    vyrobci_key = vyrobci
    vyrobci_key['join'] = 0

    df = mista_key.merge(vyrobci_key).drop('join', axis=1)

    df = pd.merge(df, prijato, how="left")
    df = pd.merge(df, prijato_odjinud, how="left")
    df = pd.merge(df, vydano, how="left")
    df = pd.merge(df, spotreba, how="left")

    df['prijato'] = df['prijato'].fillna(0).astype('int')
    df['prijato_odjinud'] = df['prijato_odjinud'].fillna(0).astype('int')
    df['vydano'] = df['vydano'].fillna(0).astype('int')
    df['pouzito'] = df['pouzito'].fillna(0).astype('int')
    df['znehodnoceno'] = df['znehodnoceno'].fillna(0).astype('int')

    df['prijato_celkem'] = df['prijato'] + df['prijato_odjinud'] - df['vydano']
    df['skladem'] = df['prijato_celkem'] - df['pouzito'] - df['znehodnoceno']

    df = df.groupby(by=['vyrobce'], as_index=False).sum().sort_values(by=['vyrobce'])

    df = df[(df['prijato_celkem'] > 0) | (df['pouzito'] > 0) | (df['znehodnoceno'] > 0)]

    return df


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
        where akce = 'Výdej' and ockovaci_misto_id in ({}) and cilove_ockovaci_misto_id not in({}) and cilove_ockovaci_misto_id != '-' and datum < '{}'  
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
        select kraj_nuts_kod kraj_id, sum(pocet) ockovano, vyrobce
        from ockovani_lide
        join vakciny on vakciny.vakcina = ockovani_lide.vakcina
        where kraj_nuts_kod = '{}' and datum < '{}'
        group by kraj_nuts_kod, vyrobce
        """.format(kraj_id, get_import_date()),
        db.engine
    )

    vyrobci = pd.read_sql_query("select vyrobce from vakciny;", db.engine)

    mista_key = mista
    mista_key['join'] = 0
    vyrobci_key = vyrobci
    vyrobci_key['join'] = 0

    df = mista_key.merge(vyrobci_key).drop('join', axis=1)

    df = pd.merge(df, prijato, how="left")
    df = pd.merge(df, prijato_odjinud, how="left")
    df = pd.merge(df, vydano, how="left")
    df = pd.merge(df, spotreba, how="left")

    df['prijato'] = df['prijato'].fillna(0).astype('int')
    df['prijato_odjinud'] = df['prijato_odjinud'].fillna(0).astype('int')
    df['vydano'] = df['vydano'].fillna(0).astype('int')
    df['znehodnoceno'] = df['znehodnoceno'].fillna(0).astype('int')

    df = df.groupby(by=['kraj_id', 'vyrobce'], as_index=False).sum()

    df = pd.merge(df, ockovano, how="left")

    df['ockovano'] = df['ockovano'].fillna(0).astype('int')

    df['prijato_celkem'] = df['prijato'] + df['prijato_odjinud'] - df['vydano']
    df['skladem'] = df['prijato_celkem'] - df['ockovano'] - df['znehodnoceno']

    df = df.groupby(by=['vyrobce'], as_index=False).sum().sort_values(by=['vyrobce'])

    df = df[(df['prijato_celkem'] > 0) | (df['ockovano'] > 0) | (df['znehodnoceno'] > 0)]

    return df


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
        select sum(pocet) ockovano, vyrobce
        from ockovani_lide
        join vakciny on vakciny.vakcina = ockovani_lide.vakcina
        where datum < '{}'
        group by vyrobce
        """.format(get_import_date()),
        db.engine
    )

    vyrobci = pd.read_sql_query("select vyrobce from vakciny;", db.engine)

    df = pd.merge(vyrobci, prijato, how="left")
    df = pd.merge(df, spotreba, how="left")

    df['prijato'] = df['prijato'].fillna(0).astype('int')
    df['znehodnoceno'] = df['znehodnoceno'].fillna(0).astype('int')

    df = df.groupby(by=['vyrobce'], as_index=False).sum()

    df = pd.merge(df, ockovano, how="left")

    df['ockovano'] = df['ockovano'].fillna(0).astype('int')

    df['prijato_celkem'] = df['prijato']
    df['skladem'] = df['prijato_celkem'] - df['ockovano'] - df['znehodnoceno']

    df = df.groupby(by=['vyrobce'], as_index=False).sum().sort_values(by=['vyrobce'])

    df = df[(df['prijato_celkem'] > 0) | (df['ockovano'] > 0) | (df['znehodnoceno'] > 0)]

    return df


def count_registrations(filter_column, filter_value):
    mista = pd.read_sql_query(
        """
        select ockovaci_mista.id ockovaci_misto_id from ockovaci_mista join okresy on ockovaci_mista.okres_id=okresy.id
        where {}='{}';
        """.format(filter_column, filter_value),
        db.engine
    )
    mista_ids = ','.join("'" + misto + "'" for misto in mista['ockovaci_misto_id'].tolist())

    if len(mista_ids) == 0:
        return pd.DataFrame()

    df = pd.read_sql_query(
        """
        select *
        from ockovani_registrace
        where import_id = {} and ockovaci_misto_id in({})
        """.format(get_import_id(), mista_ids),
        db.engine
    )

    if df.empty:
        return df

    df['dnes'] = get_import_date()
    df['datum_rezervace_fix'] = df['datum_rezervace'].where(df['datum_rezervace'] != date(1970, 1, 1))
    df['fronta_pocet'] = df[['pocet']].where(df['rezervace'] == False).fillna(0).astype('int')
    df['fronta_cekani'] = (df['dnes'] - df['datum']).astype('timedelta64[ns]').dt.days
    df['fronta_pocet_x_cekani'] = df['fronta_pocet'] * df['fronta_cekani']
    df['s_terminem_pocet'] = df[['pocet']].where((df['rezervace'] == True) & (df['ockovani'] < 1)).fillna(0).astype('int')
    df['registrace_7'] = df[['pocet']].where(df['datum'] >= get_import_date() - timedelta(7))
    df['registrace_7_rez'] = df[['pocet']].where((df['rezervace'] == True) & (df['datum'] >= get_import_date() - timedelta(7)))
    # df['registrace_14'] = df[['pocet']].where(df['datum'] >= get_import_date() - timedelta(14))
    # df['registrace_14_rez'] = df[['pocet']].where((df['rezervace'] == True) & (df['datum'] >= get_import_date() - timedelta(14)))
    # df['registrace_30'] = df[['pocet']].where(df['datum'] >= get_import_date() - timedelta(30))
    # df['registrace_30_rez'] = df[['pocet']].where((df['rezervace'] == True) & (df['datum'] >= get_import_date() - timedelta(30)))
    df['rezervace_7_cekani'] = (df['datum_rezervace_fix'] - df['datum']).astype('timedelta64[ns]').dt.days
    df['rezervace_7_pocet'] = df[['pocet']].where((df['rezervace'] == True) & (df['datum_rezervace_fix'] >= get_import_date() - timedelta(7)))
    df['rezervace_7_pocet_x_cekani'] = df['rezervace_7_cekani'] * df['rezervace_7_pocet']
    df['rezervace_14_pocet'] = df[['pocet']].where((df['rezervace'] == True) & (df['datum_rezervace_fix'] >= get_import_date() - timedelta(14)))

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

    df = df[(df['fronta_pocet'] > 0) | df['fronta_prumer_cekani'].notnull() | df['rezervace_prumer_cekani'].notnull() | df['uspesnost_7'].notnull()]

    return df.reset_index().sort_values(by=['vekova_skupina', 'povolani'])


def count_vaccinated(kraj_id=None):
    ockovani = pd.read_sql_query(
        """
        select vekova_skupina, coalesce(sum(pocet) filter(where poradi_davky = 1), 0) pocet_ockovani_castecne, 
            coalesce(sum(pocet) filter(where poradi_davky = davky), 0) pocet_ockovani_plne, 
            coalesce(sum(pocet) filter(where poradi_davky = 3), 0) pocet_ockovani_posilujici
        from ockovani_lide o 
        join vakciny v on v.vakcina = o.vakcina
        where datum < '{}' and (kraj_bydl_nuts = '{}' or {})
        group by vekova_skupina
        order by vekova_skupina
        """.format(get_import_date(), kraj_id, kraj_id is None),
        db.engine
    )

    if kraj_id is not None:
        mista = pd.read_sql_query(
            """
            select ockovaci_mista.id ockovaci_misto_id from ockovaci_mista join okresy on ockovaci_mista.okres_id=okresy.id
            where kraj_id='{}';
            """.format(kraj_id),
            db.engine
        )
        mista_ids = ','.join("'" + misto + "'" for misto in mista['ockovaci_misto_id'].tolist())
    else:
        mista_ids = "''"

    registrace = pd.read_sql_query(
        """
        select vekova_skupina, sum(pocet) filter (where rezervace = false and ockovani < 1) pocet_fronta, 
            sum(pocet) filter (where rezervace = true and ockovani < 1) pocet_s_terminem
        from ockovani_registrace
        where import_id = {} and (ockovaci_misto_id in({}) or {}) 
        group by vekova_skupina
        """.format(get_import_id(), mista_ids, kraj_id is None),
        db.engine
    )

    populace = pd.read_sql_query(
        """
        select vekova_skupina, sum(pocet) pocet_vek, min_vek
        from populace p 
        join populace_kategorie k on (k.min_vek <= vek and k.max_vek >= vek)
        where orp_kod = '{}'
        group by vekova_skupina
        """.format('CZ0' if kraj_id is None else kraj_id),
        db.engine
    )

    ockovani['vekova_skupina'] = ockovani['vekova_skupina'].replace(['nezařazeno'], 'neuvedeno')

    merged = pd.merge(ockovani, registrace, how="left")
    merged = pd.merge(merged, populace, how="left")

    merged['pocet_fronta'] = merged['pocet_fronta'].fillna(0).astype('int')
    merged['pocet_s_terminem'] = merged['pocet_s_terminem'].fillna(0).astype('int')

    merged['podil_ockovani_castecne'] = (merged['pocet_ockovani_castecne'] / merged['pocet_vek']).fillna(0)
    merged['podil_ockovani_plne'] = (merged['pocet_ockovani_plne'] / merged['pocet_vek']).fillna(0)
    merged['podil_ockovani_posilujici'] = (merged['pocet_ockovani_posilujici'] / merged['pocet_vek']).fillna(0)

    merged['zajem'] = ((merged['pocet_fronta'] + merged['pocet_s_terminem'] + merged['pocet_ockovani_castecne'])
                       / merged['pocet_vek']).replace({np.nan: None})

    return merged


def count_vaccinated_category():
    df = pd.read_sql_query(
        """
        select indikace_zdravotnik, indikace_socialni_sluzby, indikace_ostatni, indikace_pedagog, 
            indikace_skolstvi_ostatni, indikace_bezpecnostni_infrastruktura, indikace_chronicke_onemocneni,
            coalesce(sum(pocet) filter(where poradi_davky = 1), 0) pocet_ockovani_castecne, 
            coalesce(sum(pocet) filter(where poradi_davky = davky), 0) pocet_ockovani_plne
        from ockovani_lide o
        join vakciny v on v.vakcina = o.vakcina
        group by indikace_zdravotnik, indikace_socialni_sluzby, indikace_ostatni, indikace_pedagog, 
            indikace_skolstvi_ostatni, indikace_bezpecnostni_infrastruktura, indikace_chronicke_onemocneni    
        """,
        db.engine
    )

    df['bez_indikace'] = ~(df['indikace_zdravotnik'] | df['indikace_socialni_sluzby'] | df['indikace_ostatni']
                           | df['indikace_pedagog'] | df['indikace_skolstvi_ostatni']
                           | df['indikace_bezpecnostni_infrastruktura'] | df['indikace_chronicke_onemocneni'])

    df = df.melt(id_vars=['pocet_ockovani_castecne', 'pocet_ockovani_plne'],
                 value_vars=['bez_indikace', 'indikace_zdravotnik', 'indikace_socialni_sluzby', 'indikace_ostatni',
                             'indikace_pedagog', 'indikace_skolstvi_ostatni', 'indikace_bezpecnostni_infrastruktura',
                             'indikace_chronicke_onemocneni'],
                 var_name='indikace', value_name='aktivni')

    df = df[df['aktivni'] == True].groupby(['indikace']).sum()

    labels = {
        'bez_indikace': ['bez indikace', ''],
        'indikace_zdravotnik': [
            'Zdravotník',
            '''Zdravotničtí pracovníci (zejména nemocnice, ZZS, primární ambulantní péče, farmaceuti, laboratoře 
            vyšetřující COVID-19, zdravotníci v sociálních službách), oblast ochrany veřejného zdraví.'''
        ],
        'indikace_socialni_sluzby': ['Sociální služby', 'Pracovníci nebo klienti v sociálních službách.'],
        'indikace_ostatni': [
            'Ostatní',
            '''Pracovníci kritické infrastruktury, kteří zahrnují integrovaný záchranný systém, pracovníky energetiky, 
            vládu a krizové štáby (osoba není začleněna v indikačních skupinách zdravotník nebo sociální služby).'''
        ],
        'indikace_pedagog': ['Pedagog', 'Pedagogičtí pracovníci.'],
        'indikace_skolstvi_ostatni': ['Školství ostatní', 'Ostatní pracovníci ve školství.'],
        'indikace_bezpecnostni_infrastruktura': [
            'Bezpečnostní infrastruktura',
            'Zaměstnanci Ministerstva obrany nebo bezpečnostní sbory.'
        ],
        'indikace_chronicke_onemocneni': [
            'Chronické onemocnění',
            '''Chronicky nemocní (hematoonkologické onemocnění, onkologické onemocnění (solidní nádory), závažné akutní 
            nebo dlouhodobé onemocnění srdce, závažné dlouhodobé onemocnění plic, diabetes mellitus, obezita, závažné 
            dlouhodobé onemocnění ledvin, závažné dlouhodobé onemocnění jater, stav po transplantaci nebo na čekací 
            listině, hypertenze, závažné neurologické nebo neuromuskulární onemocnění, vrozený nebo získaný kognitivní 
            deficit, vzácné genetické onemocnění, závažné oslabení imunitního systému, jiné závažné onemocnění).'''],
    }

    labels_df = pd.DataFrame.from_dict(labels, orient='index', columns=['kategorie', 'popis'])

    df = pd.merge(df, labels_df, how='outer', left_on='indikace', right_index=True)

    return df.dropna().sort_values(by=['pocet_ockovani_plne'], ascending=False)


def count_reservations_category():
    ockovani_skupiny = pd.read_sql_query(
        """
        select povolani kategorie, sum(case when rezervace is false and ockovani < 1 then pocet else 0 end) cekajici, 
            sum(case when rezervace is true and ockovani < 1 then pocet else 0 end) s_terminem,
			sum(case when ockovani = 1 then pocet else 0 end) ockovani, sum(pocet) celkem
            from ockovani_registrace where import_id={} group by povolani order by sum(pocet) desc
        """.format(get_import_id()),
        db.engine
    )
    return ockovani_skupiny


def count_vaccinated_doctors(kraj_id=None):
    ockovani_doktori = pd.read_sql_query(
        """
        select z.zarizeni_nazev, o.nazev okres, z.provoz_ukoncen, sum(pocet) as sum_1, 
            coalesce(sum(pocet) filter (where ol.datum+'7 days'::interval>='{}'), 0) as sum_2,
            string_agg(distinct v.vyrobce, ', ') filter (where ol.datum+'7 days'::interval>='{}') vakciny
        from ockovani_lide ol 
        left join ockovaci_zarizeni z on ol.zarizeni_kod = z.id
        left join okresy o on o.id = z.okres_id
        left join vakciny v on ol.vakcina = v.vakcina
        where prakticky_lekar = True and (kraj_nuts_kod='{}' or True={})
	    group by z.zarizeni_nazev, o.nazev, z.provoz_ukoncen
	    order by sum(pocet) desc
        """.format(get_import_date(), get_import_date(), kraj_id, kraj_id is None),
        db.engine
    )

    ockovani_doktori['okres'] = ockovani_doktori['okres'].replace({None: ''})
    ockovani_doktori['vakciny'] = ockovani_doktori['vakciny'].replace({None: ''})

    return ockovani_doktori


def count_supplies():
    df = pd.read_sql_query('select datum, vyrobce, pocet from dodavky_vakcin where pocet > 0', db.engine)
    df = df.pivot_table(values='pocet', index='datum', columns='vyrobce', aggfunc='sum')
    return df.fillna(0)


def count_end_date_category():
    df = pd.read_sql_query(
        """
        select vekova_skupina, min(datum) mesic from (
            select min(vekova_skupina) vekova_skupina, sum(pocet) * 0.7 populace
            from populace_kategorie
            join populace on vek >= min_vek and orp_kod = 'CZ0'
            where min_vek >= 18
            group by vekova_skupina
        ) t1
        join (
            select datum, sum(pocet) over (order by datum rows between unbounded preceding and current row) celkem 
            from (
                select datum, sum(pocet / davky) as pocet 
                from dodavky_vakcin d 
                join vakciny v on (d.vyrobce = v.vyrobce)
                group by datum
            ) t3
        ) t2
        on populace <= celkem
        group by vekova_skupina
        order by vekova_skupina
        """,
        db.engine
    )
    return df.set_index('mesic')


def count_end_date_vaccinated():
    metrics = db.session.query(CrMetriky.ockovani_pocet_castecne_zmena_tyden, CrMetriky.ockovani_pocet_castecne,
                               CrMetriky.ockovani_pocet_plne_zmena_tyden, CrMetriky.ockovani_pocet_plne,
                               CrMetriky.pocet_obyvatel_celkem) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one()

    if metrics is None or metrics.ockovani_pocet_castecne_zmena_tyden is None \
            or CrMetriky.ockovani_pocet_plne_zmena_tyden is None:
        return None

    population = metrics.pocet_obyvatel_celkem
    population_to_vaccinate = population * 0.7
    days = (7 * (2 * population_to_vaccinate - metrics.ockovani_pocet_castecne - metrics.ockovani_pocet_plne)) \
           / (metrics.ockovani_pocet_castecne_zmena_tyden + metrics.ockovani_pocet_plne_zmena_tyden)
    return get_import_date() + timedelta(days=days)


def count_end_date_supplies():
    metrics = db.session.query(CrMetriky.pocet_obyvatel_celkem) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one()

    if metrics is None:
        return None

    population_to_vaccinate = metrics.pocet_obyvatel_celkem * 0.7

    end_date = db.session.query("datum").from_statement(text(
        f"""
        select datum from (
            select datum, sum(pocet) over (order by datum rows between unbounded preceding and current row) as celkem_lidi 
            from (
                select datum, sum(pocet / davky) as pocet 
                from dodavky_vakcin d 
                join vakciny v on (d.vyrobce = v.vyrobce)
                group by datum
            ) t1
        ) t2
        where celkem_lidi > {population_to_vaccinate}
        order by datum
        limit 1
        """
    )).one_or_none()

    if end_date is None:
        return None

    months = ['ledna', 'února', 'března', 'dubna', 'května', 'června', 'července', 'srpna', 'září', 'října',
              'listopadu', 'prosince']

    return months[end_date[0].month - 1] + end_date[0].strftime(" %Y")


def couht_end_date_interested():
    metrics = db.session.query(CrMetriky.ockovani_pocet_castecne, CrMetriky.ockovani_pocet_plne,
                               CrMetriky.ockovani_pocet_davek_zmena_tyden) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one()

    if metrics is None or metrics.ockovani_pocet_davek_zmena_tyden is None:
        return None

    registrations_waiting = db.session.query(func.sum(OckovaniRegistrace.pocet)) \
        .filter(OckovaniRegistrace.ockovani < 1) \
        .filter(OckovaniRegistrace.import_id == get_import_id()) \
        .one()

    waiting_count = registrations_waiting[0] * 2 + metrics.ockovani_pocet_castecne - metrics.ockovani_pocet_plne

    days = (7 * waiting_count) / metrics.ockovani_pocet_davek_zmena_tyden

    return get_import_date() + timedelta(days=days)


def count_eligible():
    eligible_population = db.session.query(func.sum(Populace.pocet)) \
        .filter(Populace.vek >= 12) \
        .filter(Populace.orp_kod == "CZ0") \
        .one()

    return eligible_population[0]


def count_interest():
    metrics = db.session.query(CrMetriky.ockovani_pocet_castecne, CrMetriky.pocet_obyvatel_celkem) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one()

    registrations_waiting = db.session.query(func.sum(OckovaniRegistrace.pocet)) \
        .filter(OckovaniRegistrace.ockovani < 1) \
        .filter(OckovaniRegistrace.import_id == get_import_id()) \
        .one()

    interest_eligible = (metrics.ockovani_pocet_castecne + registrations_waiting[0]) / count_eligible()
    interest_all = (metrics.ockovani_pocet_castecne + registrations_waiting[0]) / metrics.pocet_obyvatel_celkem

    return interest_all, interest_eligible


def count_free_slots(center_id=None):
    rezervace_1 = pd.read_sql_query(
        """
        select datum, volna_kapacita volna_kapacita_1, maximalni_kapacita maximalni_kapacita_1
        from ockovani_rezervace  
        where ockovaci_misto_id = '{}' and import_id = {} and datum >= '{}' and kalendar_ockovani = 'V1' and maximalni_kapacita != 0
        order by datum
        """.format(center_id, get_import_id(), get_import_date()),
        db.engine
    )

    rezervace_3 = pd.read_sql_query(
        """
        select datum, volna_kapacita volna_kapacita_3, maximalni_kapacita maximalni_kapacita_3
        from ockovani_rezervace  
        where ockovaci_misto_id = '{}' and import_id = {} and datum >= '{}' and kalendar_ockovani = 'V3' and maximalni_kapacita != 0
        order by datum
        """.format(center_id, get_import_id(), get_import_date()),
        db.engine
    )

    if rezervace_1.empty and rezervace_3.empty:
        return rezervace_1
    elif rezervace_1.empty:
        rezervace = rezervace_3
    elif rezervace_3.empty:
        rezervace = rezervace_1
    else:
        rezervace = pd.merge(rezervace_1, rezervace_3, how='outer', on='datum')

    rezervace = rezervace.set_index('datum')

    idx = pd.date_range(rezervace.index.min(), rezervace.index.max())

    return rezervace.reindex(idx).fillna(0)


def count_vaccinated_week():
    return db.session.query('datum', 'pocet_1', 'pocet_2', 'pocet_3', 'pocet_celkem').from_statement(text(
        f"""
        select datum, 
            sum(case when poradi_davky = 1 then pocet else 0 end) pocet_1, 
            sum(case when poradi_davky = 2 then pocet else 0 end) pocet_2, 
            sum(case when poradi_davky = 3 then pocet else 0 end) pocet_3, 
            sum(pocet) pocet_celkem
        from ockovani_lide 
        where datum >= '{get_import_date() - timedelta(10)}'
        group by datum 
        order by datum 
        """
    )).all()


def count_top_centers():
    return db.session.query("zarizeni_nazev", "pocet").from_statement(text(
        f"""
        select zarizeni_nazev, sum(pocet) pocet
        from ockovani_lide 
        where datum >= '{get_import_date() - timedelta(7)}'
        group by zarizeni_nazev 
        order by pocet desc 
        limit 10;
        """
    )).all()


def couht_gp_vaccines():
    return db.session.query(func.sum(PrakticiKapacity.pocet_davek)).one()[0]


def count_vaccinated_unvaccinated_comparison():
    populace = pd.read_sql_query("select sum(pocet) populace from populace where orp_kod = 'CZ0'", db.engine)

    ockovani = pd.read_sql_query(
        f"""
        select datum, 
            sum(case when poradi_davky = 1 then pocet else 0 end) populace_ockovani, 
            sum(case when poradi_davky = v.davky then pocet else 0 end) populace_plne, 
            sum(case when poradi_davky = 3 then pocet else 0 end) populace_posilujici
        from ockovani_lide o
        join vakciny v on (o.vakcina = v.vakcina)
        where datum < '{get_import_date()}'
        group by datum
        order by datum
        """,
        db.engine
    )
    ockovani[['populace_ockovani', 'populace_plne', 'populace_posilujici']] = \
        ockovani[['populace_ockovani', 'populace_plne', 'populace_posilujici']].transform(pd.Series.cumsum)

    srovnani = pd.read_sql_query(
        f"""
        select n.datum, 
            n.celkem nakazeni_celkem, 
            n.bez_ockovani nakazeni_bez, n.bez_ockovani_vek_prumer nakazeni_bez_vek,
            n.nedokoncene_ockovani nakazeni_castecne, n.nedokoncene_ockovani_vek_prumer nakazeni_castecne_vek,
            n.dokoncene_ockovani nakazeni_plne, n.dokoncene_ockovani_vek_prumer nakazeni_plne_vek,
            n.posilujici_davka nakazeni_posilujici, n.posilujici_davka_vek_prumer nakazeni_posilujici_vek,
            h.celkem hospitalizace_celkem,
            h.bez_ockovani hospitalizace_bez, h.bez_ockovani_vek_prumer hospitalizace_bez_vek,
            h.nedokoncene_ockovani hospitalizace_castecne, h.nedokoncene_ockovani_vek_prumer hospitalizace_castecne_vek,
            h.dokoncene_ockovani hospitalizace_plne, h.dokoncene_ockovani_vek_prumer hospitalizace_plne_vek,
            h.posilujici_davka hospitalizace_posilujici, h.posilujici_davka_vek_prumer hospitalizace_posilujici_vek,
            j.celkem hospitalizace_jip_celkem,
            j.bez_ockovani hospitalizace_jip_bez, j.bez_ockovani_vek_prumer hospitalizace_jip_bez_vek, 
            j.nedokoncene_ockovani hospitalizace_jip_castecne, j.nedokoncene_ockovani_vek_prumer hospitalizace_jip_castecne_vek, 
            j.dokoncene_ockovani hospitalizace_jip_plne, j.dokoncene_ockovani_vek_prumer hospitalizace_jip_plne_vek,
            j.posilujici_davka hospitalizace_jip_posilujici, j.posilujici_davka_vek_prumer hospitalizace_jip_posilujici_vek, 
            u.celkem umrti_celkem,
            u.bez_ockovani umrti_bez, u.bez_ockovani_vek_prumer umrti_bez_vek, 
            u.nedokoncene_ockovani umrti_castecne, u.nedokoncene_ockovani_vek_prumer umrti_castecne_vek, 
            u.dokoncene_ockovani umrti_plne, u.dokoncene_ockovani_vek_prumer umrti_plne_vek,
            u.posilujici_davka umrti_posilujici, u.posilujici_davka_vek_prumer umrti_posilujici_vek 
        from nakazeni_ockovani n 
        join hospitalizace_ockovani h on h.datum = n.datum
        join hospitalizace_jip_ockovani j on j.datum = n.datum
        join umrti_ockovani u on u.datum = n.datum
        where n.datum < '{get_import_date()}'
        """,
        db.engine
    )

    ockovani['key'] = 0
    populace['key'] = 0
    df = pd.merge(ockovani, populace)
    df = df.drop(columns=['key'])
    df['populace_bez'] = df['populace'] - df['populace_ockovani']
    df['populace_castecne'] = df['populace_ockovani'] - df['populace_plne']
    df['populace_plne'] = df['populace_plne'] - df['populace_posilujici']
    df = pd.merge(df, srovnani)

    df_vek = df.copy()

    datasets = ['nakazeni', 'hospitalizace', 'hospitalizace_jip', 'umrti']
    groups = ['bez', 'castecne', 'plne', 'posilujici']

    for d in datasets:
        for g in groups:
            df_vek[d + '_' + g + '_mult'] = df_vek[d + '_' + g] * df_vek[d + '_' + g + '_vek']

    df_vek = df_vek.rolling(7, on='datum').sum()

    for d in datasets:
        for g in groups:
            df_vek[d + '_' + g + '_vek'] = df_vek[d + '_' + g + '_mult'] / df_vek[d + '_' + g]
            df_vek[d + '_' + g + '_vek'] = df_vek[d + '_' + g + '_vek'].replace({np.nan: None})

    for d in datasets:
        df_vek[d + '_celkem_vek'] = sum([df_vek[d + '_' + g + '_mult'] for g in groups]) / df_vek[d + '_celkem']
        df_vek[d + '_celkem_vek'] = df_vek[d + '_celkem_vek'].replace({np.nan: None})

    for g in groups:
        df_vek['populace_' + g + '_zastoupeni'] = df_vek['populace_' + g] / df_vek['populace']

    return df_vek


def get_registrations_graph_data(center_id=None):
    registrace = pd.read_sql_query(
        """
        select datum, sum(pocet) pocet_registrace
        from ockovani_registrace  
        where (ockovaci_misto_id = '{}' or {}) and import_id = {} and datum < '{}'
        group by datum
        """.format(center_id, center_id is None, get_import_id(), get_import_date()),
        db.engine
    )

    rezervace = pd.read_sql_query(
        """
        select datum_rezervace datum, sum(pocet) pocet_rezervace
        from ockovani_registrace  
        where (ockovaci_misto_id = '{}' or {}) and import_id = {} and rezervace = true and datum_rezervace < '{}'
        group by datum_rezervace
        """.format(center_id, center_id is None, get_import_id(), get_import_date()),
        db.engine
    )

    merged = pd.merge(registrace, rezervace, how='outer')

    if merged.empty:
        return merged

    merged = merged.set_index('datum')

    idx = pd.date_range(merged.index.min(), merged.index.max())

    return merged.reindex(idx).fillna(0)


def get_queue_graph_data(center_id=None, kraj_id=None):
    if center_id and kraj_id:
        return
    elif center_id:
        fronta = pd.read_sql_query(
            f"""
                select datum, registrace_fronta, rezervace_cekajici_1, rezervace_cekajici_2, rezervace_cekajici_3
                from ockovaci_mista_metriky
                where misto_id = '{center_id}'
            """,
            db.engine
        )
    elif kraj_id:
        fronta = pd.read_sql_query(
            f"""
                select datum, registrace_fronta, rezervace_cekajici_1, rezervace_cekajici_2, rezervace_cekajici_3
                from kraje_metriky
                where kraj_id = '{kraj_id}'
            """,
            db.engine
        )
    else:
        fronta = pd.read_sql_query(
            """
                select datum, registrace_fronta, rezervace_cekajici_1, rezervace_cekajici_2, rezervace_cekajici_3
                from cr_metriky
            """,
            db.engine
        )

    fronta = fronta.set_index('datum').fillna(0).sort_values('datum')

    for idx, row in fronta.iterrows():
        if row['registrace_fronta'] == 0 \
                and row['rezervace_cekajici_1'] == 0 \
                and row['rezervace_cekajici_2'] == 0 \
                and row['rezervace_cekajici_3'] == 0:
            fronta.drop(idx, inplace=True)
        else:
            break

    return fronta


def get_vaccination_graph_data(center_id):
    rezervace = pd.read_sql_query(
        """
        select datum, sum(maximalni_kapacita) kapacita, sum(maximalni_kapacita-volna_kapacita) rezervace,
            sum(maximalni_kapacita) filter(where kalendar_ockovani = 'V1') kapacita_1, 
            sum(maximalni_kapacita-volna_kapacita) filter(where kalendar_ockovani = 'V1') rezervace_1, 
            sum(maximalni_kapacita) filter(where kalendar_ockovani = 'V2') kapacita_2,
            sum(maximalni_kapacita-volna_kapacita) filter(where kalendar_ockovani = 'V2') rezervace_2,
            sum(maximalni_kapacita) filter(where kalendar_ockovani = 'V3') kapacita_3,
            sum(maximalni_kapacita-volna_kapacita) filter(where kalendar_ockovani = 'V3') rezervace_3
        from ockovani_rezervace  
        where ockovaci_misto_id = '{}' and import_id = {}
        group by datum
        """.format(center_id, get_import_id()),
        db.engine
    )

    spotreba = pd.read_sql_query(
        """
        select datum, sum(pouzite_davky) pouzite
        from ockovani_spotreba  
        where ockovaci_misto_id = '{}' 
        group by datum
        """.format(center_id),
        db.engine
    )

    merged = pd.merge(rezervace, spotreba, how='outer')

    if has_unique_nrpzs(center_id):
        ockovani = pd.read_sql_query(
            """
            select datum, sum(pocet) ockovane, sum(pocet) filter(where poradi_davky = 1) ockovane_1, 
                sum(pocet) filter(where poradi_davky = 2) ockovane_2,
                sum(pocet) filter(where poradi_davky = 3) ockovane_3
            from ockovani_lide o
            join ockovaci_mista m on m.nrpzs_kod = o.zarizeni_kod
            where m.id = '{}'
            group by datum
            """.format(center_id),
            db.engine
        )

        merged = pd.merge(merged, ockovani, how='outer')

    if merged.empty:
        return merged

    merged = merged.set_index('datum')

    idx = pd.date_range(merged.index.min(), merged.index.max())

    merged = merged.reindex(idx).fillna(0)

    merged['pouzite'] = np.where(merged.index.date < get_import_date(), merged['pouzite'], None)
    if 'ockovane' in merged:
        merged['ockovane'] = np.where(merged.index.date < get_import_date(), merged['ockovane'], None)
        merged['ockovane_1'] = np.where(merged.index.date < get_import_date(), merged['ockovane_1'], None)
        merged['ockovane_2'] = np.where(merged.index.date < get_import_date(), merged['ockovane_2'], None)
        merged['ockovane_3'] = np.where(merged.index.date < get_import_date(), merged['ockovane_3'], None)

    return merged


def get_vaccination_total_graph_data():
    ockovani = pd.read_sql_query(
        """
        select datum, sum(pocet) filter(where poradi_davky = 1) ockovani_castecne, 
            sum(pocet) filter(where poradi_davky = v.davky) ockovani_plne,
            sum(pocet) filter(where poradi_davky = 3) ockovani_3
        from ockovani_lide o 
        join vakciny v on v.vakcina = o.vakcina
        group by datum
        """,
         db.engine
    )

    return ockovani.set_index('datum').fillna(0).sort_values('datum').cumsum()


def get_received_vaccine_graph_data():
    return db.session.query("vyrobce", "datum", "prijem").from_statement(text(
        """
        select 
            vyrobce,
            array_agg(base.datum) as datum,
            array_agg(base.prijem) as prijem
        from (
            select 
                vyrobce,
                datum,
                sum(pocet_davek) as prijem
            from ockovani_distribuce
            where akce='Příjem'
            group by datum, vyrobce
            order by vyrobce, datum
        ) base
        group by vyrobce
        """
    )).all()


def get_used_vaccine_graph_data():
    return db.session.query("vyrobce", "datum", "ockovano").from_statement(text(
        """
        select vyrobce, array_agg(base.datum) as datum, array_agg(base.ockovano) as ockovano 
        from (
            select vyrobce, datum, sum(pocet) as ockovano
            from ockovani_lide
            join vakciny on vakciny.vakcina = ockovani_lide.vakcina
            group by vyrobce, datum
            order by vyrobce, datum
        ) base
        group by vyrobce
        """
    )).all()


def get_infected_graph_data():
    nakazeni = pd.read_sql_query(
        """
        select datum, vekova_skupina, sum(pocet) pocet_nakazeni
        from nakazeni  
        group by datum, vekova_skupina
        """,
        db.engine
    )

    populace = pd.read_sql_query(
        """
        select vekova_skupina, sum(pocet) pocet_vek
        from populace p 
        join populace_kategorie k on (k.min_vek <= vek and k.max_vek >= vek)
        where orp_kod = 'CZ0'
        group by vekova_skupina
        """,
        db.engine
    )

    df = pd.date_range(nakazeni['datum'].min(), nakazeni['datum'].max(), name='datum').to_frame().reset_index(drop=True)
    df['datum'] = df['datum'].dt.date
    df['join'] = 0

    populace['join'] = 0
    df = pd.merge(df, populace, how='outer')
    df = df.drop('join', axis=1)

    df = pd.merge(df, nakazeni, how='left')

    df = df.fillna(0)

    df['vekova_skupina_grp'] = np.select(
        [df['vekova_skupina'] == '80+',
         (df['vekova_skupina'] == '70-74') | (df['vekova_skupina'] == '75-79'),
         (df['vekova_skupina'] == '60-64') | (df['vekova_skupina'] == '65-69'),
         (df['vekova_skupina'] == '18-24') | (df['vekova_skupina'] == '25-29'),
         (df['vekova_skupina'] == '0-11') | (df['vekova_skupina'] == '12-15') | (df['vekova_skupina'] == '16-17')],
        ['80+', '70-79', '60-69', '18-29', '0-17'], default='ostatni')

    df = df.groupby(['vekova_skupina_grp', 'datum']).sum()
    df = df.rolling(7).sum()

    df = df[df.index.get_level_values(1) >= df.index.get_level_values(1).min() + timedelta(7)]

    df['pocet_nakazeni_norm'] = ((df['pocet_nakazeni'] / df['pocet_vek']) * 100000).round(1)

    return df


def get_infected_orp_graph_data():
    df = pd.read_sql_query(
        f"""
        select ruian_kod, ((100000.0 * aktivni_pripady) / pocet) nakazeni, aktivni_pripady, nazev_obce
        from charakteristika_obci n
        join obce_orp o on o.uzis_orp = n.orp_kod
        join populace_orp p on p.orp_kod = o.kod_obce_orp
        where datum = '{get_import_date()}'
        """,
        db.engine
    )

    df['ruian_kod'] = df['ruian_kod'].round(0).astype('str')

    return df


def get_vaccinated_orp_graph_data():
    df = pd.read_sql_query(
        f"""
        select ruian_kod, (100.0 * sum(l.pocet)) / min(p.pocet) ockovani, nazev_obce 
        from ockovani_lide l
        join obce_orp o on o.uzis_orp = l.orp_bydl_kod
        join populace_orp p on p.orp_kod = o.kod_obce_orp
        join vakciny v on v.vakcina = l.vakcina
        where poradi_davky = davky
        group by ruian_kod, nazev_obce
        """,
        db.engine
    )

    df['ruian_kod'] = df['ruian_kod'].round(0).astype('str')

    return df


def get_deaths_graph_data():
    umrti = pd.read_sql_query(
        """
        select datum, vekova_skupina, sum(pocet) pocet_umrti
        from umrti  
        group by datum, vekova_skupina
        """,
        db.engine
    )

    populace = pd.read_sql_query(
        """
        select vekova_skupina, sum(pocet) pocet_vek
        from populace p 
        join populace_kategorie k on (k.min_vek <= vek and k.max_vek >= vek)
        where orp_kod = 'CZ0'
        group by vekova_skupina
        """,
        db.engine
    )

    df = pd.date_range(umrti['datum'].min(), umrti['datum'].max(), name='datum').to_frame().reset_index(drop=True)
    df['datum'] = df['datum'].dt.date
    df['join'] = 0

    populace['join'] = 0
    df = pd.merge(df, populace, how='outer')
    df = df.drop('join', axis=1)

    df = pd.merge(df, umrti, how='left')

    df = df.fillna(0)

    df['vekova_skupina_grp'] = np.select(
        [df['vekova_skupina'] == '80+',
         (df['vekova_skupina'] == '70-74') | (df['vekova_skupina'] == '75-79'),
         (df['vekova_skupina'] == '60-64') | (df['vekova_skupina'] == '65-69')],
        ['80+', '70-79', '60-69'], default='ostatni')

    df = df.groupby(['vekova_skupina_grp', 'datum']).sum()
    df = df.rolling(7).sum()

    df = df[df.index.get_level_values(1) >= df.index.get_level_values(1).min() + timedelta(7)]

    df['pocet_umrti_norm'] = ((df['pocet_umrti'] / df['pocet_vek']) * 100000).round(2)

    return df


def get_hospitalized_orp_graph_data():
    df = pd.read_sql_query(
        f"""
        select ruian_kod, ((100000.0 * pocet_hosp) / pocet) hospitalizovani, pocet_hosp, nazev_obce
        from situace_orp s
        join obce_orp o on o.uzis_orp = s.orp_kod
        join populace_orp p on p.orp_kod = o.kod_obce_orp
        where datum = '{get_import_date()}'
        """,
        db.engine
    )

    df['ruian_kod'] = df['ruian_kod'].round(0).astype('str')

    return df


def get_tests_orp_graph_data():
    df = pd.read_sql_query(
        f"""
        select ruian_kod, case when testy_7 > 0 then (100.0 * nove_pripady_7_dni) / testy_7 else 0 end pozitivita, testy_7, nazev_obce
        from situace_orp s
        join charakteristika_obci c on (c.datum = s.datum and c.orp_kod = s.orp_kod) 
        join obce_orp o on o.uzis_orp = s.orp_kod
        where s.datum = '{get_import_date()}'
        """,
        db.engine
    )

    df['ruian_kod'] = df['ruian_kod'].round(0).astype('str')

    return df


def get_vaccinated_unvaccinated_comparison_graph_data():
    populace = pd.read_sql_query("select sum(pocet) populace from populace where orp_kod = 'CZ0' group by vekova_skupina", db.engine)

    ockovani = pd.read_sql_query(
        f"""
        select datum, 
            sum(case when poradi_davky = 1 then pocet else 0 end) populace_ockovani, 
            sum(case when poradi_davky = v.davky then pocet else 0 end) populace_plne, 
            sum(case when poradi_davky = 3 then pocet else 0 end) populace_posilujici
        from ockovani_lide o
        join vakciny v on (o.vakcina = v.vakcina)
        where datum < '{get_import_date()}'
        group by datum, vekova_skupina
        order by datum
        """,
        db.engine
    )
    ockovani[['populace_ockovani', 'populace_plne', 'populace_posilujici']] = \
        ockovani[['populace_ockovani', 'populace_plne', 'populace_posilujici']].group.transform(pd.Series.cumsum)

    srovnani = pd.read_sql_query(
        f"""
        select * from srovnani_ockovani s 
        where n.datum < '{get_import_date()}'
        """,
        db.engine
    )

    df = pd.merge(ockovani, populace)
    df = df.drop(columns=['key'])
    df['populace_bez'] = df['populace'] - df['populace_ockovani']
    df['populace_castecne'] = df['populace_ockovani'] - df['populace_plne']
    df['populace_plne'] = df['populace_plne'] - df['populace_posilujici']
    df = pd.merge(df, srovnani)

    df_vek = df.copy()

    datasets = ['nakazeni', 'hospitalizace', 'hospitalizace_jip', 'umrti']
    groups = ['bez', 'castecne', 'plne', 'posilujici']

    for d in datasets:
        for g in groups:
            df_vek[d + '_' + g + '_mult'] = df_vek[d + '_' + g] * df_vek[d + '_' + g + '_vek']

    df_vek = df_vek.rolling(7, on='datum').sum()

    for d in datasets:
        for g in groups:
            df_vek[d + '_' + g + '_vek'] = df_vek[d + '_' + g + '_mult'] / df_vek[d + '_' + g]
            df_vek[d + '_' + g + '_vek'] = df_vek[d + '_' + g + '_vek'].replace({np.nan: None})

    for d in datasets:
        df_vek[d + '_celkem_vek'] = sum([df_vek[d + '_' + g + '_mult'] for g in groups]) / df_vek[d + '_celkem']
        df_vek[d + '_celkem_vek'] = df_vek[d + '_celkem_vek'].replace({np.nan: None})

    for g in groups:
        df_vek['populace_' + g + '_zastoupeni'] = df_vek['populace_' + g] / df_vek['populace']

    return df_vek