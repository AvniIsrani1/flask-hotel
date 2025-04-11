from .Enums import YesNo
from ..db import db
from werkzeug.security import generate_password_hash, check_password_hash


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
    
    @classmethod
    def create_initial_user(cls,name,email,password):
        return cls(name=name,email=email,password=generate_password_hash(password))

    def update_profile(self, name=None, phone=None, address_line1=None, address_line2=None, city=None, state=None, zipcode=None):
        self.name = name
        self.phone = phone
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        if self.name and self.phone: #what information do we most want from user??
            self.first_login = YesNo.N

    def update_notifications(self, text_notifications, email_notifications):
        self.text_notifications = text_notifications
        self.email_notifications = email_notifications
    
    def verify_password(self, entered_password):
        return check_password_hash(self.password, entered_password)
    
    def change_password(self, new_password):
        self.password = generate_password_hash(new_password)
