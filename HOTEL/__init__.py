from flask import Flask, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, distinct, Computed
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum as PyEnum
from urllib.parse import quote
import boto3
from botocore.exceptions import ClientError
import json



app = Flask(__name__,
            static_folder='static',     # Define the static folder (default is 'static')
            template_folder='templates')
app.secret_key = 'GITGOOD_12345'  # This key keeps your session data safe.
# pwd = 'UFxP|gQtX_Ft>(ru.z[rVW1kiHX>'
# pwd = quote(pwd)

secret_name = "rds!db-d319020b-bb3f-4784-807c-6271ab3293b0"
client = boto3.client(service_name='secretsmanager', region_name='us-west-1')

# Retrieve the secret from Secrets Manager
try:
    response = client.get_secret_value(SecretId=secret_name)
except ClientError as e:
    raise e
secret = json.loads(response['SecretString'])
username=secret.get("username")
pwd = quote(secret.get("password"))



app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{pwd}@hotel-db-instance.cvwasiw2g3h6.us-west-1.rds.amazonaws.com:3306/hotel_db'
# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Define the User model/table
class YesNo(PyEnum):
    Y = 'Y'
    N = "N"
class Locations(PyEnum):
    MALIBU = "Malibu"
    SM = "Santa Monica"
class RoomType(PyEnum):
    STRD = 'standard'
    DLX = 'deluxe'
    ST = 'suite'
class Availability(PyEnum):
    A = 'available'
    B = 'booked'
    M = 'maintenance'


class User(db.Model):
    __tablename__ = 'user'  # Name of the table in the database
    id = db.Column(db.Integer, primary_key=True)  # Unique id for each user
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
    room_number = db.Column(db.String(15), default="")
    first_login = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.Y) 
    text_notifications = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    email_notifications = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    bookings = db.relationship('Booking', backref='user', lazy=True) #user is keeping track of bookings


class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Enum(Locations), nullable=False) 
    #services
    free_wifi = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.Y) 
    free_breakfast = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    pool = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    gym = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    golf = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    rooms = db.relationship('Room', backref='hotel', lazy=True, cascade='all, delete-orphan') #hotel is keeping track of rooms

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True) #room number (floornum(1) then roomnum(2))
    hid = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    img = db.Column(db.String(200), nullable=False)
    room_type = db.Column(db.Enum(RoomType),nullable=False,default=RoomType.STRD)
    number_beds = db.Column(db.Integer,default=1)
    rate = db.Column(db.Integer, nullable=False)
    available = db.Column(db.Enum(Availability),nullable=False,default=Availability.A)
    max_guests = db.Column(db.Integer,default=2,nullable=False)
    num_guests = db.Column(db.Integer)
    wheelchair_accessible = db.Column(db.Enum(YesNo), nullable=False, default=YesNo.N) 
    bookings = db.relationship('Booking', backref='room', lazy=True, cascade='all, delete-orphan')  


class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'))
    room_num = db.Column(db.Integer, db.ForeignKey('room.id'))
    check_in = db.Column(DateTime)
    check_out = db.Column(DateTime)
    fees = db.Column(db.Integer, default=50)

class FAQ(db.Model):
    __tablename__ = 'faq'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(150), nullable=False)
    answer = db.Column(db.String(500), nullable=False)



# Create all database tables (if they don't exist already)
with app.app_context():
    db.create_all()

# ----- Routes -----

# Home page route
@app.route("/")
def home():
    locations = db.session.query(distinct(Hotel.location)).all()
    return render_template("home.html", locations=locations)

# Sign Up route: Display form on GET, process form on POST
@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("sign_up"))
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please use a different email or login.", "error")
            return redirect(url_for("sign_up"))
        
        # Hash the password before storing for security
        hashed_pw = generate_password_hash(password)
        
        # Create a new user instance
        new_user = User(name=name, email=email, password=hashed_pw)
        
        try:
            # Save the new user to the database
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("log_in"))
        except Exception as e:
            # Roll back the session if there is an error
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("sign_up"))
    
    return render_template("signup.html")

# Login route: Display form on GET, process form on POST
@app.route("/login", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and if the password is correct
        if user and check_password_hash(user.password, password):
            # Save user's id and name in session so we know they are logged in
            session["user_id"] = user.id
            session["user_name"] = user.name
            if user.first_login == YesNo.Y:
                return redirect(url_for('profile'))
            else:
                flash("Logged in successfully!", "success")
                return redirect(url_for("home"))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for("log_in"))
    
    return render_template("login.html")

# Logout route: Clear the session and log the user out
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# Profile route: Only accessible if the user is logged in
@app.route("/profile",methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    user = User.query.get(session["user_id"])
    if user.first_login is YesNo.Y:
        flash("Please update your profile information!", "action")
    message = ''
    status = ''
    if request.method == "POST":
        ptype = request.form.get('ptype')
        if ptype == 'profile':
            user.name = request.form.get("name")
            user.phone = request.form.get("phone")
            user.address_line1 = request.form.get("address")
            user.address_line2 = request.form.get("address2")
            user.city = request.form.get("city")
            user.state = request.form.get("state")
            user.zipcode = request.form.get("zipcode")
            user.first_login = YesNo.N
            message = 'Profile has been updated!'
            status = 'success'
        elif ptype=='notifications':
            tremind = request.form.get('tremind')
            eremind = request.form.get('eremind')
            if tremind:
                user.text_notifications = YesNo.Y
            else:
                user.text_notifications = YesNo.N
            if eremind:
                user.email_notifications = YesNo.Y
            else:
                user.email_notifications = YesNo.N
            print('update notfi')
        elif ptype=='password_change':
            print('change pass')
            cur_password = request.form.get("cur_pass")
            if check_password_hash(user.password, cur_password):
                new_password = request.form.get("new_pass")
                user.password = generate_password_hash(new_password)
                message = 'Password has been changed.'
                status = 'success'
            else:
                message = 'Unable to update password.'
                status = 'error'
        elif ptype=='account_deletion':
            db.session.delete(user)
            session.clear()
            db.session.commit()
            return render_template("home.html")
        try:
            db.session.commit()
            flash(message, status)
        except Exception as e:
            # Roll back the session if there is an error
            db.session.rollback()
            flash(f"An error occurred: {str(e)}. Please try again later.", "error")
        finally:
            return redirect(url_for("profile"))
    # Retrieve the logged-in user's information from the database
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user, YesNo = YesNo)

@app.route("/bookings", methods=["GET", "POST"])
def bookings():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    return render_template('bookings.html')

@app.route("/request-services")
def request_services():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    return render_template('request_services.html')

@app.route("/search", methods=["GET", "POST"])
def search():
    locations = db.session.query(distinct(Hotel.location)).all()
    return render_template('search.html',locations=locations)

@app.route("/terms")
def terms():
    return render_template('terms.html')

@app.route("/faq")
def faq():
    return render_template('faq.html')

from datetime import datetime, timedelta

# Credit Card Validation Class
class CreditCard:
    def __init__(self, credit_card_number, exp_date, cvv):  # Step 1
        self.credit_card_number = credit_card_number.replace('-','').replace(' ','')  # Step 2

        if "/" not in exp_date and len(exp_date) == 4:
            exp_date = exp_date[:2] + "/" + exp_date[2:]
        self.exp_date = exp_date
        
        self.cvv = cvv
        
    def validate_CC(self):
        # First check if the card number has valid digits
        if not self.credit_card_number.isdigit():
            return False
            
        sum_odd_digits = 0
        sum_even_digits = 0
        total = 0
        
        reverse_credit_card_number = self.credit_card_number[::-1]  # Step 3

        for x in reverse_credit_card_number[::2]:
            sum_odd_digits += int(x)

        for x in reverse_credit_card_number[1::2]:  # Step 4
            x = int(x) * 2 

            if x >= 10:
                sum_even_digits += (1 + (x % 10))
            else:
                sum_even_digits += x
            
        total = sum_odd_digits + sum_even_digits  # Step 5
        return total % 10 == 0  # Step 6
    
    def validate_exp_date(self):
        try:
            exp_month, exp_year = map(int, self.exp_date.split('/'))
            exp_year += (2000 if exp_year < 100 else 0)

            now = datetime.now()

            return exp_year > now.year or (exp_year == now.year and exp_month >= now.month)
        
        except Exception:
            return False
        
    def validate_cvv(self):
        if self.credit_card_number and self.credit_card_number[0] == '3':
            return len(self.cvv) == 4 and self.cvv.isdigit()
        else:
            return len(self.cvv) == 3 and self.cvv.isdigit()   
        
    def is_valid(self):
        return (self.validate_CC() and 
                self.validate_exp_date() and 
                self.validate_cvv())

# Add sample rooms if needed (run this after db.create_all())
def add_sample_data():
    """Add sample data to the database if tables are empty"""
    # Check if we have any rooms
    if not Room.query.first():
        print("Adding sample rooms")
        # First check if we have hotels
        if not Hotel.query.first():
            malibu_hotel = Hotel(location=Locations.MALIBU)
            sm_hotel = Hotel(location=Locations.SM)
            db.session.add(malibu_hotel)
            db.session.add(sm_hotel)
            db.session.commit()
        
        # Get hotel IDs
        malibu_id = Hotel.query.filter_by(location=Locations.MALIBU).first().id
        
        # Create sample rooms
        room1 = Room(
            hid=malibu_id,
            img="inside.jpeg",
            room_type=RoomType.DLX,
            number_beds=2,
            rate=150,
            available=Availability.A,
            max_guests=4
        )
        room2 = Room(
            hid=malibu_id,
            img="inside.jpeg", 
            room_type=RoomType.ST,
            number_beds=1,
            rate=250,
            available=Availability.A,
            max_guests=2
        )
        db.session.add(room1)
        db.session.add(room2)
        db.session.commit()
        print("Sample rooms added")

# Add this after db.create_all() in your __init__.py
with app.app_context():
    db.create_all()
    add_sample_data()

# Payment page route
@app.route("/payment")
def payment():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    return render_template('payment.html')

# Process payment route (form submission handling)
@app.route("/process-payment", methods=["POST"])
def process_payment():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    # Extract payment information from the form
    credit_card_number = request.form.get("card-number")
    exp_date = request.form.get("expiry")
    cvv = request.form.get("cvv")
    
    # Create a new CreditCard instance with the provided information
    new_credit_card = CreditCard(credit_card_number, exp_date, cvv)
    
    # Check individual validations to show specific errors
    validation_passed = True
    
    if not new_credit_card.validate_CC():
        validation_passed = False
        flash("INVALID CARD NUMBER \n\t The card number you have entered is either INCORRECT or INVALID.", "card_error")
        
    if not new_credit_card.validate_exp_date():
        validation_passed = False
        flash("INCORRECT EXPIRY DATE \n\t Expired or incorrectly formatted expiry date, use a '/' between the month and the year.", "date_error")
        
    if not new_credit_card.validate_cvv():
        validation_passed = False
        flash("Invalid CVV \n\t The security code should be 3 digits (4 for American Express cards).", "cvv_error")
    
    if validation_passed:
        # Card is valid, process the payment
        try:
            user_id = session.get("user_id")
            
            # Find a valid room to book (first available room)
            room = Room.query.filter_by(available=Availability.A).first()
            
            if not room:
                flash("No available rooms to book.", "database_error")
                return render_template('payment.html')
                
            # Set check-in and check-out dates
            check_in_date = datetime.now()
            check_out_date = check_in_date + timedelta(days=3)
            
            # Create a new booking record
            new_booking = Booking(
                uid=user_id,
                room_num=room.id,  # Use a valid room ID
                check_in=check_in_date,
                check_out=check_out_date,
                fees=50
            )
            
            # Update room availability
            room.available = Availability.B
            
            db.session.add(new_booking)
            db.session.commit()
            
            flash("YOUR CARD HAS BEEN ACCEPTED", "success")
            return redirect(url_for("my_bookings"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {str(e)}", "database_error")
            return render_template('payment.html')
    else:
        # Card is invalid, display appropriate error messages
        flash("INVALID CREDIT CARD DETAILS", "error")
        return render_template('payment.html')

if __name__ == "__main__":
    app.run(debug=True)