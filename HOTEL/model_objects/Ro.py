class Ro:
    def __init__(self, id=None, floor=None, hotel=None, room_number=None, img=None,
                 modPath=None, room_type=None, number_beds=1, rate=0, balcony=False, 
                 city_view=False, ocean_view=False, smoking=False, available=True, 
                 max_guests=2, wheelchair_accessible=False):
        self.id = id
        self.floor = floor
        self.hotel = hotel
        self.room_number = room_number
        self.img = img
        self.modPath = modPath
        self.room_type = room_type
        self.number_beds = number_beds
        self.rate = rate
        self.balcony = balcony
        self.city_view = city_view
        self.ocean_view = ocean_view
        self.smoking = smoking
        self.available = available
        self.max_guests = max_guests
        self.wheelchair_accessible = wheelchair_accessible
        self.bookings = []