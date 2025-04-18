from datetime import datetime
from ..db import db
from sqlalchemy import DateTime, distinct, desc, asc, cast, func, not_, String, Computed

class RoomAvailability:
    """
    RoomAvailability class for managing room availability information and querying room availability within a given date range.
    This class handles the logic for finding rooms based on specific criteria and date ranges.
    """

    def __init__(self,startdate=None,enddate=None,rid=None):
        """
        Initialize a RoomAvailability object with optional start date, end date, and room ID.

        Args:
            startdate (str, optional): The starting date for availability check in "Month Day, Year" format.
            enddate (str, optional): The ending date for availability check in "Month Day, Year" format.
            rid (str, optional): The room ID to check for availability.

        Returns: 
            None
        """
        if startdate and enddate:
            self.get_start_end_duration(startdate,enddate)
        else:
            self.starting=self.ending=self.duration=None
        if rid:
            self.set_rid_room(rid)



    def get_start_end_duration(self,startdate, enddate):
        """
        Convert string date inputs to datetime objects and calculate stay duration.
        Check-in time is set to 15:00 (3 PM) on the start date.
        Check-out time is set to 11:00 (11 AM) on the end date.

        Args:
            startdate (str): The starting date in "Month Day, Year" format.
            enddate (str): The ending date in "Month Day, Year" format.
        Returns:
            None
        """
        self.starting = datetime.strptime(str(startdate), "%B %d, %Y").replace(hour=15,minute=0,second=0)
        self.ending = datetime.strptime(str(enddate), "%B %d, %Y").replace(hour=11,minute=0,second=0)
        self.duration = (self.ending - self.starting).days + 1
        

    def set_rid_room(self,rid):
        """
        Set the room ID and retrieve the corresponding room object.

        Args:
            rid (str): The room ID to set.
            
        Returns:
            None
        """
        from ..entities import Availability, Room,Hotel
        self.rid=rid
        self.room=Room.query.join(Hotel).filter(Room.available==Availability.A).filter(Room.id==rid).first()


    
    def get_similar_rooms(self,status): #status refers to if room is available within starting and ending periods
        """
        Retrieve rooms with similar characteristics to the current room.

        Args:
            status (str): Specifies whether to return only available rooms ('open') or all rooms ('any').

        Returns:
            Query: A SQLAlchemy query object containing similar rooms matching the criteria.
        """
        from ..entities import Availability, Bookings, Room, Hotel
        if not self.room:
            print("MUST SET ROOM ID!!!!!")
            return None
        similar_rooms = Room.query.join(Hotel).filter(
            Room.hid==self.room.hid, Room.room_type==self.room.room_type, Room.number_beds==self.room.number_beds, Room.rate==self.room.rate, Room.balcony==self.room.balcony, Room.city_view==self.room.city_view,
            Room.ocean_view==self.room.ocean_view, Room.smoking==self.room.smoking, Room.max_guests==self.room.max_guests, Room.wheelchair_accessible==self.room.wheelchair_accessible
        )
        if status=='open':
            similar_rooms = similar_rooms.filter(not_(db.exists().where(Bookings.rid == Room.id).where(Bookings.check_in < self.ending).where(Bookings.check_out>self.starting))).order_by(asc(Room.room_number))
        return similar_rooms



    def get_similar_quantities(self, status):
        """
        Get the count of rooms with similar characteristics.

        Args:
            status (str): Specifies whether to count only available rooms ('open') or all rooms ('any').

        Returns:
            Query: A SQLAlchemy query object containing the count of similar rooms, 
                   along with room and hotel information.
        """
        from ..entities import Room, Hotel #need to update this when move Room/Hotel to model_dbs
        similar_rooms = self.get_similar_rooms(status=status)
        if not similar_rooms:
            print("DID NOT GET ANY SIMILAR ROOMS!!")
            return None
        if status=='any':
            similar_rooms = similar_rooms.group_by(
                Room.hid, Room.room_type, Room.number_beds, Room.rate, Room.balcony, Room.city_view, Room.ocean_view, 
                Room.smoking, Room.max_guests, Room.wheelchair_accessible
            )
        similar_rooms = similar_rooms.with_entities(Room, Hotel.address, func.count(distinct(Room.id)).label('number_rooms'), func.min(Room.id).label('min_rid'))
        return similar_rooms


    def get_duration(self):
        """
        Get the duration of the stay in days.
        Args:
            None
        Returns:
            int: The number of days of the stay.
        """
        return self.duration

    
    def get_starting(self):
        """
        Get the starting datetime of the stay.
        Args:
            None
        Returns:
            datetime: The check-in datetime.
        """
        return self.starting


    def get_ending(self):
        """
        Get the ending datetime of the stay.
        Args:
            None
        Returns:
            datetime: The check-out datetime.
        """
        return self.ending


