from .Enums import YesNo, Availability, RoomType
from ..db import db

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
    def get_room(cls, id):
        return cls.query.filter(id==id).first()
    
    def get_room_number(self):
        return self.room_number
    
    def get_room_location(self):
        return self.fid*100 + self.id
    
    def get_room_type(self):
        return self.room_type
    
    def get_number_beds(self):
        return self.number_beds
    
    def get_rate(self):
        return self.rate
    
    def get_balcony(self):
        return self.balcony
    
    def get_city_view(self):
        return self.city_view
    
    def get_ocean_view(self):
        return self.ocean_view
    
    def get_smoking(self):
        return self.smoking
    
    def get_available(self):
        return self.available

    def get_max_guests(self):
        return self.max_guests
    
    def get_wheelchair_accessible(self):
        return self.wheelchair_accessible
    
    def get_bookings(self):
        return self.bookings
    