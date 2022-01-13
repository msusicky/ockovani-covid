from datetime import date, timedelta, datetime

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from sqlalchemy import func, or_, and_, text, column

from app import db
from app.context import get_import_date, get_import_id
from app.models import OckovaciMisto, Okres, Kraj, OckovaciMistoMetriky, CrMetriky, OckovaniRegistrace, Populace, \
    PrakticiKapacity, OckovaniRezervace, Vakcina, ZdravotnickeStredisko


def unique_nrpzs_subquery():
    """Returns unique NRPZS within all centers."""
    return db.session.query(OckovaciMisto.nrpzs_kod) \
        .group_by(OckovaciMisto.nrpzs_kod) \
        .having(func.count(OckovaciMisto.nrpzs_kod) == 1)


def unique_nrpzs_active_subquery():
    """Returns unique NRPZS within active centers."""
    return db.session.query(OckovaciMisto.nrpzs_kod) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.nrpzs_kod) \
        .having(func.count(OckovaciMisto.nrpzs_kod) == 1)


def has_unique_nrpzs(center_id):
    res = db.session.query(func.count(OckovaciMisto.id)) \
        .filter(OckovaciMisto.id == center_id) \
        .filter(or_(and_(OckovaciMisto.status == True, OckovaciMisto.nrpzs_kod.in_(unique_nrpzs_active_subquery())),
                    and_(OckovaciMisto.status == False, OckovaciMisto.nrpzs_kod.in_(unique_nrpzs_subquery())))) \
        .one()
    return res[0] == 1


def find_kraj_options():
    return db.session.query(Kraj.nazev, Kraj.id).order_by(Kraj.nazev).all()


def find_centers(filter_column, filter_value):
    centers = db.session.query(OckovaciMisto.id, OckovaciMisto.nazev, Okres.nazev.label("okres"),
                               Kraj.nazev_kratky.label("kraj"), Kraj.id.label("kraj_id"), OckovaciMisto.longitude,
                               OckovaciMisto.latitude, OckovaciMisto.adresa, OckovaciMisto.status,
                               OckovaciMisto.bezbarierovy_pristup, OckovaciMisto.vekove_skupiny, OckovaciMisto.typ,
                               OckovaciMisto.davky, OckovaciMisto.vakciny,
                               OckovaciMistoMetriky.registrace_fronta, OckovaciMistoMetriky.registrace_prumer_cekani,
                               OckovaciMistoMetriky.ockovani_odhad_cekani,
                               OckovaciMistoMetriky.registrace_fronta_prumer_cekani,
                               OckovaciMistoMetriky.registrace_pred_zavorou) \
        .join(OckovaciMistoMetriky) \
        .outerjoin(Okres, OckovaciMisto.okres_id == Okres.id) \
        .outerjoin(Kraj, Okres.kraj_id == Kraj.id) \
        .filter(filter_column == filter_value) \
        .filter(OckovaciMistoMetriky.datum == get_import_date()) \
        .filter(or_(OckovaciMisto.status == True, OckovaciMistoMetriky.registrace_fronta > 0,
                    OckovaciMistoMetriky.rezervace_cekajici > 0, OckovaciMisto.typ == 'WALKIN')) \
        .filter(OckovaciMisto.typ != 'AČR') \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, Okres.id, Kraj.id, OckovaciMisto.longitude,
                  OckovaciMisto.latitude, OckovaciMisto.adresa, OckovaciMisto.status,
                  OckovaciMisto.bezbarierovy_pristup, OckovaciMisto.vekove_skupiny, OckovaciMisto.typ,
                  OckovaciMisto.davky, OckovaciMisto.vakciny, OckovaciMistoMetriky.registrace_fronta,
                  OckovaciMistoMetriky.registrace_prumer_cekani, OckovaciMistoMetriky.ockovani_odhad_cekani,
                  OckovaciMistoMetriky.registrace_fronta_prumer_cekani, OckovaciMistoMetriky.registrace_pred_zavorou) \
        .order_by(Kraj.nazev_kratky, Okres.nazev, OckovaciMisto.nazev) \
        .all()

    return centers


def find_third_doses_centers():
    center_ids = db.session.query(OckovaniRezervace.ockovaci_misto_id) \
        .distinct() \
        .filter(OckovaniRezervace.kalendar_ockovani == 'V3') \
        .all()

    return [center[0] for center in center_ids]


def find_centers_vaccine_options():
    return db.session.query(func.unnest(OckovaciMisto.vakciny).label('vyrobce')).order_by('vyrobce').distinct().all()


def find_doctor_offices(nrpzs_kod):
    df = pd.read_sql_query(
        f"""
        select coalesce(z.zarizeni_nazev, min(s.nazev_cely)) zarizeni_nazev, o.nazev okres, k.nazev kraj, 
            k.nazev_kratky kraj_kratky, s.druh_zarizeni, s.obec, s.psc, s.ulice, s.cislo_domu, s.telefon, s.email, 
            s.web, s.latitude, s.longitude
        from ockovaci_zarizeni z
        full join zdravotnicke_stredisko s on s.nrpzs_kod = z.id
        left join okresy o on o.id = coalesce(z.okres_id, s.okres_kod)
        join kraje k on k.id = o.kraj_id
        where z.id = '{nrpzs_kod}' or s.nrpzs_kod = '{nrpzs_kod}'
        group by z.zarizeni_nazev, o.nazev, k.nazev, k.nazev_kratky, s.druh_zarizeni, s.obec, s.psc, s.ulice, 
            s.cislo_domu, s.telefon, s.email, s.web, s.latitude, s.longitude
        """,
        db.engine)

    return df


NRPZS_PEDIATRICIAN_CODE = 321


def find_doctors(okres_id=None, kraj_id=None):
    okres_id_sql = 'null' if okres_id is None else f"'{okres_id}'"
    kraj_id_sql = 'null' if kraj_id is None else f"'{kraj_id}'"

    df = pd.read_sql_query(
        f"""
        select z.id, z.zarizeni_nazev, o.nazev okres, o.kraj_id, k.nazev kraj, k.nazev_kratky kraj_kratky, 
            z.provoz_ukoncen, m.ockovani_pocet_davek, m.ockovani_pocet_davek_zmena_tyden, m.ockovani_vakciny_7,
            count(n.nrpzs_kod) nabidky, 
            case when s.druh_zarizeni_kod = {NRPZS_PEDIATRICIAN_CODE} then true else false end pediatr
        from ockovaci_zarizeni z
        left join zdravotnicke_stredisko s on s.nrpzs_kod = z.id
        left join okresy o on o.id = z.okres_id
        join kraje k on k.id = o.kraj_id
        left join zarizeni_metriky m on m.zarizeni_id = z.id and m.datum = '{get_import_date()}'
        left join (
            select left(zdravotnicke_zarizeni_kod, 11) nrpzs_kod 
            from praktici_kapacity n 
            where n.pocet_davek > 0 and (n.expirace is null or n.expirace >= '{get_import_date()}')
        ) n on n.nrpzs_kod = z.id 
        where prakticky_lekar = True 
            and (z.okres_id = {okres_id_sql} or {okres_id_sql} is null) 
            and (o.kraj_id = {kraj_id_sql} or {kraj_id_sql} is null)
        group by z.id, z.zarizeni_nazev, o.nazev, o.kraj_id, k.nazev, k.nazev_kratky, z.provoz_ukoncen, 
            m.ockovani_pocet_davek, m.ockovani_pocet_davek_zmena_tyden, m.ockovani_vakciny_7, pediatr
        order by k.nazev_kratky, o.nazev, z.zarizeni_nazev
        """,
        db.engine
    )

    df['ockovani_vakciny_7'] = df['ockovani_vakciny_7'].replace({None: ''})

    df['provoz_ukoncen'] = df['provoz_ukoncen'].astype('bool')

    df['ockovani_pocet_davek'] = df['ockovani_pocet_davek'].replace({np.nan: 0})
    df['ockovani_pocet_davek_zmena_tyden'] = df['ockovani_pocet_davek_zmena_tyden'].replace({np.nan: 0})

    return df


def find_doctors_map():
    df = pd.read_sql_query(
        f"""
        select z.id, z.zarizeni_nazev, z.provoz_ukoncen, s.latitude, s.longitude, m.ockovani_pocet_davek, 
            m.ockovani_pocet_davek_zmena_tyden, m.ockovani_vakciny_7, count(n.nrpzs_kod) nabidky, 
            case when s.druh_zarizeni_kod = {NRPZS_PEDIATRICIAN_CODE} then true else false end pediatr
        from ockovaci_zarizeni z
        left join zdravotnicke_stredisko s on s.nrpzs_kod = z.id
        left join zarizeni_metriky m on m.zarizeni_id = z.id and m.datum = '{get_import_date()}'
        left join (
            select left(zdravotnicke_zarizeni_kod, 11) nrpzs_kod 
            from praktici_kapacity n 
            where n.pocet_davek > 0 and (n.expirace is null or n.expirace >= '{get_import_date()}')
        ) n on n.nrpzs_kod = z.id 
        where prakticky_lekar = True 
        group by z.id, z.zarizeni_nazev, z.provoz_ukoncen, s.latitude, s.longitude, m.ockovani_pocet_davek, 
            m.ockovani_pocet_davek_zmena_tyden, m.ockovani_vakciny_7, pediatr
        """,
        db.engine
    )

    df['ockovani_vakciny_7'] = df['ockovani_vakciny_7'].replace({None: ''})

    df['provoz_ukoncen'] = df['provoz_ukoncen'].astype('bool')

    df['latitude'] = df['latitude'].replace({np.nan: None})
    df['longitude'] = df['longitude'].replace({np.nan: None})

    df['ockovani_pocet_davek'] = df['ockovani_pocet_davek'].replace({np.nan: 0})
    df['ockovani_pocet_davek_zmena_tyden'] = df['ockovani_pocet_davek_zmena_tyden'].replace({np.nan: 0})

    return df


def find_doctors_vaccine_options():
    return db.session.query(Vakcina.vyrobce) \
        .filter(Vakcina.aktivni == True) \
        .order_by(Vakcina.vyrobce) \
        .all()


def find_free_vaccines_available(nrpzs_kod=None, okres_id=None, kraj_id=None):
    return db.session.query(PrakticiKapacity.datum_aktualizace, PrakticiKapacity.pocet_davek,
                            PrakticiKapacity.typ_vakciny, PrakticiKapacity.mesto, PrakticiKapacity.nazev_ordinace,
                            PrakticiKapacity.deti, PrakticiKapacity.dospeli, PrakticiKapacity.kontakt_tel,
                            PrakticiKapacity.kontakt_email, PrakticiKapacity.expirace, PrakticiKapacity.poznamka,
                            PrakticiKapacity.kraj, ZdravotnickeStredisko.nrpzs_kod, ZdravotnickeStredisko.latitude,
                            ZdravotnickeStredisko.longitude) \
        .outerjoin(ZdravotnickeStredisko, ZdravotnickeStredisko.zdravotnicke_zarizeni_kod == PrakticiKapacity.zdravotnicke_zarizeni_kod) \
        .filter(or_(func.left(PrakticiKapacity.zdravotnicke_zarizeni_kod, 11) == nrpzs_kod, nrpzs_kod is None)) \
        .filter(or_(ZdravotnickeStredisko.okres_kod == okres_id, okres_id is None)) \
        .filter(or_(ZdravotnickeStredisko.kraj_kod == kraj_id, kraj_id is None)) \
        .filter(PrakticiKapacity.pocet_davek > 0) \
        .filter(or_(PrakticiKapacity.expirace == None, PrakticiKapacity.expirace >= get_import_date())) \
        .order_by(PrakticiKapacity.kraj, PrakticiKapacity.mesto, PrakticiKapacity.nazev_ordinace,
                  PrakticiKapacity.typ_vakciny) \
        .all()


def find_free_vaccines_vaccine_options():
    return db.session.query(PrakticiKapacity.typ_vakciny) \
        .filter(PrakticiKapacity.pocet_davek > 0) \
        .filter(or_(PrakticiKapacity.expirace == None, PrakticiKapacity.expirace >= get_import_date())) \
        .distinct(PrakticiKapacity.typ_vakciny) \
        .order_by(PrakticiKapacity.typ_vakciny) \
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
        f"""
        select *
        from ockovani_registrace
        where import_id = {get_import_id()} and ockovaci_misto_id in({mista_ids}) 
        and datum + '90 days'::interval >= '{get_import_date()}' 
        """,
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

    end_date = db.session.query(column('datum')).from_statement(text(
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


def count_end_date_interested():
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
        where ockovaci_misto_id = '{}' and datum >= '{}' and kalendar_ockovani = 'V1' and maximalni_kapacita != 0
        order by datum
        """.format(center_id, get_import_date()),
        db.engine
    )

    rezervace_3 = pd.read_sql_query(
        """
        select datum, volna_kapacita volna_kapacita_3, maximalni_kapacita maximalni_kapacita_3
        from ockovani_rezervace  
        where ockovaci_misto_id = '{}' and datum >= '{}' and kalendar_ockovani = 'V3' and maximalni_kapacita != 0
        order by datum
        """.format(center_id, get_import_date()),
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
    return db.session.query(column('datum'), column('pocet_1'), column('pocet_2'), column('pocet_3'), column('pocet_celkem')).from_statement(text(
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
    return db.session.query(column('zarizeni_nazev'), column('pocet')).from_statement(text(
        f"""
        select zarizeni_nazev, sum(pocet) pocet
        from ockovani_lide 
        where datum >= '{get_import_date() - timedelta(7)}'
        group by zarizeni_nazev 
        order by pocet desc 
        limit 10;
        """
    )).all()


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


def count_vaccinated_unvaccinated_comparison_age():
    populace = pd.read_sql_query(
        """
        select vekova_skupina, sum(pocet) populace, min_vek
            from populace p 
            join populace_kategorie k on (k.min_vek <= vek and k.max_vek >= vek)
            where orp_kod = 'CZ0'
            group by vekova_skupina
        """,
        db.engine)

    srovnani = pd.read_sql_query(
        f"""
        select n.tyden, n.tyden_od, n.tyden_do, n.vekova_skupina,
            nakazeni_celkem, nakazeni_bez, nakazeni_castecne, nakazeni_plne, nakazeni_posilujici,
            hospitalizace_celkem, hospitalizace_bez, hospitalizace_castecne, hospitalizace_plne, hospitalizace_posilujici, 
            hospitalizace_jip_celkem, hospitalizace_jip_bez, hospitalizace_jip_castecne, hospitalizace_jip_plne, hospitalizace_jip_posilujici
        from nakazeni_ockovani_vek n 
        left join hospitalizace_ockovani_vek h on (h.tyden = n.tyden and h.vekova_skupina = n.vekova_skupina)
        left join hospitalizace_jip_ockovani_vek j on (j.tyden = n.tyden and j.vekova_skupina = n.vekova_skupina)
        where n.tyden_do < '{get_import_date()}'
        """,
        db.engine
    )
    srovnani_max_datum = srovnani['tyden_od'].max()
    srovnani = srovnani[srovnani['tyden_od'] == srovnani_max_datum]
    srovnani['vekova_skupina'] = srovnani['vekova_skupina'].str.replace(' let', '') \
        .replace({'80-84': '80+', '85-89': '80+', '90+': '80+'})
    srovnani = srovnani.groupby(['tyden', 'tyden_od', 'tyden_do', 'vekova_skupina']).sum().reset_index()

    ockovani = pd.read_sql_query(
        f"""
        select vekova_skupina,
            sum(case when poradi_davky = 1 then pocet else 0 end) populace_ockovani, 
            sum(case when poradi_davky = v.davky then pocet else 0 end) populace_plne, 
            sum(case when poradi_davky = 3 then pocet else 0 end) populace_posilujici
        from ockovani_lide o
        join vakciny v on (o.vakcina = v.vakcina)
        where datum < '{srovnani_max_datum}'
        group by vekova_skupina
        """,
        db.engine
    )
    ockovani = ockovani.groupby(['vekova_skupina']).sum().reset_index()

    df = pd.merge(ockovani, populace)
    df = pd.merge(df, srovnani)

    df['vekova_skupina'] = df['vekova_skupina'].replace(
        {'12-15': '12-17', '16-17': '12-17', '18-24': '18-29', '25-29': '18-29', '30-34': '30-39', '35-39': '30-39',
         '40-44': '40-49', '45-49': '40-49', '50-54': '50-59', '55-59': '50-59', '60-64': '60-69', '65-69': '60-69',
         '70-74': '70-79', '75-79': '70-79'})
    df = df.groupby(['tyden', 'tyden_od', 'tyden_do', 'vekova_skupina']).sum().reset_index()

    df['populace_bez'] = df['populace'] - df['populace_ockovani']
    df['populace_plne'] = df['populace_plne'] - df['populace_posilujici']

    df_norm = df.copy()

    datasets = ['nakazeni', 'hospitalizace', 'hospitalizace_jip']
    groups = ['bez', 'plne', 'posilujici']

    for g in groups:
        df_norm['populace_' + g + '_zastoupeni'] = df_norm['populace_' + g] / df_norm['populace']

    for d in datasets:
        for g in groups:
            df_norm[d + '_' + g + '_norm'] = ((100000 * df_norm[d + '_' + g]) / df_norm['populace_' + g]) \
                .replace({np.nan: 0})

        for g in ['plne', 'posilujici']:
            df_norm[d + '_' + g + '_ratio'] = (df_norm[d + '_bez_norm'] / df_norm[d + '_' + g + '_norm']).replace({np.inf: np.nan})
            df_norm.loc[df_norm['populace_' + g + '_zastoupeni'] < 0.05, d + '_' + g + '_ratio'] = np.nan
            df_norm[d + '_' + g + '_ratio'] = df_norm[d + '_' + g + '_ratio'].replace({np.nan: None})

    return df_norm


def count_hospitalization_probabilities():
    date_from = get_import_date() - relativedelta(months=4)
    date_to = get_import_date() - relativedelta(months=1)

    hosp = pd.read_sql_query(
        f"""
        select vek_kat, tezky_stav, jip, kyslik, upv, ecmo, umrti, dni_tezky_stav, dni_jip, dni_kyslik, dni_upv, dni_ecmo 
        from uzis_modely_05_hospitalizovani
        where datum_positivity >= '{date_from}' and datum_positivity <= '{date_to}'
        """,
        db.engine)
    hosp['vek_kat'] = hosp['vek_kat'].replace({'0-4': '0-9', '5-9': '0-9', '10-14': '10-19', '15-19': '10-19',
                                               '20-24': '20-29', '25-29': '20-29', '30-34': '30-39', '35-39': '30-39',
                                               '40-44': '40-49', '45-49': '40-49', '50-54': '50-59', '55-59': '50-59',
                                               '60-64': '60-69', '65-69': '60-69', '70-74': '70-79', '75-79': '70-79',
                                               '80-84': '80-89', '85-89': '80-89', '90-94': '90+', '95-99': '90+',
                                               '100-104': '90+', '105-109': '90+'})
    hosp['hospitalizace'] = True
    hosp = hosp.groupby(['vek_kat']).sum().reset_index()

    nakazeni = pd.read_sql_query(
        f"select pocet, vek from nakazeni where datum >= '{date_from}' and datum <= '{date_to}'",
        db.engine)
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 150]
    labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80-89', '90+']
    nakazeni['vekova_skupina'] = pd.cut(nakazeni['vek'], bins=bins, labels=labels, right=False)
    nakazeni = nakazeni.drop(columns=['vek']).groupby(['vekova_skupina']).sum().reset_index()

    df = pd.merge(hosp, nakazeni, left_on=['vek_kat'], right_on=['vekova_skupina'])

    df['hospitalizace_r'] = df['hospitalizace'] / df['pocet']
    df['jip_r'] = df['jip'] / df['pocet']
    df['kyslik_r'] = df['kyslik'] / df['pocet']
    df['upv_r'] = df['upv'] / df['pocet']
    df['ecmo_r'] = df['ecmo'] / df['pocet']
    df['tezky_stav_r'] = df['tezky_stav'] / df['pocet']
    df['umrti_r'] = df['umrti'] / df['pocet']

    df['jip_d'] = (df['dni_jip'] / df['jip']).replace({np.nan: None})
    df['kyslik_d'] = (df['dni_kyslik'] / df['kyslik']).replace({np.nan: None})
    df['upv_d'] = (df['dni_upv'] / df['upv']).replace({np.nan: None})
    df['ecmo_d'] = (df['dni_ecmo'] / df['ecmo']).replace({np.nan: None})
    df['tezky_stav_d'] = (df['dni_tezky_stav'] / df['tezky_stav']).replace({np.nan: None})

    return (df, date_from, date_to)


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
        where ockovaci_misto_id = '{}'
        group by datum
        """.format(center_id),
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
    return db.session.query(column('vyrobce'), column('datum'), column('prijem')).from_statement(text(
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
    return db.session.query(column('vyrobce'), column('datum'), column('ockovano')).from_statement(text(
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
        from nakazeni n
        join populace_kategorie k on (k.min_vek <= vek and k.max_vek >= vek)
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

    df['vekova_skupina_grp'] = df['vekova_skupina'].replace(
        {'0-11': '0-17', '12-15': '0-17', '16-17': '0-17', '18-24': '18-29', '25-29': '18-29', '30-34': '30-39',
         '35-39': '30-39', '40-44': '40-49', '45-49': '40-49', '50-54': '50-59', '55-59': '50-59', '60-64': '60-69',
         '65-69': '60-69', '70-74': '70-79', '75-79': '70-79'})

    df = df.groupby(['vekova_skupina_grp', 'datum']).sum()
    df_sum = df.rolling(7).sum()

    df_sum['pocet_nakazeni_norm'] = ((df_sum['pocet_nakazeni'] / df_sum['pocet_vek']) * 100000)

    df = pd.merge(df_sum[['pocet_nakazeni_norm']], df[['pocet_nakazeni']], left_index=True, right_index=True)

    df = df[df.index.get_level_values(1) >= df.index.get_level_values(1).min() + timedelta(7)]

    return df


def get_deaths_graph_data():
    umrti = pd.read_sql_query(
        """
        select datum, vekova_skupina, sum(pocet) pocet_umrti
        from umrti u
        join populace_kategorie k on (k.min_vek <= vek and k.max_vek >= vek)
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

    df['vekova_skupina_grp'] = df['vekova_skupina'].replace(
        {'0-11': '0-17', '12-15': '0-17', '16-17': '0-17', '18-24': '18-29', '25-29': '18-29', '30-34': '30-39',
         '35-39': '30-39', '40-44': '40-49', '45-49': '40-49', '50-54': '50-59', '55-59': '50-59', '60-64': '60-69',
         '65-69': '60-69', '70-74': '70-79', '75-79': '70-79'})

    df = df.groupby(['vekova_skupina_grp', 'datum']).sum()
    df_sum = df.rolling(7).sum()

    df_sum['pocet_umrti_norm'] = ((df_sum['pocet_umrti'] / df_sum['pocet_vek']) * 100000)

    df = pd.merge(df_sum[['pocet_umrti_norm']], df[['pocet_umrti']], left_index=True, right_index=True)

    df = df[df.index.get_level_values(1) >= df.index.get_level_values(1).min() + timedelta(7)]

    return df


def get_hospitalized_graph_data():
    hospitalizace = pd.read_sql_query("select * from hospitalizace", db.engine)

    hospitalizace = hospitalizace.set_index('datum')

    return hospitalizace


def get_tests_graph_data():
    df = pd.read_sql_query("select * from testy", db.engine)

    df = df.set_index('datum')
    df_sum = df.rolling(7).sum()

    df_sum['pozitivita_diagnosticka'] = (df_sum['pozit_typologie_test_indik_diagnosticka'] / df_sum['typologie_test_indik_diagnosticka']) * 100
    df_sum['pozitivita_epidemiologicka'] = (df_sum['pozit_typologie_test_indik_epidemiologicka'] / df_sum['typologie_test_indik_epidemiologicka']) * 100
    df_sum['pozitivita_preventivni'] = (df_sum['pozit_typologie_test_indik_preventivni'] / df_sum['typologie_test_indik_preventivni']) * 100

    df = pd.merge(df_sum[['pozitivita_diagnosticka', 'pozitivita_epidemiologicka', 'pozitivita_preventivni']], df, left_index=True, right_index=True)

    df = df[df.index >= df.index.min() + timedelta(7)]

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


def get_hospital_capacities_graph_data():
    capacities = pd.read_sql_query(f"select * from kapacity_nemocnic where datum < '{get_import_date()}'", db.engine).fillna(0)
    capacities['luzka_standard_kyslik_kapacita_volna_covid_pozitivni'] += capacities['inf_luzka_kyslik_kapacita_volna_covid_pozitivni']
    capacities['luzka_standard_kyslik_kapacita_volna_covid_negativni'] += capacities['inf_luzka_kyslik_kapacita_volna_covid_negativni']
    capacities['luzka_standard_kyslik_kapacita_celkem'] += capacities['inf_luzka_kyslik_kapacita_celkem']
    capacities['luzka_hfno_cpap_kapacita_volna_covid_pozitivni'] += capacities['inf_luzka_hfno_kapacita_volna_covid_pozitivni']
    capacities['luzka_hfno_cpap_kapacita_volna_covid_negativni'] += capacities['inf_luzka_hfno_kapacita_volna_covid_negativni']
    capacities['luzka_hfno_cpap_kapacita_celkem'] += capacities['inf_luzka_hfno_kapacita_celkem']
    capacities['luzka_upv_niv_kapacita_volna_covid_pozitivni'] += capacities['inf_luzka_upv_kapacita_volna_covid_pozitivni']
    capacities['luzka_upv_niv_kapacita_volna_covid_negativni'] += capacities['inf_luzka_upv_kapacita_volna_covid_negativni']
    capacities['luzka_upv_niv_kapacita_celkem'] += capacities['inf_luzka_upv_kapacita_celkem']

    capacities_21 = pd.read_sql_query("select * from kapacity_nemocnic_21 where datum >= '2021-03-30'", db.engine).fillna(0)

    capacities_20 = pd.read_sql_query("select * from kapacity_nemocnic_20", db.engine).fillna(0)

    kraje = pd.read_sql_query("select id, nazev_kratky nazev from kraje", db.engine)
    kraje['nazev_norm'] = kraje['nazev'].str.normalize('NFKD') \
        .str.encode('ascii', errors='ignore') \
        .str.decode('utf-8') \
        .str.lower()

    df = pd.concat([capacities_20, capacities_21, capacities])

    df = pd.merge(df, kraje, left_on='kraj_nuts_kod', right_on='id')
    df = df.drop(columns=['zz_kod', 'zz_nazev', 'id'])
    df = df.groupby(['kraj_nuts_kod', 'datum', 'nazev', 'nazev_norm']).sum().reset_index()

    df_cr = df.groupby('datum').sum().reset_index()
    df_cr['kraj_nuts_kod'] = 'CZ0'
    df_cr['nazev'] = 'ČR'
    df_cr['nazev_norm'] = 'cr'

    df = df.set_index(['nazev_norm', 'datum'])
    df_cr = df_cr.set_index(['nazev_norm', 'datum'])

    df = pd.concat([df_cr, df])

    df = df.sort_index()

    df['ventilatory_volno'] = df['ventilatory_prenosne_kapacita_volna'] + df['ventilatory_operacni_sal_kapacita_volna']
    df['ventilatory_celkem'] = df['ventilatory_prenosne_kapacita_celkem'] + df[
        'ventilatory_operacni_sal_kapacita_celkem']

    df = df.drop(columns=['ventilatory_prenosne_kapacita_volna', 'ventilatory_operacni_sal_kapacita_volna',
                          'ventilatory_prenosne_kapacita_celkem', 'ventilatory_operacni_sal_kapacita_celkem'])

    df = df.rename(columns={'luzka_standard_kyslik_kapacita_volna_covid_pozitivni': 'kyslik_volno_poz',
                            'luzka_standard_kyslik_kapacita_volna_covid_negativni': 'kyslik_volno_neg',
                            'luzka_standard_kyslik_kapacita_celkem': 'kyslik_celkem',
                            'luzka_hfno_cpap_kapacita_volna_covid_pozitivni': 'hfno_volno_poz',
                            'luzka_hfno_cpap_kapacita_volna_covid_negativni': 'hfno_volno_neg',
                            'luzka_hfno_cpap_kapacita_celkem': 'hfno_celkem',
                            'luzka_upv_niv_kapacita_volna_covid_pozitivni': 'upv_volno_poz',
                            'luzka_upv_niv_kapacita_volna_covid_negativni': 'upv_volno_neg',
                            'luzka_upv_niv_kapacita_celkem': 'upv_celkem',
                            'ecmo_kapacita_volna': 'ecmo_volno',
                            'ecmo_kapacita_celkem': 'ecmo_celkem',
                            'cvvhd_kapacita_volna': 'cvvhd_volno',
                            'cvvhd_kapacita_celkem': 'cvvhd_celkem'})

    df['kyslik_obsazeno'] = df['kyslik_celkem'] - df['kyslik_volno_poz'] - df['kyslik_volno_neg']
    df['hfno_obsazeno'] = df['hfno_celkem'] - df['hfno_volno_poz'] - df['hfno_volno_neg']
    df['upv_obsazeno'] = df['upv_celkem'] - df['upv_volno_poz'] - df['upv_volno_neg']
    df['ecmo_obsazeno'] = df['ecmo_celkem'] - df['ecmo_volno']
    df['cvvhd_obsazeno'] = df['cvvhd_celkem'] - df['cvvhd_volno']
    df['ventilatory_obsazeno'] = df['ventilatory_celkem'] - df['ventilatory_volno']

    return df
