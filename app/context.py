from datetime import date

from flask import g
from sqlalchemy import func

from app import db
from app.models import Import

STATUS_FINISHED = 'FINISHED'


def get_import_date():
    """
    Returns date of the last successful import.
    """
    if 'import_date' not in g:
        last_date = db.session.query(func.max(Import.date)).filter(Import.status == STATUS_FINISHED).first()[0]
        g.import_date = date.today() if last_date is None else last_date

    return g.import_date


def get_import_id():
    """
    Returns id of the last successful import.
    """
    if 'import_id' not in g:
        last_id = db.session.query(func.max(Import.id)).filter(Import.status == STATUS_FINISHED).first()[0]
        g.import_id = -1 if last_id is None else last_id

    return g.import_id