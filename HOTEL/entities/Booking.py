from sqlalchemy import DateTime, distinct, Computed, asc, desc, func, literal, or_, and_
from datetime import datetime
from .Enums import YesNo
from ..db import db


class Booking(db.Model):
    """
    A table for storing reservation details. 

    Has a foreign key to the Users and Rooms tables.
    Has a 2-way relationship with the Services table.

    Note:
        Author: Avni Israni
        Documentation: Avni Israni
        Created: March 6, 2025
        Modified: April 17, 2025
    """
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    uid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rid = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    check_in = db.Column(DateTime, nullable=False)
    check_out = db.Column(DateTime, nullable=False)
    fees = db.Column(db.Integer, default=50) #the total price for the stay
    cancel_date = db.Column(DateTime)
    refund_type = db.Column(db.Enum(YesNo)) 
    special_requests = db.Column(db.String(1000))
    name = db.Column(db.String(150),nullable=False)
    email = db.Column(db.String(150),nullable=False)
    phone = db.Column(db.String(15),nullable=False)
    num_guests = db.Column(db.Integer, default=1)
    services = db.relationship('Service', backref='users', lazy=True, cascade='all, delete-orphan')

    def update_booking(self, special_requests, name, email, phone, num_guests):
        """
        Update booking details.

        Parameters: 
            special_requests (str): The special requests made by the user.
            name (str): The name the booking is made under.
            email (str): The email address specified by the user.
            phone (str): The phone number specified by the user.
            num_guests (str): The number of guests.

        Returns:
            None
        """
        self.special_requests = special_requests
        self.name = name
        self.email = email
        self.phone = phone
        self.num_guests=num_guests

    def full_refund(self):
        """
        Check if a full refund should be issued upon cancellation.

        Parameters:
            None

        Returns:
            YesNo: YesNo.N if check_in is within 2 days of today, else YesNo.Y.
        """
        today = datetime.now()
        if (self.check_in - today).days >= 2:
            return YesNo.Y
        return YesNo.N
    
    def cancel(self):
        """
        Cancel the booking.

        Parameters:
            None

        Returns:
            None
        """
        today = datetime.now()
        self.refund_type = self.full_refund()
        self.cancel_date = today

    @classmethod
    def add_booking(cls, uid, rid, check_in, check_out, fees, special_requests, name, email, phone, num_guests):
        """
        Create and commit a booking
        
        Parameters:
            uid (int): The unique ID of the user.
            rid (int): The unique ID of the room to reserve.
            check_in (datetime): The check in date.
            check_out (datetime): The check out date.
            fees (int): The flat rate per night. 
            special_requests (str): Special requests made by the user.
            name (str): The name the booking is under.
            email (str): The email address specified by the user.
            phone (str): The phone number specified by the user.
            num_guests (str): The number of guests.
        
        Returns:
            None
        """
        duration = (check_out - check_in).days + 1
        total_price = fees*duration*1.15 + 30 #NEED TO CHECK THIS LOGIC!!
        print('total',total_price)
        booking = cls(uid=uid, rid=rid, check_in=check_in, check_out=check_out, fees=total_price, special_requests=special_requests, name=name, email=email, phone=phone, num_guests=num_guests)
        return booking

    @classmethod
    def get_booking(cls, id):
        """
        Retrieve a booking by its unique ID.

        Parameters:
            id (int): The unique ID of the booking.

        Returns:
            Booking | None: The Booking object if found, else None.
        """
        return cls.query.get(id)

    @classmethod
    def get_current_user_bookings(cls,uid):
        """
        Retrieve a user's current (active) bookings.
        
        Parameters:
            uid (int): The unique ID of the user.
        
        Returns:
            list[Booking]: A list of the user's current (active) bookings.
        """
        today = datetime.now()
        return cls.query.filter(cls.uid==uid, cls.check_in<=today, cls.check_out>=today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out)).all()

    @classmethod
    def get_specific_current_user_bookings(cls,uid,bid):
        """
        Retrieve a user's booking by its unique ID.

        Parameters:
            uid (int): The unique ID of the user.
            bid (int): The unique ID of the booking.

        Returns:
            Booking | None: The Booking object if found, else None.
        """
        today = datetime.now()
        return cls.query.filter(cls.uid==uid, cls.id==bid, cls.check_in<=today,cls.check_out>=today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out)).first()

    @classmethod
    def get_future_user_bookings(cls,uid):
        """
        Retrieve a user's future bookings. 

        Parameters:
            uid (int): The unique ID of the user.
        
        Returns:
            list[Booking]: A list of the user's future bookings.
        """
        today = datetime.now()
        return cls.query.filter(cls.uid==uid,cls.check_in>today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out)).all()
    
    @classmethod
    def get_past_user_bookings(cls,uid):
        """
        Retrieve a user's past, completed bookings.

        Parameters:
            uid (int): The unique ID of the user.

        Returns:
            list[Booking]: A list of the user's past, completed bookings.
        """
        today = datetime.now()
        return cls.query.filter(cls.uid==uid, cls.check_out<today, cls.cancel_date.is_(None)).order_by(asc(cls.check_in), asc(cls.check_out)).all()
    
    @classmethod
    def get_canceled_user_bookings(cls,uid):
        """
        Retrieve a user's cancelled bookings. 

        Parameters:
            uid (int): The unique ID of the user.

        Returns:
            list[Booking]: A list of the user's cancelled bookings.
        """
        return cls.query.filter(cls.uid==uid, cls.cancel_date.isnot(None)).order_by(desc(cls.check_in), asc(cls.check_out)).all()
    


    @classmethod
    def get_booking_stats(cls, location=None, startdate=None, enddate=None):
        from .Room import Room
        from .Hotel import Hotel
        today = datetime.now()
        completed = cls.query.filter(cls.cancel_date.is_(None)).join(Room).join(Hotel)
        if location:
            completed = completed.filter(Hotel.location == location)
        if startdate and enddate: #completed refers to bookings fully completed within the startdate and enddate
            print('time period',startdate, enddate)
            completed = completed.filter(cls.check_in >= startdate, cls.check_out <= enddate)
        else:
            completed = completed.filter(cls.check_out <= today)
        completed = completed.with_entities(literal('Completed').label('status'), func.sum(cls.fees).label('total_fees'), func.count(distinct(cls.id)).label('total_bookings')).first()

        pending = cls.query.filter(cls.cancel_date.is_(None)).join(Room).join(Hotel)
        if location:
            pending = pending.filter(Hotel.location == location)
        if startdate and enddate: #pending refers to future bookings (after enddate)
            pending = pending.filter(
                or_(
                    cls.check_out > enddate
                )
            )
        else:
            pending = pending.filter(cls.check_out > today)
        pending = pending.with_entities(literal('Pending').label('status'), func.sum(cls.fees).label('total_fees'), func.count(distinct(cls.id)).label('total_bookings')).first()
        return [completed, pending]
    
    @classmethod
    def get_room_popularity_stats(cls, location=None, startdate=None, enddate=None):
        from .Room import Room
        from .Hotel import Hotel
        popularity = cls.query.filter(cls.cancel_date.is_(None)).join(Room).join(Hotel)
        if location:
            popularity = popularity.filter(Hotel.location==location)
        if startdate and enddate: #check in during time period, check out during time period, or check in and out during time period
            popularity = popularity.filter(
                    or_(
                        and_(cls.check_in >= startdate, cls.check_in <= enddate),
                        and_(cls.check_out >= startdate, cls.check_out <= enddate),
                        and_(cls.check_in <= startdate, cls.check_out >= enddate)
                    )
            )         
        popularity = popularity.group_by(Room.hid, Room.room_type, Room.number_beds, Room.rate, Room.balcony, Room.city_view, Room.ocean_view, 
                                     Room.smoking, Room.max_guests, Room.wheelchair_accessible)
        popularity = popularity.with_entities(func.min(cls.rid).label('rid'), func.count(cls.rid).label('popularity')).order_by(desc('popularity')).all()
        print(popularity)
        return popularity