from datetime import datetime
from ..db import db
from sqlalchemy import DateTime, distinct, desc, asc, cast, func, not_, String, Computed



class RoomAvailability:

    @staticmethod
    def get_start_end_duration(startdate, enddate):
        starting = datetime.strptime(str(startdate), "%B %d, %Y").replace(hour=15,minute=0,second=0)
        ending = datetime.strptime(str(enddate), "%B %d, %Y").replace(hour=11,minute=0,second=0)
        duration = (ending - starting).days + 1
        return starting, ending, duration

    @staticmethod
    def get_similar_rooms(rid, starting, ending, status): #status refers to if room is available within starting and ending periods
        from ..models import Room, Hotel #need to update this when move Room/Hotel to model_dbs
        from ..model_dbs import Availability, Bookings
        query = Room.query.join(Hotel).filter(Room.available==Availability.A)
        room = query.filter(Room.id==rid).first()
        similar_rooms = Room.query.join(Hotel).filter(
            Room.hid==room.hid, Room.room_type==room.room_type, Room.number_beds==room.number_beds, Room.rate==room.rate, Room.balcony==room.balcony, Room.city_view==room.city_view,
            Room.ocean_view==room.ocean_view, Room.smoking==room.smoking, Room.max_guests==room.max_guests, Room.wheelchair_accessible==room.wheelchair_accessible
        )
        if status=='open':
            similar_rooms = similar_rooms.filter(not_(db.exists().where(Bookings.rid == Room.id).where(Bookings.check_in < ending).where(Bookings.check_out>starting))).order_by(asc(Room.room_number))
        return similar_rooms

    @staticmethod
    def get_similar_quantities(rid, starting, ending, status):
        from ..models import Room, Hotel #need to update this when move Room/Hotel to model_dbs
        if status=='open':
            similar_rooms = RoomAvailability.get_similar_rooms(rid=rid, starting=starting, ending=ending, status='open')
        else:
            similar_rooms = RoomAvailability.get_similar_rooms(rid=rid, starting=starting, ending=ending, status='any')
        similar_rooms = similar_rooms.group_by(
            Room.hid, Room.room_type, Room.number_beds, Room.rate, Room.balcony, Room.city_view, Room.ocean_view, 
            Room.smoking, Room.max_guests, Room.wheelchair_accessible
        )
        similar_rooms = similar_rooms.with_entities(Room, Hotel.address, func.count(distinct(Room.id)).label('number_rooms'), func.min(Room.id).label('min_rid'))
        return similar_rooms
