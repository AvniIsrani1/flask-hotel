from .Enums import YesNo, Availability, RoomType
from ..db import db

class Room(db.Model):
    """
    A table for storing room information.

    Maintains a 2-way relationship with the Bookings table.
    There is a unique constraint on the combined hid, fid, and room_number

    Note:
        Author: Avni Israni
        Documentation: Avni Israni
        Created: March 6, 2025
        Modified: April 17, 2025
    """
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True) 
    fid = db.Column(db.Integer, db.ForeignKey('floors.id'))
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
    bookings = db.relationship('Booking', backref='rooms', lazy=True, cascade='all, delete-orphan')  
    
    __table_args__ = (db.UniqueConstraint('fid', 'room_number', name='fid_room_number_unique'),)

    
    @classmethod
    def get_room(cls, id):
        """
        Retrieve the room by its unique ID.

        Parameters:
            id: The unique ID of the room.

        Returns:
            Room | None: The Room object if found, else None.
        """
        return cls.query.filter(cls.id==id).first()
    
    def get_room_hotel(self):
        """
        Retrieve the hotel ID of the room.

        Parameters:
            None

        Returns:
            int: The room's hotel ID (hid)
        """
        return self.floors.hid
    
    def get_room_number(self):
        """
        Retrieve the room number of the room.

        Parameters:
            None

        Returns:
            int: The room's room number
        """
        return self.room_number
    
    def get_room_location(self):
        """
        Retrieve the room's full location

        Parameters:
            None

        Returns:
            int: The full location of the room (floor_number + room_number)
        """
        return self.floors.floor_number*100 + self.room_number
    
    def get_room_type(self):
        """
        Retrieve the room's room type

        Parameters:
            None

        Returns:
            RoomType: The room type of the room
        """
        return self.room_type
    
    def get_number_beds(self):
        """
        Retrieve the number of beds in the room.

        Parameters:
            None
        
        Returns:
            int: The number of beds in the room.
        """
        return self.number_beds
    
    def get_rate(self):
        """
        Retrieve the nightly rate of the room.

        Parameters:
            None

        Returns:
            int: The nightly rate of the room.
        """
        return self.rate
    
    def get_balcony(self):
        """
        Retrieve the balcony status of the room.

        Parameters:
            None

        Returns:
            YesNo: YesNo.Y if the room has a balcony, else YesNo.N.
        """
        return self.balcony
    
    def get_city_view(self):
        """
        Retrieve the city view status of the room.

        Parameters:
            None

        Returns:
            YesNo: YesNo.Y if the room has a city view, else YesNo.N.
        """
        return self.city_view
    
    def get_ocean_view(self):
        """
        Retrieve the ocean view status of the room.

        Parameters:
            None

        Returns:
            YesNo: YesNo.Y if the room has an ocean view, else YesNo.N.
        """
        return self.ocean_view
    
    def get_smoking(self):
        """
        Retrieve the smoking status of the room.

        Parameters:
            None

        Returns:
            YesNo: YesNo.Y if the room allows smoking, else YesNo.N.
        """
        return self.smoking

    def get_max_guests(self):
        """
        Retrieve the guest capacity of the room.

        Parameters:
            None

        Returns:
            int: The maximum number of guests allowed in the room.
        """
        return self.max_guests
    
    def get_wheelchair_accessible(self):
        """
        Retrieve the wheelchair accessibility status of the room.

        Parameters:
            None

        Returns:
            YesNo: YesNo.Y if the room is wheelchair accessible, else YesNo.N
        """
        return self.wheelchair_accessible
    
    def get_bookings(self):
        """
        Retrieve the bookings held in the room.

        Parameters:
            None

        Returns:
            list[Booking]: A list of all bookings (past, current, future, canceled) held in the room.
        """
        return self.bookings
    
    def get_room_description(self):
        desc = str(self.number_beds) + '-Bedroom ' + self.room_type.value
        if self.wheelchair_accessible==YesNo.Y:
            desc = desc + " (Wheelchair Accessible)"
        if self.balcony==YesNo.Y:
            desc = desc + " with Balcony"
        if self.ocean_view==YesNo.Y and self.city_view==YesNo.Y:
            desc = desc + " - Ocean View, City View"
        elif self.ocean_view==YesNo.Y:
            desc = desc + " - Ocean View"
        elif self.city_view==YesNo.Y:
            desc = desc+ " - City View"
        if self.smoking == YesNo.N:
            desc = desc + " | Non-Smoking"
        return desc
    


