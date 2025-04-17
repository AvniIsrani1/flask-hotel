from .Enums import YesNo, Availability, RoomType
from ..db import db

class Room(db.Model):
    __tablename__ = 'room'
    """
    A table for storing room information.
    Maintains a 2-way relationship with the Bookings table.
    There is a unique constraint on the combined hid, fid, and room_number
    """
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
        """
        Retrieve the room by its unique ID.

        Args:
            id: The unique ID of the room.

        Returns:
            Room | None: The Room object if found, else None.
        """
        return cls.query.filter(id==id).first()
    
    def get_room_number(self):
        """
        Retrieve the room number of the room.

        Args:
            None

        Returns:
            int: The room's room number
        """
        return self.room_number
    
    def get_room_location(self):
        """
        Retrieve the room's full location

        Args:
            None

        Returns:
            int: The full location of the room (floor_number + room_number)
        """
        return self.fid*100 + self.id #nned to fix this
    
    def get_room_type(self):
        """
        Retrieve the room's room type

        Args:
            None

        Returns:
            RoomType: The room type of the room
        """
        return self.room_type
    
    def get_number_beds(self):
        """
        Retrieve the number of beds in the room.

        Args:
            None
        
        Returns:
            int: The number of beds in the room.
        """
        return self.number_beds
    
    def get_rate(self):
        """
        Retrieve the nightly rate of the room.

        Args:
            None

        Returns:
            int: The nightly rate of the room.
        """
        return self.rate
    
    def get_balcony(self):
        """
        Retrieve the balcony status of the room.

        Args:
            None

        Returns:
            YesNo: YesNo.Y if the room has a balcony, else YesNo.N.
        """
        return self.balcony
    
    def get_city_view(self):
        """
        Retrieve the city view status of the room.

        Args:
            None

        Returns:
            YesNo: YesNo.Y if the room has a city view, else YesNo.N.
        """
        return self.city_view
    
    def get_ocean_view(self):
        """
        Retrieve the ocean view status of the room.

        Args:
            None

        Returns:
            YesNo: YesNo.Y if the room has an ocean view, else YesNo.N.
        """
        return self.ocean_view
    
    def get_smoking(self):
        """
        Retrieve the smoking status of the room.

        Args:
            None

        Returns:
            YesNo: YesNo.Y if the room allows smoking, else YesNo.N.
        """
        return self.smoking

    def get_max_guests(self):
        """
        Retrieve the guest capacity of the room.

        Args:
            None

        Returns:
            int: The maximum number of guests allowed in the room.
        """
        return self.max_guests
    
    def get_wheelchair_accessible(self):
        """
        Retrieve the wheelchair accessibility status of the room.

        Args:
            None

        Returns:
            YesNo: YesNo.Y if the room is wheelchair accessible, else YesNo.N
        """
        return self.wheelchair_accessible
    
    def get_bookings(self):
        """
        Retrieve the bookings held in the room.

        Args:
            None

        Returns:
            list[Booking]: A list of all bookings (past, current, future, canceled) held in the room.
        """
        return self.bookings
    