from ..db import db
from sqlalchemy import DateTime, Date, cast, distinct, Computed
from datetime import datetime, timedelta
from .Enums import YesNo, Assistance, SType, Status


class Services(db.Model):
    __tablename__ = 'services'
    """
    A table to keep track of service request information.
    Has a foreign key to the Bookings table.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bid = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False) 
    issued = db.Column(DateTime, nullable=False)
    modified = db.Column(DateTime)
    stype = db.Column(db.Enum(SType), nullable=False)
    robes = db.Column(db.Integer)
    btowels = db.Column(db.Integer)
    htowels = db.Column(db.Integer)
    soap = db.Column(db.Integer)
    shampoo = db.Column(db.Integer)
    conditioner = db.Column(db.Integer)
    wash = db.Column(db.Integer)
    lotion = db.Column(db.Integer)
    hdryer = db.Column(db.Integer)
    pillows = db.Column(db.Integer)
    blankets = db.Column(db.Integer)
    sheets = db.Column(db.Integer)
    housedatetime = db.Column(DateTime)
    trash = db.Column(db.Enum(YesNo)) 
    calldatetime = db.Column(DateTime)
    recurrent = db.Column(db.Enum(YesNo)) 
    restaurant = db.Column(db.String(200)) 
    assistance = db.Column(db.Enum(Assistance))
    other = db.Column(db.String(300)) 
    status = db.Column(db.Enum(Status),default=Status.N)

    @classmethod
    def add_item(cls, bid,robes=0, btowels=0, htowels=0, soap=0, shampoo=0, conditioner=0, wash=0, lotion=0, hdryer=0, pillows=0, blankets=0, sheets=0):
        """
        Create an request for items.

        Args:
            bid (int): The unique ID of the booking.
            robes (int): The number of robes requested.
            btowels (int): The number of bath towels requested.
            htowels (int): The number of hand towels requested.
            soap (int): The number of soaps requested.
            shampoo (int): The number of shampoo bottles requested.
            conditioner (int): The number of conditioner bottles requested.
            wash (int): The number of body wash bottles requested.
            lotion (int): The number of lotion bottles requested.
            hdryer (int): The number of hair dryers requested.
            pillows (int): The number of pillows requested.
            blankets (int): The number of blankets requested.
            sheets (int): The number of sheets requested. 

        Returns:
            Service: The item request.
        """
        today = datetime.now()
        return cls(
            bid=bid,
            issued=today,
            stype = SType.I,
            robes=robes, btowels=btowels, htowels=htowels, soap=soap, shampoo=shampoo, conditioner=conditioner, wash=wash, lotion=lotion,
            hdryer=hdryer, pillows=pillows, blankets=blankets, sheets=sheets
        )
    
    @classmethod
    def add_housekeeping(cls, bid, housetime, validate_check_out):
        """
        Create a request for housekeeping service.

        Args:
            bid (int): The unique ID of the booking.
            housetime (datetime): The 
        """
        today = datetime.now()
        housedatetime = datetime.combine(today.date(), housetime)
        if housedatetime < today:
            housedatetime = today
        if housedatetime <= validate_check_out: #this probably does not work, this method probably needs to be self instead!!!
            return cls(id=id, bid=bid, issued=today, stype=SType.H, housedatetime=housedatetime)
    
    @classmethod
    def add_call(cls, bid, calltime, recurrent, validate_check_out): #when calltime is recieved from form, it is of type time (not datetime)
        today = datetime.now()
        calls = []
        calldatetime = datetime.combine(today.date(), calltime)
        if calldatetime < today:
            calldatetime = calldatetime + timedelta(days=1)
        if calldatetime <= validate_check_out: #probably does not work (likely need self instead of cls for validate_check_out)
            if recurrent:
                while(calldatetime <= validate_check_out):
                    call = cls(bid=bid, issued=today, stype=SType.C, calldatetime=calldatetime)
                    calls.append(call)
                    calldatetime = calldatetime + timedelta(days=1)
            else:
                call = cls(bid=bid, issued=today, stype=SType.C, calldatetime=calldatetime)
                calls.append(call)
            return calls #calls is a list of Call objects!!
        
    @classmethod
    def add_trash(cls, bid):
        return cls(bid=bid, issued=datetime.now(), stype=SType.T, trash=YesNo.Y)

    @classmethod
    def add_dining(cls, bid, restaurant):
        return cls(bid=bid, issued=datetime.now(), stype=SType.D, restaurant=restaurant)
    
    @classmethod
    def add_assistance(cls,bid, assistance):
        return cls(bid=bid, issued=datetime.now(), stype=SType.A, assistance=assistance)

    @classmethod
    def add_other(cls,bid, other):
        return cls(bid=bid, issued=datetime.now(), stype=SType.O, other=other)

    def update_status(self, new_status):
        from ..entities.Enums import Status
        self.modified = datetime.now()
        if isinstance(new_status,Status):
            self.status = new_status
            return True
        return False
    