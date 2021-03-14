from sqlalchemy import func

from app import db
from app.models import OckovaciMisto

import pandas as pd

STATUS_FINISHED = 'FINISHED'


def unique_nrpzs_subquery():
    return db.session.query(OckovaciMisto.nrpzs_kod) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.nrpzs_kod) \
        .having(func.count(OckovaciMisto.nrpzs_kod) == 1) \
        .subquery()


def count_vaccines(filter_column, filter_value):
    mista = pd.read_sql_query(
        """
        select ockovaci_mista.id ockovaci_misto_id, ockovaci_mista.nazev, okres_id, kraj_id 
        from ockovaci_mista join okresy on ockovaci_mista.okres_id=okresy.id
        where {}='{}';
        """.format(filter_column, filter_value),
        db.engine
    )

    mista_ids = ','.join("'" + misto + "'" for misto in mista['ockovaci_misto_id'].tolist())

    prijato = pd.read_sql_query(
        """
        select ockovaci_misto_id, vyrobce, sum(pocet_davek) prijato
        from ockovani_distribuce 
        where akce = 'Příjem' and ockovaci_misto_id in ({})
        group by (ockovaci_misto_id, vyrobce);
        """.format(mista_ids),
        db.engine
    )

    prijato_odjinud = pd.read_sql_query(
        """
        select cilove_ockovaci_misto_id ockovaci_misto_id, vyrobce, sum(pocet_davek) prijato_odjinud
        from ockovani_distribuce 
        where akce = 'Výdej' and cilove_ockovaci_misto_id in ({})
        group by (cilove_ockovaci_misto_id, vyrobce);
        """.format(mista_ids),
        db.engine
    )

    vydano = pd.read_sql_query(
        """
        select ockovaci_misto_id, vyrobce, sum(pocet_davek) vydano
        from ockovani_distribuce 
        where akce = 'Výdej' and ockovaci_misto_id in ({})
        group by (ockovaci_misto_id, vyrobce);
        """.format(mista_ids),
        db.engine
    )

    spotreba = pd.read_sql_query(
        """
        select ockovaci_misto_id, vyrobce, sum(pouzite_davky) pouzito, sum(znehodnocene_davky) znehodnoceno
        from ockovani_spotreba 
        where ockovaci_misto_id in ({})
        group by (ockovaci_misto_id, vyrobce);
        """.format(mista_ids),
        db.engine
    )

    mista_key = mista
    mista_key['join'] = 0
    vyrobci_key = spotreba[['vyrobce']].drop_duplicates()
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

    res['prijato_celkem'] = res['prijato'] + res['prijato_odjinud']
    res['skladem'] = res['prijato_celkem'] - res['vydano'] - res['pouzito'] - res['znehodnoceno']

    res = res.groupby(by=['vyrobce'], as_index=False).sum().sort_values(by=['vyrobce'])

    return res
