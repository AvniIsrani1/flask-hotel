from sqlalchemy import DateTime, distinct, Computed, asc, desc
from datetime import datetime
from ..model_objects import Booking, User
from .Enums import YesNo
from ..db import db


class Bookings(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True) 
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


    def create_booking_object(self):
        return Booking(id=self.id,uid=self.uid, rid=self.rid, check_in=self.check_in,
                       check_out=self.check_out, fees=self.fees, cancel_date=self.cancel_date,
                       refund_type=self.refund_type,special_requests=self.special_requests,name=self.name,
                       email=self.email,phone=self.phone,num_guests=self.num_guests
        )
    
    @classmethod
    def create_bookings_db(cls, bookings):
        booking_rows = []
        for booking in bookings:
            booking_rows.append(
                cls(
                    uid=booking.uid,rid=booking.rid,check_in=booking.check_in,check_out=booking.check_out,fees=booking.fees,
                    cancel_date=booking.cancel_date,
                    refund_type=YesNo.Y if booking.refund_type else YesNo.N,
                    special_requests=booking.special_requests,
                    name=booking.name,email=booking.email,phone=booking.phone,num_guests=booking.num_guests
                )
            )
        return booking_rows


    @classmethod
    def update_bookings_db(cls, booking):
        model=cls.query.get(booking.id)
        if model:
            model.cancel_date = booking.cancel_date
            model.refund_type = YesNo.Y if booking.refund_type else YesNo.N
            model.special_requests = booking.special_requests
            model.name = booking.name
            model.email = booking.email
            model.phone = booking.phone
            model.num_guests = booking.num_guests
            return True
        return False

    @classmethod
    def add_booking(cls, uid, rid, check_in, check_out, fees, special_requests, name, email, phone, num_guests):
        booking = cls(uid=uid, rid=rid, check_in=check_in, check_out=check_out, fees=fees, special_requests=special_requests, name=name, email=email, phone=phone, num_guests=num_guests)
        db.session.add(booking)
        db.session.commit()

    @classmethod
    def get_current_bookings(cls):
        today = datetime.now()
        return cls.query.filter(cls.check_in<=today,cls.check_out>=today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out))

    @classmethod
    def get_current_user_bookings(cls,uid):
        today = datetime.now()
        return cls.query.filter(cls.uid==uid, cls.check_in<=today,cls.check_out>=today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out))


    @classmethod
    def get_future_bookings(cls):
        today = datetime.now()
        return cls.query.filter(cls.check_in>today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out))
    
    @classmethod
    def get_past_bookings(cls):
        today = datetime.now()
        return cls.query.filter(cls.check_out<today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out))
    
    @classmethod
    def get_canceled_bookings(cls):
        return cls.query.filter(cls.cancel_date.isnot(None)).order_by(desc(cls.check_in), asc(cls.check_out))
    

    