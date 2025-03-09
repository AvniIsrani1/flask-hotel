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

@app.route("/my-bookings")
def my_bookings():
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

@app.route("/bookings")
def bookings():
    return render_template('bookings.html')

@app.route("/search")
def search():
    return render_template('search.html')

@app.route("/terms")
def terms():
    return render_template('terms.html')

@app.route("/faq")
def faq():
    return render_template('faq.html')


if __name__ == "__main__":
    app.run(debug=True)