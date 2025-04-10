from flask_sqlalchemy import SQLAlchemy
from enum import Enum as PyEnum
from sqlalchemy import DateTime, distinct, Computed
from datetime import datetime, timedelta
from .db import db
from .model_objects import User, Booking, Service
from .model_dbs import Locations, YesNo, RoomType, Availability, SType, Assistance
# from .model_objects.Booking import Booking
# from .model_objects.User import User








class FAQ(db.Model):
    __tablename__ = 'faq'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(150), nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    subject = db.Column(db.String(150), nullable=False)

    @classmethod
    def add_faq(cls, f):
        faqs = []
        for question, answer, subject in f:
            faq = cls(question=question, answer=answer, subject=subject)
            faqs.append(faq)
        db.session.add_all(faqs)
        db.session.commit()

class Saved(db.Model):
    __tablename__ = 'saved'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rid = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False) 
    user = db.relationship('Users', backref=db.backref('saved_u', lazy=True))
    room = db.relationship('Room', backref=db.backref('saved_r', lazy=True)) 


    

    