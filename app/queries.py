from datetime import date, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import func, or_, and_, text

from app import db
from app.context import get_import_date, get_import_id
from app.models import OckovaciMisto, Okres, Kraj, OckovaciMistoMetriky, CrMetriky


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
                               OckovaciMistoMetriky.registrace_fronta, OckovaciMistoMetriky.registrace_prumer_cekani,
                               OckovaciMistoMetriky.ockovani_odhad_cekani,
                               OckovaciMistoMetriky.registrace_fronta_prumer_cekani) \
        .join(OckovaciMistoMetriky) \
        .outerjoin(Okres, (OckovaciMisto.okres_id == Okres.id)) \
        .outerjoin(Kraj, (Okres.kraj_id == Kraj.id)) \
        .filter(filter_column == filter_value) \
        .filter(OckovaciMistoMetriky.datum == get_import_date()) \
        .filter(or_(OckovaciMisto.status == True, OckovaciMistoMetriky.registrace_fronta > 0,
                    OckovaciMistoMetriky.rezervace_cekajici > 0)) \
        .group_by(OckovaciMisto.id, OckovaciMisto.nazev, Okres.id, Kraj.id, OckovaciMisto.longitude,
                  OckovaciMisto.latitude, OckovaciMisto.adresa, OckovaciMisto.status,
                  OckovaciMistoMetriky.registrace_fronta, OckovaciMistoMetriky.registrace_prumer_cekani,
                  OckovaciMistoMetriky.ockovani_odhad_cekani, OckovaciMistoMetriky.registrace_fronta_prumer_cekani) \
        .order_by(Kraj.nazev, Okres.nazev, OckovaciMisto.nazev) \
        .all()

    return centers


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
            coalesce(sum(pocet) filter(where poradi_davky = davky), 0) pocet_ockovani_plne
        from ockovani_lide o 
        join vakciny v on v.vakcina = o.vakcina
        where datum < '{}' and (kraj_nuts_kod = '{}' or {})
        group by vekova_skupina
        order by vekova_skupina
        """.format(get_import_date(), kraj_id, kraj_id is None),
        db.engine
    )

    if kraj_id is not None:
        ockovani_kraj = pd.read_sql_query(
            """
            select vekova_skupina, coalesce(sum(pocet) filter(where poradi_davky = 1), 0) pocet_ockovani_v_kraji_castecne, 
                coalesce(sum(pocet) filter(where poradi_davky = davky), 0) pocet_ockovani_v_kraji_plne
            from ockovani_lide_profese o 
            join vakciny v on v.vakcina = o.vakcina
            where datum < '{}' and (kraj_bydl_nuts = '{}')
            group by vekova_skupina
            """.format(get_import_date(), kraj_id),
            db.engine
        )

        mista = pd.read_sql_query(
            """
            select ockovaci_mista.id ockovaci_misto_id from ockovaci_mista join okresy on ockovaci_mista.okres_id=okresy.id
            where kraj_id='{}';
            """.format(kraj_id),
            db.engine
        )
        mista_ids = ','.join("'" + misto + "'" for misto in mista['ockovaci_misto_id'].tolist())
    else:
        ockovani_kraj = None
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

    if kraj_id is not None:
        if ockovani_kraj is not None and not ockovani_kraj.empty:
            ockovani_kraj['vekova_skupina'] = ockovani_kraj['vekova_skupina'].replace(['nezařazeno'], 'neuvedeno')

            merged = pd.merge(merged, ockovani_kraj, how="left")
            merged['podil_ockovani_v_kraji_castecne'] = (merged['pocet_ockovani_v_kraji_castecne'] / merged['pocet_vek']) \
                .replace({np.nan: None})
            merged['podil_ockovani_v_kraji_plne'] = (merged['pocet_ockovani_v_kraji_plne'] / merged['pocet_vek']) \
                .replace({np.nan: None})
    else:
        merged['podil_ockovani_castecne'] = (merged['pocet_ockovani_castecne'] / merged['pocet_vek']) \
            .replace({np.nan: None})
        merged['podil_ockovani_plne'] = (merged['pocet_ockovani_plne'] / merged['pocet_vek']) \
            .replace({np.nan: None})
        merged['zajem'] = ((merged['pocet_fronta'] + merged['pocet_s_terminem']
                           + merged['pocet_ockovani_castecne']) / merged['pocet_vek']).replace({np.nan: None})

    return merged


def count_vaccinated_category():
    df = pd.read_sql_query(
        """
        select indikace_zdravotnik, indikace_socialni_sluzby, indikace_ostatni, indikace_pedagog, 
            indikace_skolstvi_ostatni, indikace_bezpecnostni_infrastruktura, indikace_chronicke_onemocneni,
            coalesce(sum(pocet) filter(where poradi_davky = 1), 0) pocet_ockovani_castecne, 
            coalesce(sum(pocet) filter(where poradi_davky = davky), 0) pocet_ockovani_plne
        from ockovani_lide_profese o
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
        select zarizeni_nazev, zarizeni_kod, obec, sum(pocet) as sum_1, 
            sum(case when ol.datum+'7 days'::interval>='{}' then pocet else 0 end) as sum_2
        from ockovani_lide ol left join (
            SELECT nrpzs_kod, string_agg(distinct obec, ', ') obec 
            from zdravotnicke_stredisko zs 
            group by nrpzs_kod
        ) zs on (ol.zarizeni_kod=zs.nrpzs_kod)
	    where zarizeni_kod not in (select nrpzs_kod from ockovaci_mista) and (kraj_nuts_kod='{}' or True={})
	    group by zarizeni_nazev, zarizeni_kod, obec 
	    order by sum(pocet) desc
        """.format(get_import_date(), kraj_id, kraj_id is None),
        db.engine
    )
    ockovani_doktori['obec'] = ockovani_doktori['obec'].replace({None: ''})
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
                               CrMetriky.pocet_obyvatel_dospeli) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one()

    if metrics is None or metrics.ockovani_pocet_castecne_zmena_tyden is None \
            or CrMetriky.ockovani_pocet_plne_zmena_tyden is None:
        return None

    population = metrics.pocet_obyvatel_dospeli
    population_to_vaccinate = population * 0.7
    days = (7 * (2 * population_to_vaccinate - metrics.ockovani_pocet_castecne - metrics.ockovani_pocet_plne)) \
           / (metrics.ockovani_pocet_castecne_zmena_tyden + metrics.ockovani_pocet_plne_zmena_tyden)
    return get_import_date() + timedelta(days=days)


def count_end_date_supplies():
    metrics = db.session.query(CrMetriky.pocet_obyvatel_dospeli) \
        .filter(CrMetriky.datum == get_import_date()) \
        .one()

    if metrics is None:
        return None

    population_to_vaccinate = metrics.pocet_obyvatel_dospeli * 0.7

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
                select datum, registrace_fronta, rezervace_cekajici_1, rezervace_cekajici_2
                from ockovaci_mista_metriky
                where misto_id = '{center_id}'
            """,
            db.engine
        )
    elif kraj_id:
        fronta = pd.read_sql_query(
            f"""
                select datum, registrace_fronta, rezervace_cekajici_1, rezervace_cekajici_2
                from kraje_metriky
                where kraj_id = '{kraj_id}'
            """,
            db.engine
        )
    else:
        fronta = pd.read_sql_query(
            """
                select datum, registrace_fronta, rezervace_cekajici_1, rezervace_cekajici_2
                from cr_metriky
            """,
            db.engine
        )

    fronta = fronta.set_index('datum').fillna(0).sort_values('datum')

    for idx, row in fronta.iterrows():
        if row['registrace_fronta'] == 0 and row['rezervace_cekajici_1'] == 0 and row['rezervace_cekajici_2'] == 0:
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
            sum(maximalni_kapacita-volna_kapacita) filter(where kalendar_ockovani = 'V2') rezervace_2
        from ockovani_rezervace  
        where ockovaci_misto_id = '{}' and import_id = {} and datum <= '{}'
        group by datum
        """.format(center_id, get_import_id(), get_import_date()),
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
                sum(pocet) filter(where poradi_davky = 2) ockovane_2
            from ockovani_lide o
            join ockovaci_mista m on m.nrpzs_kod = o.zarizeni_kod
            where m.id = '{}'
            group by datum
            """.format(center_id),
            db.engine
        )

        merged = pd.merge(merged, ockovani, how='outer')

    merged = merged.set_index('datum').fillna(0).sort_values('datum')

    return merged


def get_vaccination_total_graph_data():
    ockovani = pd.read_sql_query(
        """
        select datum, sum(pocet) filter(where poradi_davky = 1) ockovani_castecne, 
            sum(pocet) filter(where poradi_davky = v.davky) ockovani_plne
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
         df['vekova_skupina'] == '0-17'],
        ['80+', '70-79', '60-69', '0-17'], default='ostatni')

    df = df.groupby(['vekova_skupina_grp', 'datum']).sum()
    df = df.rolling(7).sum()

    df = df[df.index.get_level_values(1) >= df.index.get_level_values(1).min() + timedelta(7)]

    df['pocet_nakazeni_norm'] = ((df['pocet_nakazeni'] / df['pocet_vek']) * 100000).round(1)

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

    df['pocet_umrti_norm'] = ((df['pocet_umrti'] / df['pocet_vek']) * 100000).round(1)

    return df
