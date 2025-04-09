from sqlalchemy import DateTime, distinct, Computed
from datetime import datetime
from ..model_objects import Booking, User
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

    def create_booking_object(self):
        return Booking(id=self.id, uid=self.uid, rid=self.rid, check_in=self.check_in,
                       check_out=self.check_out, fees=self.fees, cancel_date=self.cancel_date,
                       refund_type=self.refund_type,special_requests=self.special_requests,name=self.name,
                       email=self.email,phone=self.phone,num_guests=self.num_guests
        )

    @classmethod
    def add_booking(cls, uid, rid, check_in, check_out, fees, special_requests, name, email, phone, num_guests):
        booking = cls(uid=uid, rid=rid, check_in=check_in, check_out=check_out, fees=fees, special_requests=special_requests, name=name, email=email, phone=phone, num_guests=num_guests)
        db.session.add(booking)
        db.session.commit()

    @classmethod
    def get_current_bookings(cls):
        today = datetime.now()
        return cls.query.filter(cls.check_in<=today,cls.check_out>=today, cls.cancel_date.is_(None))
    
    @classmethod
    def get_future_bookings(cls):
        today = datetime.now()
        return cls.query.filter(cls.check_in>today, cls.cancel_date.is_(None))
    
    @classmethod
    def get_past_bookings(cls):
        today = datetime.now()
        return cls.query.filter(cls.check_out<today, cls.cancel_date.is_(None))
    
    @classmethod
    def get_canceled_bookings(cls):
        return cls.query.filter(cls.cancel_date.isnot(None))
    
    def update_booking(self, special_requests, name, email, phone, num_guests):
        self.special_requests = special_requests
        self.name = name
        self.email = email
        self.phone = phone
        self.num_guests=num_guests
        db.session.commit()

    def cancel_booking(self):
        today = datetime.now()
        if (self.check_in - today).days >=2:
            self.refund_type = YesNo.Y
        else:
            self.refund_type = YesNo.N
        self.cancel_date = today
        print('Canceled booking')
        db.session.commit()

    def full_refund(self):
        today = datetime.now()
        if (self.check_in - today).days >=2:
            return True
        return False
    