from enum import Enum as PyEnum

class YesNo(PyEnum):
    Y = 'Y'
    N = "N"
class Locations(PyEnum):
    MALIBU = "Malibu"
    SM = "Santa Monica"
class RoomType(PyEnum):
    STRD = 'Standard'
    DLX = 'Deluxe'
    ST = 'Suite'
class Availability(PyEnum):
    A = 'Available'
    B = 'Booked'
    M = 'Maintenance'
class SType(PyEnum):
    I = 'Items Needed'
    H = 'Housekeeping'
    T = 'Trash Cleanup'
    C = 'Wake-Up Call'
    D = 'Dining Reservation'
    A = 'Assistance Needed'
    O = 'Other'
class Assistance(PyEnum):
    L = 'recommendations'
    B = 'transportation'
    R = 'maintenance'
    A = 'accessibility'
class Status(PyEnum):
    N = 'Not Started'
    I = 'In-Progress'
    C = 'Complete'