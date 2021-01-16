from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, Unicode, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker

db = SQLAlchemy()

class MyModel(db.Model):
    id = Column(Integer, primary_key=True)
    some_string = Column(Unicode)
    some_integer = Column(Integer)
    some_time = Column(DateTime, default=datetime.now)


class OckovaciMisto(db.Model):
    misto_id = Column(Integer, primary_key=True)
    nazev = Column(Unicode)
    service_id = Column(Integer)
    operation_id= Column(Integer)
    place_id= Column(Integer)
    mesto= Column(Unicode)
