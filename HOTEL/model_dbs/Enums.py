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
    I = 'Items'
    H = 'Housekeeping'
    T = 'Trash'
    C = 'Call'
    D = 'Dining'
    A = 'Assistance'
    O = 'Other'
class Assistance(PyEnum):
    L = 'recommendations'
    B = 'transportation'
    R = 'maintenance'
    A = 'accessibility'