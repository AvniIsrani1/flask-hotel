from .Enums import YesNo, Locations, RoomType, Availability
from ..db import db
from .Floor import Floor
from .Room import Room

class Hotel(db.Model):
    """
    A table for storing hotel information.
    Maintains a 2-way relationship with the Floors and Rooms tables.
    """
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


    @classmethod
    def get_hotel(cls, hid):
        """
        Retrieve a hotel by its unique ID.

        Args:
            hid (int): The unique ID of the hotel.

        Returns:
            Hotel | None: The Hotel object if found, else None.
        """
        return cls.query.filter_by(hid=hid).first()
        
    @classmethod
    def get_hotels_by_location(cls, location):
        """
        Retrieve a list of hotels at the specified location. 

        Args: 
            location (Locations): The location of the hotel.
        
        Returns:
            list[Hotel]: A list of the hotel's at the specified location.
        """
        return cls.query.filter_by(location=Locations(location)).all()
    
    def get_location(self):
        """
        Retrieve the location of the Hotel object.

        Args:
            None

        Returns:
            Locations: The location of the hotel.
        """
        return self.location
    
    def get_address(self):
        """
        Retrieve the address of the Hotel object.

        Args:
            None

        Returns:
            str: The address of the hotel.
        """
        return self.address
    
    def get_hotel_services(self):
        """
        Retrieve the services offered by the hotel.

        Args:
            None

        Returns: 
            dict: A dictionary with details about the availability of hotel services (free wifi, free breakfast, pool, gym, and golf)
        """
        return {
            "free_wifi": self.free_wifi,
            "free_breakfast": self.free_breakfast,
            "pool": self.pool,
            "gym": self.gym,
            "golf": self.golf
        }
    
    def get_floors(self):
        """
        Retrieve the hotel's floors. 

        Args:
            None
        
        Returns:
            list[Floor]: A list of the hotel's floors.
        """
        return self.floors
    
    def get_rooms(self):
        """
        Retrieve the hotel's rooms.

        Args:
            None

        Returns:
            list[Room]: A list of the hotel's rooms.
        """
        return self.rooms
    
    def add_floor(self, number_floors, base_floor_number):
        """
        Create floors in the hotel.

        Args:
            number_floors: The number of floors to add.
            base_floor_number: The starting floor number upon which more floors will be added. 
        
        Returns:
            list[Floor]: A list of the floors created.
        """
        floors = []
        for i in range(number_floors):
            floor = Floor(hid=self.id, floor_number=base_floor_number+i)
            floors.append(floor)
        return floors

    def add_layout(self, base_floor_number, number_floors, add_room_params):
        """
        Create and commit the layout for the hotel (floors and rooms) (each floor gets the same room layout)

        Args:
            base_floor_number (int): The starting floor number upon which the room layout will be created.
            number_floors (int): The number of floors to recieve the room layout. 
            add_room_params (dict): A dictionary with keys - initial_room_base_number (int), rooms (list)

        Returns:
            None

        """
        floors = self.add_floor(number_floors=number_floors, base_floor_number=base_floor_number)
        rooms = []
        for floor in floors:
            fid = floor.id
            start = int(add_room_params["initial_room_base_number"])
            rooms_to_add = add_room_params["rooms"]
            for room_to_add in rooms_to_add:
                rooms.extend(
                    floor.add_room(
                        number_rooms=int(room_to_add["num_rooms"]),
                        hid=self.id,
                        base_room_number=start,
                        img=room_to_add["img"],
                        modPath=room_to_add["modPath"],
                        room_type=RoomType(room_to_add["room_type"]),
                        number_beds=int(room_to_add["number_beds"]),
                        rate=int(room_to_add["rate"]),
                        balcony=YesNo(room_to_add["balcony"]),
                        city_view=YesNo(room_to_add["city_view"]),
                        ocean_view=YesNo(room_to_add["ocean_view"]),
                        smoking=YesNo(room_to_add["smoking"]),
                        available=Availability(room_to_add["available"]),
                        max_guests=int(room_to_add["max_guests"]),
                        wheelchair_accessible=YesNo(room_to_add["wheelchair_accessible"])
                    )
                )
                start+=int(room_to_add["num_rooms"])
        db.session.add_all(floors)
        db.session.add_all(rooms)
        db.session.commit()
