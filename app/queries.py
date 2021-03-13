from sqlalchemy import func

from app import db
from app.models import OckovaciMisto

STATUS_FINISHED = 'FINISHED'


def unique_nrpzs_subquery():
    return db.session.query(OckovaciMisto.nrpzs_kod) \
        .filter(OckovaciMisto.status == True) \
        .group_by(OckovaciMisto.nrpzs_kod) \
        .having(func.count(OckovaciMisto.nrpzs_kod) == 1) \
        .subquery()
