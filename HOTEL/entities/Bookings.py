from sqlalchemy import DateTime, distinct, Computed, asc, desc
from datetime import datetime
from .Enums import YesNo
from ..db import db


class Bookings(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rid = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    check_in = db.Column(DateTime, nullable=False)
    check_out = db.Column(DateTime, nullable=False)
    fees = db.Column(db.Integer, default=50)
    cancel_date = db.Column(DateTime)
    refund_type = db.Column(db.Enum(YesNo)) 
    special_requests = db.Column(db.String(1000))
    name = db.Column(db.String(150),nullable=False)
    email = db.Column(db.String(150),nullable=False)
    phone = db.Column(db.String(15),nullable=False)
    num_guests = db.Column(db.Integer, default=1)
    services = db.relationship('Services', backref='users', lazy=True, cascade='all, delete-orphan')

    def update_booking(self, special_requests, name, email, phone, num_guests):
        self.special_requests = special_requests
        self.name = name
        self.email = email
        self.phone = phone
        self.num_guests=num_guests

    def full_refund(self):
        today = datetime.now()
        if (self.check_in - today).days >= 2:
            return YesNo.Y
        return YesNo.N
    
    def cancel(self):
        today = datetime.now()
        self.refund_type = self.full_refund()
        self.cancel_date = today

    @classmethod
    def add_booking(cls, uid, rid, check_in, check_out, fees, special_requests, name, email, phone, num_guests):
        booking = cls(uid=uid, rid=rid, check_in=check_in, check_out=check_out, fees=fees, special_requests=special_requests, name=name, email=email, phone=phone, num_guests=num_guests)
        db.session.add(booking)
        db.session.commit()

    @classmethod
    def get_booking(cls, id):
        return cls.query.get(id)

    @classmethod
    def get_current_user_bookings(cls,uid):
        today = datetime.now()
        return cls.query.filter(cls.uid==uid, cls.check_in<=today, cls.check_out>=today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out)).all()

    @classmethod
    def get_specific_current_user_bookings(cls,uid,bid):
        today = datetime.now()
        return cls.query.filter(cls.uid==uid, cls.id==bid, cls.check_in<=today,cls.check_out>=today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out)).first()

    @classmethod
    def get_future_user_bookings(cls,uid):
        today = datetime.now()
        return cls.query.filter(cls.uid==uid,cls.check_in>today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out)).all()
    
    @classmethod
    def get_past_user_bookings(cls,uid):
        today = datetime.now()
        return cls.query.filter(cls.uid==uid, cls.check_out<today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out)).all()
    
    @classmethod
    def get_canceled_user_bookings(cls,uid):
        return cls.query.filter(cls.uid==uid, cls.cancel_date.isnot(None)).order_by(desc(cls.check_in), asc(cls.check_out)).all()
    

