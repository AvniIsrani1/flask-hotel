from sqlalchemy import DateTime, distinct, desc, asc, cast, func, not_, String, Computed
from datetime import datetime, timedelta
from ..entities import Hotel, Floor, Room, Booking, Locations, YesNo, RoomType,Availability
from ..db import db

class SearchController:
    """
    A class for handling search functionality throughout the application.
    This controller manages the querying and filtering of room availability based on various criteria.

    Note: 
        Author: Avni Israni
        Documentation: Andrew Ponce
        Created: March 17, 2025
        Modified: April 17, 2025
    """

    def __init__(self):
        """
        Initialize a SearchController object with a base query for available rooms.
        
        Args:
            None
            
        Returns:
            None
        """
        self.query=Room.query.join(Hotel).filter(Room.available==Availability.A)
    
    def main_search(self,location=None,start=None,end=None):
        """
        Perform the main search based on location and date parameters.
        Sets up date ranges for search and filters rooms based on location and availability during the specified date range.
        
        Args:
            location (str, optional): The location identifier to search for.
            start (str, optional): The starting date in "Month Day, Year" format.
            end (str, optional): The ending date in "Month Day, Year" format.
            
        Returns:
            tuple: A tuple containing:
                datetime: starting - The starting date.
                datetime: ending - The ending date.
                bool: valid - True if search parameters were provided, False if defaults were used. 
        """
        valid = True
        if not start and not end: #only time this can happen is when user clicks to search page via home search bar or search button (otherwise always have at least start)
            starting = datetime.now().strftime("%B %d, %Y")
            ending = (datetime.now() + timedelta(days=1)).strftime("%B %d, %Y")
            valid = False
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
        self.query = self.query.filter(not_(db.exists().where(Booking.rid == Room.id).where(Booking.check_in < ending).where(Booking.check_out>starting)))
        return starting,ending,valid
    
    def filter_search(self,room_type=None,bed_type=None,view=None,balcony=None,smoking_preference=None,accessibility=None,price_range=None):
        """
        Apply additional filters to the search query based on various room criteria.
        
        Args:
            room_type (str, optional): The type of room to filter by.
            bed_type (str, optional): The bed type or count to filter by.
            view (str, optional): The view type to filter by ('ocean' or 'city').
            balcony (str, optional): The balcony preference to filter by ('balcony' or 'no_balcony').
            smoking_preference (str, optional): The smoking preference to filter by ('Smoking' or 'Non-Smoking').
            accessibility (str, optional): The accessibility requirement to filter by.
            price_range (str, optional): The maximum price to filter by.
            
        Returns:
            None
        """
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
        """
        Sort the search results based on specified criteria.
        
        Args:
            sort (str): The sorting parameter ('priceL' for ascending price, 'priceH' for descending price).
            
        Returns:
            None
        """
        if sort=='priceL':
            self.query = self.query.order_by(Room.rate.asc())
        elif sort=='priceH':
            self.query = self.query.order_by(Room.rate.desc())


    
    def get_quantities(self):
        """
        Group the search results and count the number of rooms for each unique combination of characteristics.
        This method modifies the query to include counts and minimum room IDs for each group.
        
        Args:
            None
            
        Returns:
            None
        """
        self.query = self.query.group_by(
            Room.hid, Room.room_type, Room.number_beds, Room.rate, Room.balcony, Room.city_view, Room.ocean_view, 
            Room.smoking, Room.max_guests, Room.wheelchair_accessible
        )
        self.query = self.query.with_entities(Room, func.count(distinct(Room.id)).label('number_rooms'), func.min(Room.id).label('min_rid'))


    
    def get_search(self):
        """
        Execute the query and retrieve all matching results.
        
        Args:
            None
            
        Returns:
            list: A list of all matching room records based on the applied filters and sorting.
        """
        return self.query.all()

