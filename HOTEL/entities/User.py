from .Enums import YesNo
from ..db import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """
    A table for storing user information and profile settings.

    Maintains a 2-way relationship with the Bookings table.

    Note:
        Author: Devansh Sharma, Avni Israni
        Documentation: Avni Israni
        Created: March 1, 2025
        Modified: April 17, 2025
    """
    __tablename__ = 'users'  # Name of the table in the database
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Unique id for each user
    type = db.Column(db.String(50)) #keep track of type of user
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
    bookings = db.relationship('Booking', backref='users', lazy=True, cascade='all, delete-orphan') #user is keeping track of bookings

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }
    
    @classmethod
    def get_user(cls, id):
        """
        Retrieve a user by their unique ID.

        Parameters: 
            id (int): The unique ID of the user.

        Returns:
            User | None: The User object if found, else None.
        """
        return cls.query.filter(cls.id==id).first()
    
    def get_name(self):
        """
        Retrieve a user's name.

        Parameters: 
            None

        Returns:
            str | None: The name of the user if found, else None.
        """
        return self.name
    
    @classmethod
    def get_user_by_email(cls,email):
        """
        Retrieve a user by their unique email address.

        Parameters:
            email (str): The email address to check for.
        
        Returns:
            User | None: The User object if found, else None    
        """
        return cls.query.filter(cls.email==email).first()
    
    @classmethod
    def unique_email(cls,email):
        """
        Check if the email specified is unique among all users.
        
        Parameters:
            email (str): The email address to search for.

        Returns:
            bool: True if the email address is unique, else False
        """
        return cls.get_user_by_email(email) is None
    
    @classmethod
    def create_initial_user(cls,name,email,password):
        """
        Create a new User object with hashed password.

        Parameters:
            name (str): The name of the user.
            email (str): The unique email address of the user.
            password (str): The password of the user in plaintext.

        Returns:
            User: A new User object with the provided name, email, and hashed password.
        """
        return cls(name=name,email=email,password=generate_password_hash(password))

    def update_profile(self, name=None, phone=None, address_line1=None, address_line2=None, city=None, state=None, zipcode=None):
        """
        Update the user's profile information. 
        If name and phone are provided, the user's first_login is set to YesNo.N.

        Parameters:
            name (str, optional): Updated name.
            phone (str, optional): Updated phone number.
            address_line1 (str, optional): Updated address line 1.
            address_line2 (str, optional): Updated address line 2.
            city (str, optional): Updated city.
            state (str, optional): Updated state.
            zipcode (str, optional): Updated zipcode.
        
        Returns:
            None

        """
        self.name = name
        self.phone = phone
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        if self.name and self.phone: 
            self.first_login = YesNo.N

    def update_notifications(self, text_notifications, email_notifications):
        """
        Update the user's notification settings.

        Parameters:
            text_notifications (YesNo): New text notification setting.
            email_notifications (YesNo): New email notification setting.

        Returns:
            None
        """
        self.text_notifications = text_notifications
        self.email_notifications = email_notifications
    
    def verify_password(self, entered_password):
        """
        Check if the user's saved password matches the entered password.

        Parameters:
            entered_password (str): The plaintext password to verify.

        Returns:
            bool: True if the entered password matches the user's password, else False
        """
        return check_password_hash(self.password, entered_password)
    
    def change_password(self, new_password):
        """
        Update the user's password after hashing the new password.

        Parameters:
            new_password (str): The plaintext password to update to.

        Returns:
            None
        """
        self.password = generate_password_hash(new_password)
