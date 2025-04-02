from flask_sqlalchemy import SQLAlchemy
from enum import Enum as PyEnum
from sqlalchemy import DateTime, distinct, Computed
from datetime import datetime

db = SQLAlchemy()

class YesNo(PyEnum):
    Y = 'Y'
    N = "N"
class Locations(PyEnum):
    MALIBU = "Malibu"
    SM = "Santa Monica"
class RoomType(PyEnum):
    STRD = 'Standard'
    DLX = 'Deluxe'
    ST = 'Suite'
class Availability(PyEnum):
    A = 'Available'
    B = 'Booked'
    M = 'Maintenance'

class User(db.Model):
    __tablename__ = 'user'  # Name of the table in the database
    id = db.Column(db.Integer, primary_key=True)  # Unique id for each user
    name = db.Column(db.String(150), nullable=False)  # User's name
    email = db.Column(db.String(150), unique=True, nullable=False)  # User's email (must be unique)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    phone = db.Column(db.String(15))
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zipcode = db.Column(db.String(10))
    rewards = db.Column(db.Integer,default=0)
    room_number = db.Column(db.String(15), default="")
    first_login = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.Y) 
    text_notifications = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    email_notifications = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    bookings = db.relationship('Booking', backref='user', lazy=True) #user is keeping track of bookings

    @classmethod
    def get_user(cls, id):
        return cls.query.filter(cls.id==id).first()



class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Enum(Locations), nullable=False) 
    address = db.Column(db.String(200), nullable=False)
    #services
    free_wifi = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.Y) 
    free_breakfast = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    pool = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    gym = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    golf = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    floors = db.relationship('Floor', backref='hotel', lazy=True, cascade='all, delete-orphan') #hotel is keeping track of floors
    rooms = db.relationship('Room', backref='hotel', lazy=True, cascade='all, delete-orphan') #hotel is keeping track of floors

class Floor(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    hid = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    floor_number = db.Column(db.Integer,nullable=False)
    rooms = db.relationship('Room', backref='floor', lazy=True, cascade='all, delete-orphan') #floor is keeping track of rooms

    __table_args__ = (db.UniqueConstraint('hid', 'floor_number', name='hid_floor_number_unique'),)

    @classmethod
    def add_floor(cls, number_floors, hid, base_floor_number):
        floors = []
        for i in range(number_floors):
            floor = cls(hid=hid, floor_number=base_floor_number+i)
            floors.append(floor)
        db.session.add_all(floors)
        db.session.commit()

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True) 
    fid = db.Column(db.Integer, db.ForeignKey('floor.id'))
    hid = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    room_number = db.Column(db.Integer,nullable=False) #room number
    img = db.Column(db.String(200), nullable=False)
    modPath = db.Column(db.String(200))
    room_type = db.Column(db.Enum(RoomType),nullable=False,default=RoomType.STRD)
    number_beds = db.Column(db.Integer,default=1)
    rate = db.Column(db.Integer, nullable=False)
    balcony = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    city_view = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    ocean_view = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N)
    smoking = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N)  
    available = db.Column(db.Enum(Availability),nullable=False,default=Availability.A)
    max_guests = db.Column(db.Integer,default=2,nullable=False)
    wheelchair_accessible = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    bookings = db.relationship('Booking', backref='room', lazy=True, cascade='all, delete-orphan')  
    
    __table_args__ = (db.UniqueConstraint('hid', 'fid', 'room_number', name='hid_fid_room_number_unique'),)

    @classmethod
    def add_room(cls, num_rooms, fid, hid, base_room_number, img, modPath, room_type, number_beds, rate,balcony,city_view,ocean_view,smoking,available,max_guests,wheelchair_accessible):
        rooms = []
        for i in range(num_rooms):
            room = cls(
                fid=fid,
                hid=hid,
                room_number = base_room_number + i,
                img = img, 
                modPath=modPath,
                room_type = room_type,
                number_beds = number_beds,
                rate = rate,
                balcony = balcony,
                city_view = city_view, 
                ocean_view = ocean_view,
                smoking = smoking, 
                available = available,
                max_guests = max_guests, 
                wheelchair_accessible = wheelchair_accessible
            )     
            rooms.append(room)
        db.session.add_all(rooms)
        db.session.commit()
    
    @classmethod
    def get_room(cls, id):
        return cls.query.filter(id==id).first()


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
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
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rid = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False) 
    user = db.relationship('User', backref=db.backref('saved_u', lazy=True))
    room = db.relationship('Room', backref=db.backref('saved_r', lazy=True)) 
