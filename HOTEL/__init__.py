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
from .models import db, User, Hotel, Floor, Room, Booking, FAQ, YesNo, Locations, RoomType, Availability



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
db.init_app(app)


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
    rooms = Room.query.all()
    if request.method == "POST":
        stype = request.form.get('stype')
        if stype == 'apply_search':
            location = request.form.get('location-type')
            start = request.form.get('startdate')
            end = request.form.get('enddate')
            query = Room.query.join(Hotel)
            print("finding hotel", location, " and ", Hotel.location , " and2 ", Hotel.location==location)
            if location:
                location = Locations(location)
                query = query.filter(Hotel.location == location)
            rooms = query.all()
        elif stype=='apply_filters':
            pass
    return render_template('search.html',locations=locations, rooms=rooms, YesNo = YesNo)

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
        sm_id = Hotel.query.filter_by(location=Locations.SM).first().id
        
        #create floors
        malibu_floor1 = Floor(hid=malibu_id, floor_number=1)
        malibu_floor2 = Floor(hid=malibu_id, floor_number=2)
        db.session.add(malibu_floor1)
        db.session.add(malibu_floor2)
        sm_floor1 = Floor(hid=sm_id, floor_number=1)
        sm_floor2 = Floor(hid=sm_id, floor_number=2)
        db.session.add(sm_floor1)
        db.session.add(sm_floor2)
        db.session.commit()

        floor1_malibu_id = Floor.query.filter_by(hid=malibu_id, floor_number=1).first().id
        floor2_malibu_id = Floor.query.filter_by(hid=malibu_id, floor_number=2).first().id
        floor1_sm_id = Floor.query.filter_by(hid=sm_id, floor_number=1).first().id
        floor2_sm_id = Floor.query.filter_by(hid=sm_id, floor_number=2).first().id

        # Create sample rooms
        malibu_room11 = Room(
            fid=floor1_malibu_id,
            hid=malibu_id,
            img="inside.jpeg",
            room_type=RoomType.DLX,
            number_beds=2,
            rate=150,
            balcony=YesNo.N,
            city_view=YesNo.Y,
            ocean_view=YesNo.N,
            smoking=YesNo.Y,
            available=Availability.A,
            max_guests=4,
            wheelchair_accessible=YesNo.Y
        )
        malibu_room21 = Room(
            fid=floor2_malibu_id,
            hid=malibu_id,
            img="inside.jpeg", 
            room_type=RoomType.ST,
            number_beds=1,
            rate=250,
            balcony=YesNo.Y,
            city_view=YesNo.N,
            ocean_view=YesNo.Y,
            smoking=YesNo.N,
            available=Availability.A,
            max_guests=2
        )
        sm_room11 = Room(
            fid=floor1_sm_id,
            hid=sm_id,
            img="inside.jpeg",
            room_type=RoomType.STRD,
            number_beds=2,
            rate=200,
            balcony=YesNo.Y,
            city_view=YesNo.Y,
            ocean_view=YesNo.N,
            smoking=YesNo.N,
            available=Availability.A,
            max_guests=4
        )
        sm_room21 = Room(
            fid=floor2_sm_id,
            hid=sm_id,
            img="inside.jpeg", 
            room_type=RoomType.ST,
            number_beds=1,
            rate=275,
            balcony=YesNo.Y,
            city_view=YesNo.N,
            ocean_view=YesNo.Y,
            smoking=YesNo.Y,
            available=Availability.A,
            max_guests=3, 
            wheelchair_accessible=YesNo.Y
        )        
        db.session.add(malibu_room11)
        db.session.add(malibu_room21)
        db.session.add(sm_room11)
        db.session.add(sm_room21)

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