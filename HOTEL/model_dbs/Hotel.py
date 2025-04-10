


from .Enums import YesNo, Locations
from ..db import db
from ..model_objects import Ho

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


    def create_hotel_object(self):
        return Ho(
             id=self.id,location=self.location,address=self.address,free_wifi=self.free_wifi,
             free_breakfast=self.free_breakfast,pool=self.pool,gym=self.gym,golf=self.golf
        ) #does not handle floors or rooms logic!!!
    
    @classmethod
    def create_hotels_db(cls, hotels):
        hotel_rows=[]
        for hotel in hotels:
            hotel_rows.append(
                cls(
                    location=hotel.location,address=hotel.address,free_wifi=hotel.free_wifi,free_breakfast=hotel.free_breakfast,
                    pool=hotel.pool,gym=hotel.gym,golf=hotel.golf
                )
            ) #does not handle floors or rooms logic!!!
        return hotel_rows

    @classmethod
    def update_bookings_db(cls, hotel):
        model=cls.query.get(hotel.id)
        if model:
            model.location=hotel.location
            model.address=hotel.address
            model.free_wifi=hotel.free_wifi
            model.free_break=hotel.free_breakfast
            model.pool=hotel.pool
            model.gym=hotel.gym
            model.golf=hotel.golf
            return True
        return False