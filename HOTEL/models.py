from flask_sqlalchemy import SQLAlchemy
from enum import Enum as PyEnum
from sqlalchemy import DateTime, distinct, Computed
from datetime import datetime, timedelta
from .db import db
from .model_objects import User, Booking
from .model_dbs import Locations, YesNo, RoomType, Availability, SType, Assistance
# from .model_objects.Booking import Booking
# from .model_objects.User import User







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
    bookings = db.relationship('Bookings', backref='room', lazy=True, cascade='all, delete-orphan')  
    
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

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bid = db.Column(db.Integer, db.ForeignKey('bookings.id'))
    issued = db.Column(DateTime, nullable=False)
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

    @classmethod
    def add_item(cls, bid, robes, btowels, htowels, soap, shampoo, conditioner, wash, lotion, hdryer, pillows, blankets, sheets):
        item = cls(bid=bid,issued=datetime.now(), stype=SType.I, robes=robes,btowels=btowels,htowels=htowels,soap=soap,shampoo=shampoo,conditioner=conditioner,wash=wash,lotion=lotion,hdryer=hdryer,pillows=pillows,blankets=blankets,sheets=sheets)
        db.session.add(item)
        db.session.commit()

    @classmethod
    def add_housekeeping(cls, bid,housetime):
        today = datetime.now()
        housedatetime = datetime.combine(today.date(), housetime)
        if housedatetime < today:
            housedatetime = today
        # check_out = Bookings.query.get(bid).check_out
        # if housedatetime <= check_out:
        #     housekeeping = cls(bid=bid,issued=today,stype=SType.H,housedatetime=housedatetime)
        #     db.session.add(housekeeping)
        #     db.session.commit()

    @classmethod
    def add_trash(cls, bid):
        trash = cls(bid=bid,issued=datetime.now(),stype=SType.T,trash=YesNo.Y)
        db.session.add(trash)
        db.session.commit()

    @classmethod
    def add_call(cls, bid, calltime, recurrent): #when calltime is recieved from form, it is of type time (not datetime)
        today = datetime.now()
        calls = []
        calldatetime = datetime.combine(today.date(), calltime)
        if calldatetime < today:
            calldatetime = calldatetime + timedelta(days=1)
        # check_out = Bookings.query.get(bid).check_out
        # if calldatetime <= check_out:
        #     if recurrent==YesNo.Y:
        #         while(calldatetime <= check_out):
        #             call = cls(bid=bid,issued=today,stype=SType.C,calldatetime=calldatetime)
        #             calls.append(call)
        #             calldatetime = calldatetime + timedelta(days=1)
        #     else:
        #         call = cls(bid=bid,issued=today,stype=SType.C,calldatetime=calldatetime)
        #         calls.append(call)
        #     db.session.add_all(calls)
        #     db.session.commit()

    @classmethod
    def add_dining(cls, bid, restaurant):
        dining = cls(bid=bid,issued=datetime.now(),stype=SType.D,restaurant=restaurant)
        db.session.add(dining)
        db.session.commit()
    
    @classmethod
    def add_assistance(cls, bid, assistance):
        a = cls(bid=bid,issued=datetime.now(),stype=SType.A,assistance=assistance)
        db.session.add(a)
        db.session.commit()

    @classmethod
    def add_other(cls, bid, other):
        o = cls(bid=bid,issued=datetime.now(),stype=SType.O,other=other)
        db.session.add(o)
        db.session.commit()
    

    