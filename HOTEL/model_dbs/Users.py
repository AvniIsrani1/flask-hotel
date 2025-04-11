from ..model_objects import Booking, User
from .Enums import YesNo
from ..db import db

class Users(db.Model):
    __tablename__ = 'users'  # Name of the table in the database
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique id for each user
    name = db.Column(db.String(150), nullable=False)  # User's name
    email = db.Column(db.String(150), unique=True, nullable=False)  # User's email (must be unique)
    password = db.Column(db.String(255), nullable=False)  # Hashed password
    phone = db.Column(db.String(15))
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    zipcode = db.Column(db.String(10))
    rewards = db.Column(db.Integer,default=0)
    first_login = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.Y) 
    text_notifications = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    email_notifications = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    bookings = db.relationship('Bookings', backref='users', lazy=True, cascade='all, delete-orphan') #user is keeping track of bookings
    
    @classmethod
    def get_user(cls, id):
        return cls.query.filter(cls.id==id).first()
    
    @classmethod
    def get_user_by_email(cls,email):
        return cls.query.filter(cls.email==email).first()
    
    @classmethod
    def unique_email(cls,email):
        return cls.get_user_by_email(email) is None
    
    def create_user_object(self):
        from .Bookings import Bookings 
        booking_objs = db.session.query(Bookings).filter_by(uid=self.id).all()
        booking_list = [booking.create_booking_object() for booking in booking_objs] if booking_objs else []
        return User(id=self.id,name=self.name, email=self.email, password=self.password,phone=self.phone,
                    address_line1=self.address_line1, address_line2=self.address_line2, city=self.city,
                    state=self.state, zipcode=self.zipcode, rewards=self.rewards,
                    first_login=self.first_login==YesNo.Y,
                    text_notifications=self.text_notifications==YesNo.Y, 
                    email_notifications=self.email_notifications==YesNo.Y,
                    bookings=booking_list
        )
    
    @classmethod
    def update_users_db(cls, user):
        model=cls.query.get(user.id)
        if model:
            model.name = user.name
            model.email = user.email
            model.password = user.password
            model.phone = user.phone
            model.address_line1 = user.address_line1
            model.address_line2 = user.address_line2
            model.city = user.city
            model.state = user.state
            model.zipcode = user.zipcode
            model.rewards = user.rewards
            model.first_login = YesNo.Y if user.first_login else YesNo.N
            model.text_notifications = YesNo.Y if user.text_notifications else YesNo.N
            model.email_notifications = YesNo.Y if user.email_notifications else YesNo.N
            # model.bookings = user.bookings #not correct for bookings
            return True
        return False
    
    @classmethod
    def create_user_db(cls, user): #create a SINGLE user at a time
        return cls(
            name=user.name,email=user.email,password=user.password,phone=user.phone,
            address_line1=user.address_line1,address_line2=user.address_line2,city=user.city,
            state=user.state,zipcode=user.zipcode,rewards=user.rewards,
            first_login=YesNo.Y if user.first_login else YesNo.N,
            text_notifications=YesNo.Y if user.text_notifications else YesNo.N,
            email_notifications=YesNo.Y if user.email_notifications else YesNo.N
        )

    