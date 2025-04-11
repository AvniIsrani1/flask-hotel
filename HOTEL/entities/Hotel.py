from .Enums import YesNo, Locations, RoomType, Availability
from ..db import db
from .Floor import Floor
from .Room import Room

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


    @classmethod
    def get_hotel(cls, hid):
        return cls.query.filter_by(hid=hid).first()
        
    @classmethod
    def get_hotels_by_location(cls, location):
        return cls.query.filter_by(location=Locations(location)).all()
    
    def get_hotel_services(self):
        return {
            "free_wifi": self.free_wifi,
            "free_breakfast": self.free_breakfast,
            "pool": self.pool,
            "gym": self.gym,
            "golf": self.floors
        }
    
    def get_floors(self):
        return self.floors
    
    def get_rooms(self):
        return self.rooms
    
    def add_floor(self, number_floors, base_floor_number):
        floors = []
        for i in range(number_floors):
            floor = Floor(hid=self.id, floor_number=base_floor_number+i)
            floors.append(floor)
        return floors

    def add_layout(self, base_floor_number, number_floors, add_room_params):
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
