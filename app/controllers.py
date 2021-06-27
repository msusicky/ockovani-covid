import random
import string
from datetime import datetime

from flask import session, redirect, request, url_for

from app import db, bp
from app.models import ZdravotnickeStredisko, PrakticiLogin, PrakticiKapacity, Vakcina


@bp.route("/praktici_admin/register", methods = ['POST'])
def praktici_admin_register():
    session.pop('error', None)
    session.pop('success', None)

    id = request.form.get('id')

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
        random.seed(datetime.now())
        characters = string.ascii_letters + string.digits
        passwd = ''.join(random.choice(characters) for i in range(8))

        user = PrakticiLogin(id, passwd)
        db.session.add(user)

        vaccines = db.session.query(Vakcina).all()

        for vaccine in vaccines:
            free_vaccine = PrakticiKapacity()
            free_vaccine.zdravotnicke_zarizeni_kod = id
            free_vaccine.typ_vakciny = vaccine.vyrobce
            free_vaccine.kraj = zarizeni.kraj
            free_vaccine.mesto = zarizeni.obec
            free_vaccine.nazev_ordinace = zarizeni.nazev_cely
            free_vaccine.adresa = f'{zarizeni.ulice} {zarizeni.cislo_domu}, {zarizeni.psc} {zarizeni.obec}'
            free_vaccine.pocet_davek = 0
            free_vaccine.kontakt_email = zarizeni.email
            free_vaccine.kontakt_tel = zarizeni.telefon
            db.session.add(free_vaccine)

        db.session.commit()

        session['user_id'] = id
        session['user_passwd'] = passwd

        session['success'] = f"Děkujeme za registraci. Pro ordinaci '{id}' je Vaše heslo '{passwd}'."

    return redirect(url_for('view.praktici_admin'))


@bp.route("/praktici_admin/login", methods = ['POST'])
def praktici_admin_login():
    session.pop('error', None)
    session.pop('success', None)

    id = request.form.get('id')
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


@bp.route("/praktici_admin/logout", methods = ['GET'])
def praktici_admin_logout():
    session.pop('error', None)
    session.pop('success', None)

    session.pop('user_id', None)
    session.pop('user_passwd', None)

    return redirect(url_for('view.praktici_admin'))


@bp.route("/praktici_admin/edit", methods = ['POST'])
def praktici_admin_edit():
    session.pop('error', None)
    session.pop('success', None)

    id = session['user_id']
    passwd = session['user_passwd']

    user = db.session.query(PrakticiLogin) \
        .filter(PrakticiLogin.zdravotnicke_zarizeni_kod == id) \
        .fitler(PrakticiLogin.heslo == passwd) \
        .one_or_none()

    if user is None:
        session['error'] = 'Neplatné zdravotnické zařízení nebo heslo.'
    else:
        pass # todo: nacteni udaju z formulare a uprava zaznamu

    return redirect(url_for('view.praktici_admin'))


