from sqlalchemy import DateTime, distinct, desc, asc, cast, func, not_, String, Computed
from datetime import datetime, timedelta
from ..models import Hotel, Room
from ..model_dbs import Bookings, Locations, YesNo, RoomType,Availability
from ..db import db

class SearchController:

    def __init__(self):
        self.query=Room.query.join(Hotel).filter(Room.available==Availability.A)
    
    def main_search(self,location=None,start=None,end=None):
        if not start and not end: #only time this can happen is when user clicks to search page via home search bar or search button (otherwise always have at least start)
            starting = datetime.now().strftime("%B %d, %Y")
            ending = (datetime.now() + timedelta(days=1)).strftime("%B %d, %Y")
            return starting,ending,False
        if location:
            location = Locations(location)
            self.query = self.query.filter(Hotel.location == location)
        if start:
            starting = datetime.strptime(str(start), "%B %d, %Y").replace(hour=15,minute=0,second=0) #check in is at 3:00 PM
            ending = (starting + timedelta(days=1)).replace(hour=11,minute=0,second=0)
        if end: 
            ending = datetime.strptime(str(end), "%B %d, %Y").replace(hour=11,minute=0,second=0) #check out is at 11:00 AM
            if not start: #impossible to have only end (must have at least start) (will never reach this condition)
                starting = (ending - timedelta(days=1)).replace(hour=15,minute=0,second=0)
        self.query = self.query.filter(not_(db.exists().where(Bookings.rid == Room.id).where(Bookings.check_in < ending).where(Bookings.check_out>starting)))
        return starting,ending,True
    
    def filter_search(self,room_type=None,bed_type=None,view=None,balcony=None,smoking_preference=None,accessibility=None,price_range=None):
        if room_type:
            room_type = RoomType(room_type)
            self.query = self.query.filter(Room.room_type == room_type)
        if bed_type:
            self.query = self.query.filter(Room.number_beds == bed_type)
        if view:
            if view=='ocean':
                self.query = self.query.filter(Room.ocean_view==YesNo.Y)
            elif view=='city':
                self.query = self.query.filter(Room.city_view==YesNo.Y)
        if balcony:
            if balcony=='balcony':
                self.query = self.query.filter(Room.balcony==YesNo.Y)
            elif balcony=='no_balcony':
                self.query = self.query.filter(Room.balcony==YesNo.N)
        if smoking_preference:
            if smoking_preference == 'Smoking':
                smoking_preference = YesNo.Y
            else:
                smoking_preference = YesNo.N
            self.query = self.query.filter(Room.smoking == smoking_preference)
        if accessibility:
            accessibility = YesNo.Y
            self.query = self.query.filter(Room.wheelchair_accessible == accessibility)
        if price_range:
            price_range = int(price_range)
            self.query = self.query.filter(Room.rate <= price_range)
    
    def sort_search(self,sort):
        if sort=='priceL':
            self.query = self.query.order_by(Room.rate.asc())
        elif sort=='priceH':
            self.query = self.query.order_by(Room.rate.desc())
    
    def get_quantities(self):
        self.query = self.query.group_by(
            Room.hid, Room.room_type, Room.number_beds, Room.rate, Room.balcony, Room.city_view, Room.ocean_view, 
            Room.smoking, Room.max_guests, Room.wheelchair_accessible
        )
        self.query = self.query.with_entities(Room, func.count(distinct(Room.id)).label('number_rooms'), func.min(Room.id).label('min_rid'))

    def get_search(self):
        return self.query.all()