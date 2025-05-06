"""
Enums to simplify data representation. 

This module helps validate data consistently. 

Note:
    Author: Avni Israni
    Documentation: Devansh Sharma
    Created: March 6, 2025
    Modified: April 28, 2025
"""

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
    Enum representing service requests types. 

    Defines the types of services that can be requested. 
    """
    I = 'Items Needed'
    H = 'Housekeeping'
    T = 'Trash Cleanup'
    C = 'Wake-Up Call'
    D = 'Dining Reservation'
    A = 'Assistance Needed'
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
    E = 'Expired'
    # CA = 'Canceled'

class Position(PyEnum):
    """
    Enum representing position types for staff. 

    Defines the types of positions staff can hold and associated colors for each position. 
    """
    MANAGER = ("Manager","blue")
    FRONT_DESK = ("Front Desk", "green")
    HOUSEKEEPING = ("Housekeeping", "purple")
    MAINTENANCE = ("Maintenance", "gray")
    CONCIERGE = ("Concierge", "brown")
    CHEF = ("Chef", "orange")
    SERVER = ("Server", "yellow")

    def __init__(self, label, color):
        self.label = label
        self.color = color
