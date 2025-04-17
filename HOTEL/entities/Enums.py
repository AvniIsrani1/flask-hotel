from enum import Enum as PyEnum

class YesNo(PyEnum):
    """
    Enum representing Yes/No values.
    
    Used throughout the application where binary choices are required.
    """
    Y = 'Y'
    N = "N" 

class Locations(PyEnum):
    """
    Enum representing hotel location options.
    
    Defines the available locations for Ocean Vista hotels.
    """
    MALIBU = "Malibu"
    SM = "Santa Monica"

class RoomType(PyEnum):
    """
    Enum representing room type categories.
    
    Defines the different room types available for booking.
    """
    STRD = 'Standard'
    DLX = 'Deluxe'
    ST = 'Suite'

class Availability(PyEnum):
    """
    Enum representing room availability status.
    
    Defines the possible states for room availability.
    """
    A = 'Available'
    B = 'Booked'
    M = 'Maintenance'

class SType(PyEnum):
    """
    Enum representing service types.
    
    Defines the categories of services that can be requested.
    """
    I = 'Items'
    H = 'Housekeeping'
    T = 'Trash'
    C = 'Call'
    D = 'Dining'
    A = 'Assistance'
    O = 'Other'

class Assistance(PyEnum):
    """
    Enum representing assistance request types.
    
    Defines the categories of assistance that guests can request.
    """
    L = 'recommendations'
    B = 'transportation'
    R = 'maintenance'
    A = 'accessibility'

class Status(PyEnum):
    """
    Enum representing request status values.
    
    Defines the possible states for service requests.
    """
    N = 'Not Started'
    I = 'In-Progress'
    C = 'Complete'