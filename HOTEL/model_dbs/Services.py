from ..db import db
from sqlalchemy import DateTime, distinct, Computed
from datetime import datetime
from .Enums import YesNo, Assistance, SType, Status

class Services(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bid = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    issued = db.Column(DateTime, nullable=False)
    modified = db.Column(DateTime)
    stype = db.Column(db.Enum(SType), nullable=False)
    robes = db.Column(db.Integer)
    btowels = db.Column(db.Integer)
    htowels = db.Column(db.Integer)
    soap = db.Column(db.Integer)
    shampoo = db.Column(db.Integer)
    conditioner = db.Column(db.Integer)
    wash = db.Column(db.Integer)
    lotion = db.Column(db.Integer)
    hdryer = db.Column(db.Integer)
    pillows = db.Column(db.Integer)
    blankets = db.Column(db.Integer)
    sheets = db.Column(db.Integer)
    housedatetime = db.Column(DateTime)
    trash = db.Column(db.Enum(YesNo)) 
    calldatetime = db.Column(DateTime)
    recurrent = db.Column(db.Enum(YesNo)) 
    restaurant = db.Column(db.String(200)) 
    assistance = db.Column(db.Enum(Assistance))
    other = db.Column(db.String(300)) 
    status = db.Column(db.Enum(Status),default=Status.N)

