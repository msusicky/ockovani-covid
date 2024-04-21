import random
import string
from datetime import datetime

from flask import session, redirect, request, url_for

from app import db, bp
from app.models import ZdravotnickeStredisko, PrakticiLogin, PrakticiKapacity


@bp.route("/praktici_admin/register", methods=['POST'])
def praktici_admin_register():
    session.pop('error', None)
    session.pop('success', None)

    id = request.form.get('id')[:14]

    # for ICO acceptance
    if len(id) < 14:
        id = id.ljust(14, '0')

    zarizeni = db.session.query(ZdravotnickeStredisko) \
        .filter(ZdravotnickeStredisko.zdravotnicke_zarizeni_kod == id) \
        .one_or_none()

    user = db.session.query(PrakticiLogin) \
        .filter(PrakticiLogin.zdravotnicke_zarizeni_kod == id) \
        .one_or_none()

    if zarizeni is None:
        session['error'] = 'Zdravotnické zařízení se zadaným kódem neexistuje.'
    elif user is not None:
        session['error'] = 'Zdravotnické zařízení je už registrováno.'
    else:
        random.seed(datetime.now().timestamp())
        characters = string.ascii_letters + string.digits
        passwd = ''.join(random.choice(characters) for i in range(8))

        user = PrakticiLogin(id, passwd)
        db.session.add(user)

        db.session.commit()

        session['user_id'] = id
        session['user_passwd'] = passwd

        session['success'] = f"Děkujeme za registraci. Pro ordinaci {id} je Vaše heslo <strong>{passwd}</strong>."

    return redirect(url_for('view.praktici_admin'))


@bp.route("/praktici_admin/login", methods=['POST'])
def praktici_admin_login():
    session.pop('error', None)
    session.pop('success', None)

    id = request.form.get('id')[:14]
    # for ICO acceptance
    if len(id) < 14:
        id = id.ljust(14, '0')

    passwd = request.form.get('passwd')

    user = db.session.query(PrakticiLogin) \
        .filter(PrakticiLogin.zdravotnicke_zarizeni_kod == id) \
        .filter(PrakticiLogin.heslo == passwd) \
        .one_or_none()

    if user is None:
        session['error'] = 'Neplatné zdravotnické zařízení nebo heslo.'
    else:
        session['user_id'] = id
        session['user_passwd'] = passwd

    return redirect(url_for('view.praktici_admin'))


@bp.route("/praktici_admin/logout", methods=['GET'])
def praktici_admin_logout():
    session.pop('error', None)
    session.pop('success', None)

    session.pop('user_id', None)
    session.pop('user_passwd', None)

    return redirect(url_for('view.praktici_admin'))


@bp.route("/praktici_admin/edit", methods=['POST'])
def praktici_admin_edit():
    session.pop('error', None)
    session.pop('success', None)

    id = session['user_id']
    passwd = session['user_passwd']

    user = db.session.query(PrakticiLogin) \
        .filter(PrakticiLogin.zdravotnicke_zarizeni_kod == id) \
        .filter(PrakticiLogin.heslo == passwd) \
        .one_or_none()

    if user is None:
        session['error'] = 'Neplatné zdravotnické zařízení nebo heslo.'
    else:
        email = request.form.get('email')
        user.email = email if email else None

        telefon = request.form.get('telefon')
        user.telefon = telefon if telefon else None

        db.session.merge(user)

        for i in range(len(request.form.getlist('typ_vakciny[]'))):
            nemoc = request.form.getlist('nemoc[]')[i]
            typ_vakciny = request.form.getlist('typ_vakciny[]')[i]

            vaccine = db.session.query(PrakticiKapacity) \
                .filter(PrakticiKapacity.zdravotnicke_zarizeni_kod == id) \
                .filter(PrakticiKapacity.nemoc == nemoc) \
                .filter(PrakticiKapacity.typ_vakciny == typ_vakciny) \
                .one_or_none()

            if vaccine is None:
                vaccine = PrakticiKapacity()
                vaccine.zdravotnicke_zarizeni_kod = id
                vaccine.nemoc = nemoc
                vaccine.typ_vakciny = typ_vakciny

            pocet_davek = request.form.getlist('pocet_davek[]')[i]
            vaccine.pocet_davek = pocet_davek if pocet_davek.isnumeric() else 0

            dospeli = [int(v) - 1 for v in request.form.getlist('dospeli[]')]
            vaccine.dospeli = i in dospeli

            deti = [int(v) - 1 for v in request.form.getlist('deti[]')]
            vaccine.deti = i in deti

            expirace = request.form.getlist('expirace[]')[i]
            vaccine.expirace = expirace if len(expirace) > 0 else None

            vaccine.datum_aktualizace = datetime.now()

            vaccine.poznamka = request.form.getlist('poznamka[]')[i]

            db.session.merge(vaccine)

        db.session.commit()

    return redirect(url_for('view.praktici_admin'))
