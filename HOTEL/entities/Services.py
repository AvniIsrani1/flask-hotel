from ..db import db
from sqlalchemy import DateTime, distinct, Computed
from datetime import datetime, timedelta
from .Enums import YesNo, Assistance, SType, Status


class Services(db.Model):
    """
    Model representing service requests for bookings.
    
    This class manages various types of service requests that guests can make
    during their stay, including housekeeping, item requests, and assistance.

    Note:
        Author: Avni Israni
        Documentation: Devansh Sharma, Avni Israni
        Created: April 3, 2025
        Modified: April 17, 2025
    """
    __tablename__ = 'services'
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
    status = db.Column(db.Enum(Status), default=Status.N)

    @classmethod
    def add_item(cls, bid, robes=0, btowels=0, htowels=0, soap=0, shampoo=0, conditioner=0, wash=0, lotion=0, hdryer=0, pillows=0, blankets=0, sheets=0):
        """
        Create a new item request service.
        
        Args:
            bid (int): The booking ID associated with this service request.
            robes (int, optional): Number of robes requested. Defaults to 0.
            btowels (int, optional): Number of bath towels requested. Defaults to 0.
            htowels (int, optional): Number of hand towels requested. Defaults to 0.
            soap (int, optional): Number of soap bars requested. Defaults to 0.
            shampoo (int, optional): Number of shampoo bottles requested. Defaults to 0.
            conditioner (int, optional): Number of conditioner bottles requested. Defaults to 0.
            wash (int, optional): Number of body wash bottles requested. Defaults to 0.
            lotion (int, optional): Number of lotion bottles requested. Defaults to 0.
            hdryer (int, optional): Number of hair dryers requested. Defaults to 0.
            pillows (int, optional): Number of pillows requested. Defaults to 0.
            blankets (int, optional): Number of blankets requested. Defaults to 0.
            sheets (int, optional): Number of sheet sets requested. Defaults to 0.
            
        Returns:
            Services: A new service request object for items.
        """
        today = datetime.now()
        return cls(
            bid=bid,
            issued=today,
            stype=SType.I,
            robes=robes, btowels=btowels, htowels=htowels, soap=soap, shampoo=shampoo, conditioner=conditioner, wash=wash, lotion=lotion,
            hdryer=hdryer, pillows=pillows, blankets=blankets, sheets=sheets
        )
    
    @classmethod
    def add_housekeeping(cls, bid, housetime, validate_check_out):
        """
        Create a new housekeeping service request.
        
        Args:
            bid (int): The booking ID associated with this service request.
            housetime (time): The requested time for housekeeping.
            validate_check_out (datetime): The checkout date to validate against.
            
        Returns:
            Services: A new service request object for housekeeping if valid, None otherwise.
        """
        today = datetime.now()
        housedatetime = datetime.combine(today.date(), housetime)
        if housedatetime < today:
            housedatetime = today
        if housedatetime <= validate_check_out:
            return cls(id=id, bid=bid, issued=today, stype=SType.H, housedatetime=housedatetime)
    
    @classmethod
    def add_call(cls, bid, calltime, recurrent, validate_check_out):
        """
        Create one or more wake-up call service requests.
        
        Args:
            bid (int): The booking ID associated with this service request.
            calltime (time): The requested time for the wake-up call.
            recurrent (bool): Whether the call should recur daily until checkout.
            validate_check_out (datetime): The checkout date to validate against.
            
        Returns:
            list: A list of service request objects for wake-up calls if valid, empty list otherwise.
        """
        today = datetime.now()
        calls = []
        calldatetime = datetime.combine(today.date(), calltime)
        if calldatetime < today:
            calldatetime = calldatetime + timedelta(days=1)
        if calldatetime <= validate_check_out:
            if recurrent:
                while(calldatetime <= validate_check_out):
                    call = cls(bid=bid, issued=today, stype=SType.C, calldatetime=calldatetime)
                    calls.append(call)
                    calldatetime = calldatetime + timedelta(days=1)
            else:
                call = cls(bid=bid, issued=today, stype=SType.C, calldatetime=calldatetime)
                calls.append(call)
            return calls
        
    @classmethod
    def add_trash(cls, bid):
        """
        Create a new trash pickup service request.
        
        Args:
            bid (int): The booking ID associated with this service request.
            
        Returns:
            Services: A new service request object for trash pickup.
        """
        return cls(bid=bid, issued=datetime.now(), stype=SType.T, trash=YesNo.Y)

    @classmethod
    def add_dining(cls, bid, restaurant):
        """
        Create a new dining reservation service request.
        
        Args:
            bid (int): The booking ID associated with this service request.
            restaurant (str): The restaurant name for the reservation.
            
        Returns:
            Services: A new service request object for dining reservation.
        """
        return cls(bid=bid, issued=datetime.now(), stype=SType.D, restaurant=restaurant)
    
    @classmethod
    def add_assistance(cls, bid, assistance):
        """
        Create a new assistance service request.
        
        Args:
            bid (int): The booking ID associated with this service request.
            assistance (Assistance): The type of assistance needed.
            
        Returns:
            Services: A new service request object for assistance.
        """
        return cls(bid=bid, issued=datetime.now(), stype=SType.A, assistance=assistance)

    @classmethod
    def add_other(cls, bid, other):
        """
        Create a new custom service request.
        
        Args:
            bid (int): The booking ID associated with this service request.
            other (str): Description of the custom service request.
            
        Returns:
            Services: A new service request object for other services.
        """
        return cls(bid=bid, issued=datetime.now(), stype=SType.O, other=other)

    def update_status(self, new_status):
        """
        Update the status of a service request.
        
        Args:
            new_status (Status): The new status to set.
            
        Returns:
            bool: True if the status was updated successfully, False otherwise.
        """
        from ..entities.Enums import Status
        self.modified = datetime.now()
        if isinstance(new_status, Status):
            self.status = new_status
            return True
        return False