from .Enums import YesNo, Availability, RoomType
from ..db import db
from ..model_objects import Ro

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
    
    #############################################

    def create_room_object(self):
        return Ro(
             fid=self.fid,hid=self.hid,room_number=self.room_number,img=self.img,modPath=self.modPath,room_type=self.room_type,
             number_beds=self.number_beds,rate=self.rate,balcony=self.balcony,city_view=self.city_view,ocean_view=self.ocean_view,
             smoking=self.smoking,available=self.available,max_guests=self.max_guests,wheelchair_accessible=self.wheelchair_accessible
        ) #does not handle bookings logic!!!
    
    @classmethod
    def create_rooms_db(cls, rooms):
        room_rows=[]
        for room in rooms:
            room_rows.append(
                cls(
                    fid=cls.fid,hid=cls.hid,room_number=cls.room_number,img=cls.img,modPath=cls.modPath,room_type=cls.room_type,
                    number_beds=cls.number_beds,rate=cls.rate,balcony=cls.balcony,city_view=cls.city_view,ocean_view=cls.ocean_view,
                    smoking=cls.smoking,available=cls.available,max_guests=cls.max_guests,wheelchair_accessible=cls.wheelchair_accessible                
                )
            ) #does not handle bookings logic!!!
        return room_rows

    @classmethod
    def update_rooms_db(cls, room):
        model=cls.query.get(room.id)
        if model:
            model.fid=room.fid,
            model.hid=room.hid,
            model.room_number = room.room_number
            model.img = room.img, 
            model.modPath=room.modPath,
            model.room_type = room.room_type,
            model.number_beds = room.number_beds,
            model.rate = room.rate,
            model.balcony = room.balcony,
            model.city_view = room.city_view, 
            model.ocean_view = room.ocean_view,
            model.smoking = room.smoking, 
            model.available = room.available,
            model.max_guests = room.max_guests, 
            model.wheelchair_accessible = room.wheelchair_accessible
            return True
        return False