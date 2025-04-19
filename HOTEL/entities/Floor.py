from ..db import db
from .Enums import YesNo, Locations
from .Room import Room


class Floor(db.Model):
    """
    A table for storing floor information. 

    Has a 2-way relationship with the Rooms table.
    Has a unique constraint on the combined hid and floor_number

    Note:
        Author: Avni Israni
        Documentation: Avni Israni
        Created: March 9, 2025
        Modified: April 17, 2025
    """
    __tablename__ = 'floors'
    id = db.Column(db.Integer, primary_key=True) 
    hid = db.Column(db.Integer, db.ForeignKey('hotels.id'))
    floor_number = db.Column(db.Integer,nullable=False)
    rooms = db.relationship('Room', backref='floors', lazy=True, cascade='all, delete-orphan') #floor is keeping track of rooms

    __table_args__ = (db.UniqueConstraint('hid', 'floor_number', name='hid_floor_number_unique'),)

    def add_room(self, number_rooms, hid, base_room_number, img, modPath, room_type, number_beds, rate,balcony,city_view,ocean_view,smoking,available,max_guests,wheelchair_accessible):
        """
        Create rooms in the hotel.

        Args:
            number_rooms (int): The number of rooms to add.
            hid (int): The unique ID of the hotel.
            base_room_number (int): The starting room number upon which more rooms will be added.
            img (str): The path to the image file.
            modPath (str): The path to the 3D model.
            room_type (RoomType): The type of the room
            number_beds (int): The number of beds in the room.
            rate (int): The nightly fee for the room.
            balcony (YesNo): YesNo.Y if the room has a balcony, else YesNo.N
            city_view (YesNo): YesNo.Y if the room has a city view, else YesNo.N
            ocean_view (YesNo): YesNo.Y if the room has an ocean_view, else YesNo.N
            smoking (YesNo): YesNo.Y if the room allows smowking, else YesNo.N
            max_guests (int): The maximum guest capacity for the room.
            wheelchair_accessible (YesNo): YesNo.Y if the room has is wheelchair accessible, else YesNo.N

        Returns:
            list[Room]: A list of the rooms to be added.
        """
        rooms = []
        for i in range(number_rooms):
            room = Room(
                fid=self.id,
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
        return rooms
    
    def get_hotel_id(self):
        """
        Retrieves the floor's hotel ID.

        Args:
            None

        Returns:
            int: The floor's hotel ID
        """
        return self.hid
    
    def get_floor_number(self):
        """
        Retrieves the floor number.

        Args:
            None

        Returns:
            int: The floor's location (number)
        """
        return self.floor_number
    
    def get_rooms(self):
        """
        Retrieves the floor's rooms.

        Args:
            None

        Returns:
            list[Room]: The list of rooms on the floor.
        """
        return self.rooms
    