from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime, distinct, desc, asc, cast, func, not_, String, Computed
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum as PyEnum
from urllib.parse import quote
import boto3
from botocore.exceptions import ClientError
import json
from .entities import Users, Bookings, Services, Hotel, Floor, Room, FAQ, Saved, YesNo, Locations, RoomType, Availability, Assistance
from .controllers import EmailController
from .db import db
#all will evantually become plural here

from .controllers import RoomAvailability #will remove this line once payment is moved to routes.py
from .adding import add_layout
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from HOTEL.AImodels.ai_model import load_ai_model, generate_ai_response
from HOTEL.AImodels.csv_retriever import setup_csv_retrieval, get_answer_from_csv
from .response import format_response  
from io import BytesIO
from .receipt_generator import ReceiptGenerator
from flask import send_file
# from .routes import bp_profile, bp_bookings, bp_reserve, bp_request_services, bp_search
from .blueprints import register_blueprints
app = Flask(__name__,
            static_folder='static',     # Define the static folder (default is 'static')
            template_folder='templates')
app.secret_key = 'GITGOOD_12345'  # This key keeps your session data safe.

rds_secret_name = "rds!db-d319020b-bb3f-4784-807c-6271ab3293b0"
ses_secret_name = "oceanvista_ses"


def get_secrets(secret_name):
    client = boto3.client(service_name='secretsmanager', region_name='us-west-1')
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    secret = json.loads(response['SecretString'])
    username=secret.get("username")
    pwd = secret.get("password")
    return username, pwd

rds_username, rds_pwd = get_secrets(rds_secret_name)
rds_pwd = quote(rds_pwd)
ses_username, ses_pwd = get_secrets(ses_secret_name)
#'AKIAZVMTVFXJYB4NK7BH','BLQALd5gKDcpmTq+Fl6nAMZ8hSdGv+gFvgAfaBGrXlwf'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{rds_username}:{rds_pwd}@hotel-db-instance.cvwasiw2g3h6.us-west-1.rds.amazonaws.com:3306/hotel_db'

app.config['MAIL_SERVER'] = 'email-smtp.us-west-1.amazonaws.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = ses_username
app.config['MAIL_PASSWORD'] = ses_pwd
app.config['MAIL_DEFAULT_SENDER'] = 'ocean.vista.hotels@gmail.com'

ai_model = load_ai_model()
ai_db = setup_csv_retrieval()

db.init_app(app)
mail = Mail(app)
email_controller = EmailController(mail)
register_blueprints(app, email_controller)



model = [Users, Hotel, Floor, Room, Bookings, FAQ, YesNo, Locations, RoomType, Availability, Saved]
admin = Admin(app, name="Admin", template_mode="bootstrap4")



# Create all database tables (if they don't exist already)
with app.app_context():
    db.create_all()

    # admin.add_view(ModelView(Users, db.session))

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
        if not Users.unique_email(email):
            flash("Email already registered. Please use a different email or login.", "error")
            return redirect(url_for("sign_up"))
        
        # Hash the password before storing for security
        user = Users.create_initial_user(name,email,password)

        
        try:
            # Save the new user to the database
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            email_controller.send_welcome_email(user=user)
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
        user = Users.get_user_by_email(email)

        # Check if user exists and if the password is correct
        if user and user.verify_password(password):
            # Save user's id and name in session so we know they are logged in
            session["user_id"] = user.id
            session["user_name"] = user.name
            if user.first_login == YesNo.Y:
                return redirect(url_for('profile.profile'))
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


@app.route("/success")
def success():
    return render_template('success.html')

@app.route("/terms")
def terms():
    return render_template('terms.html')

@app.route("/events")
def events():
    return render_template('events.html')

@app.route("/menu1")
def menu1():
    return render_template('menu1.html')

@app.route("/faq")
def faq():
    faqs = FAQ.query.all()
    return render_template('faq.html',faqs=faqs)

@app.route("/about")
def about():
    return render_template('about.html')

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
            malibu_hotel = Hotel(location=Locations.MALIBU, address="1234 Sunset Blvd, Malibu, CA 90265")
            sm_hotel = Hotel(location=Locations.SM, address="5678 Ocean Drive, Santa Monica, CA 90401")
            db.session.add(malibu_hotel)
            db.session.add(sm_hotel)
            db.session.commit()

        # Get hotel IDs
        malibu_hotel = Hotel.get_hotels_by_location("Malibu")[0]
        sm_hotel = Hotel.get_hotels_by_location("Santa Monica")[0]
        
        with open('sample_layout.json','r') as f:
            add_room_params = json.load(f)
        malibu_hotel.add_layout(base_floor_number=1, number_floors=4, add_room_params=add_room_params)
        sm_hotel.add_layout(base_floor_number=1, number_floors=4, add_room_params=add_room_params)
        print("Sample rooms added")

        users = []
        avni = Users(name="avni",email="avni@gmail.com",password=generate_password_hash("avni"))
        devansh = Users(name="devansh",email="devansh@gmail.com",password=generate_password_hash("devansh"))
        elijah = Users(name="elijah",email="elijah@gmail.com",password=generate_password_hash("elijah"))
        andrew = Users(name="andrew",email="andrew@gmail.com",password=generate_password_hash("andrew"))
        users.extend([avni, devansh, elijah, andrew])
        db.session.add_all(users)
        db.session.commit()
        print('sample users added')

        # avni_id = Users.query.filter_by(email="avni@gmail.com").first().id
        # malibu_room_1 = Room.query.filter_by(hid=malibu_id).first().id
        # sm_room_1 = Room.query.filter_by(hid=sm_id).first().id
        # sample_bookings = []
        # sample_bookings.append(Booking(uid=avni_id, rid=malibu_room_1, check_in=datetime.now(), check_out=datetime.now()+timedelta(5), fees=500, name="avni", email="avni@gmail.com", phone="123"))
        # sample_bookings.append(Booking(uid=avni_id, rid=sm_room_1, check_in=datetime.now()+timedelta(5), check_out=datetime.now()+timedelta(days=10), fees=600, name="avni", email="avni@gmail.com", phone="123"))
        # sample_bookings.append(Booking(uid=avni_id, rid=malibu_room_1, check_in=datetime.now()-timedelta(2), check_out=datetime.now()-timedelta(days=1), fees=600, name="avni", email="avni@gmail.com", phone="123"))
        # sample_bookings.append(Booking(uid=avni_id, rid=sm_room_1, check_in=datetime.now()-timedelta(3), check_out=datetime.now()-timedelta(days=1), fees=600, name="avni", email="avni@gmail.com", phone="123"))
        # sample_bookings.append(Booking(uid=avni_id, rid=malibu_room_1, check_in=datetime.now()-timedelta(1), check_out=datetime.now()+timedelta(days=1), fees=600, name="avni", email="avni@gmail.com", phone="123"))
        # sample_bookings[0].cancel()
        # results = Bookings.create_bookings_db(sample_bookings)
        # db.session.add_all(results)
        # db.session.commit()
        print("sample bookings")

def add_sample_faq():
    faqs = [
        ("Where are Ocean Vista's locations?", 
        "Ocean Vista Hotel has two locations: one in Malibu and one in Santa Monica.", 
        "General Information"),

        ("What are the check-in and check-out times?", 
        "Check-in is at 3:00 PM, and check-out is at 11:00 AM.", 
        "General Information"),

        ("Do you allow early check-in or late check-out?", 
        "Early check-in and late check-out are subject to availability. Please contact the front desk for requests.", 
        "General Information"),

        ("Is parking available at the hotel?", 
        "Yes, both locations offer on-site parking. A daily parking fee may apply.", 
        "General Information"),

        ("Does Ocean Vista have an on-site restaurant?", 
        "Yes, our Ocean Breeze Restaurant serves fresh seafood and international cuisine with stunning oceanfront views.", 
        "Dining & Activities"),

        ("Is room service available?", 
        "Yes, room service is available from 7:00 AM to 10:00 PM.", 
        "Dining & Activities"),

        ("Does Ocean Vista have a pool or spa?", 
        "Our Santa Monica location features a rooftop infinity pool, while our Malibu location has a full-service spa and wellness center.", 
        "Dining & Activities"),

        ("Is Wi-Fi available?", 
        "Yes, we offer complimentary high-speed Wi-Fi in all rooms and public areas.", 
        "Rooms & Amenities"),

        ("Do rooms have kitchenettes or minibars?", 
        "Select suites come with kitchenettes. All rooms include a minibar, coffee maker, and essential appliances.", 
        "Rooms & Amenities"),

        ("Is Ocean Vista pet-friendly?", 
        "Yes! We welcome pets for an additional fee. Please review our pet policy before booking.", 
        "Rooms & Amenities"),

        ("What is the cancellation policy?", 
        "Our standard cancellation policy allows free cancellations up to 48 hours before check-in. Policies may vary for special rates and peak seasons.", 
        "Reservations & Policies"),

        ("Can I host an event or wedding at Ocean Vista?", 
        "Absolutely! We offer event spaces, wedding packages, and beachside ceremonies at both locations.", 
        "Reservations & Policies")
    ]
    FAQ.add_faq(faqs)

def process_query(user_question):
    "Processes the user query using CSV first, AI as backup."
    csv_answer = get_answer_from_csv(ai_db, user_question)
    formatted_response = format_response(csv_answer, user_question)
    
    # If we got a valid formatted response, return it
    if formatted_response:
        return formatted_response
    
    # Otherwise, use the AI model to generate a response
    return generate_ai_response(ai_model, user_question)

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    try:
        csv_data = request.get_json()
        user_message = csv_data.get("message", "")
        
        if not user_message:
            return jsonify({"response": "I'm not sure what you mean."})
        
        ai_response = process_query(user_message)
        return jsonify({"response": ai_response})
    except Exception as e:
        # Log the error
        print(f"Error: {str(e)}")
        # Return a proper error response
        return jsonify({"response": "An error occurred while processing your request."}), 500

# Add this after db.create_all() in your __init__.py
with app.app_context():
    db.create_all()
    add_sample_data()
    if not FAQ.query.first():
        add_sample_faq()

# Payment page route
@app.route("/payment", methods=["GET","POST"])
def payment():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    if request.method=='POST':
        rid = request.form.get('rid') #only being used to get back to reserve page if cancel button is clicked; otherwise is never used
        location_type = request.form.get('location_type')
        startdate = request.form.get('startdate')
        enddate = request.form.get('enddate')
        rooms = request.form.get('rooms')
        requests = request.form.get('requests')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        guests = request.form.get('guests')

        room_availability = RoomAvailability(startdate=startdate,enddate=enddate)
        room_availability.set_rid_room(rid=rid)
        similar_rooms=room_availability.get_similar_rooms(status='open')
        if not similar_rooms:
            flash('This room no longer available. Please search for a new room.','error')
            return redirect(url_for('search.search'))

        rooms_to_book = similar_rooms.limit(int(rooms))
        rooms_to_book_count = rooms_to_book.count()
        if rooms_to_book_count < int(rooms):
            flash('Not able to book ' + rooms + ' rooms. ' + str(rooms_to_book_count) + ' rooms available.', 'error') 
        one_room = rooms_to_book.first()
        return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate,duration=room_availability.get_duration(),
                               YesNo=YesNo, one_room=one_room, 
                               guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                               requests=requests)

# Process payment route (form submission handling)
@app.route("/process-payment", methods=["POST"])
def process_payment():
    print("processing payment...")
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    user = Users.query.get(session["user_id"])
    
    # Extract payment information from the form
    credit_card_number = request.form.get("card-number")
    exp_date = request.form.get("expiry")
    cvv = request.form.get("cvv")

    # Extract room information from form
    rid = request.form.get('rid') 
    location_type = request.form.get('location_type')
    startdate = request.form.get('startdate')
    enddate = request.form.get('enddate')
    rooms = request.form.get('rooms')
    requests = request.form.get('requests')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    guests = request.form.get('guests')

    # Find a valid room to book 

    room_availability = RoomAvailability(startdate=startdate,enddate=enddate)
    room_availability.set_rid_room(rid=rid)
    similar_rooms=room_availability.get_similar_rooms(status='open')
    if not similar_rooms:
        flash('Room no longer available. Please search for a new room.','error')
        return redirect(url_for('search.search'))
    rooms_to_book = similar_rooms.limit(int(rooms))
    rooms_to_book_count = rooms_to_book.count()
    one_room = rooms_to_book.first()
    print(one_room)
    rooms_to_book = rooms_to_book.all()
    
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
        print("card validation passed...")
        try:
            user_id = session.get("user_id")
            
            if not rooms_to_book:
                flash('Room no longer available. Please search for a new room.','error')
                return redirect(url_for('search.search'))
            elif rooms_to_book_count < int(rooms):
                flash('Not able to book ' + rooms + ' rooms. ' + str(rooms_to_book_count) + ' rooms available.', 'error') 
                return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate,duration=room_availability.get_duration(),
                                    YesNo=YesNo, one_room=one_room, 
                                    guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                                    requests=requests)                
            # Set check-in and check-out dates
            check_in_date = room_availability.get_starting()
            check_out_date = room_availability.get_ending()
            
            # Create a new booking record
            new_bookings = []
            for room in rooms_to_book:
                new_bookings.append(
                    Bookings(
                        uid=user_id,
                        rid=room.id, 
                        check_in=check_in_date,
                        check_out=check_out_date,
                        fees=Room.get_room(id==room.id).rate, #might need to update fees
                        special_requests=requests,
                        name=name, 
                        email=email,
                        phone=phone, 
                        num_guests=guests
                    )
                )
                # Update room availability
                #room.available = Availability.B
                # db.session.add(new_booking)
                # send_email(subject='Ocean Vista Booking Created!',recipients=[user.email], body="Thank you for creating a new booking!",
                #            body_template='emails/booking_created.html',user=user, booking=new_booking, YesNo=YesNo)
            db.session.add_all(new_bookings)
            db.session.commit()
            print("sending email...")
            email_controller.send_booking_created(user=user,bookings=new_bookings,YesNo=YesNo)
            print("Done sending email")
            print("Card accepted...")
            flash("YOUR CARD HAS BEEN ACCEPTED", "success")
            return redirect(url_for("bookings.bookings"))
            
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {str(e)}", "database_error")
            flash(f"Database error: {str(e)}", "database_error")
            return redirect(url_for('search.search'))
            # return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate,duration=duration,
            #             YesNo=YesNo, one_room=one_room, 
            #             guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
            #             requests=requests)
    else:
        # Card is invalid, display appropriate error messages
        flash("INVALID CREDIT CARD DETAILS", "error")
        return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate,duration=room_availability.get_duration(),
                               YesNo=YesNo, one_room=one_room, 
                               guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                               requests=requests)
    
@app.route("/booking/<int:booking_id>/receipt/view")
def view_receipt(booking_id):
    """
    Display an HTML receipt for a booking
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    booking = Bookings.query.get(booking_id)
    
    if not booking:
        flash("Booking not found.", "error")
        return redirect(url_for("bookings"))
    
    if booking.uid != session["user_id"]:
        flash("You don't have permission to view this receipt.", "error")
        return redirect(url_for("bookings"))
    
    today = datetime.now()
    
    num_nights = (booking.check_out - booking.check_in).days
    if num_nights == 0:
        num_nights = 1
    
    room_rate = booking.room.rate
    total_room_charges = room_rate * num_nights
    resort_fee = 30.00 * num_nights
    tax_amount = total_room_charges * 0.15
    total_amount = total_room_charges + resort_fee + tax_amount
    
    return render_template(
        "receipt.html", 
        booking=booking, 
        today=today,
        YesNo=YesNo,
        num_nights=num_nights,
        room_rate=room_rate,
        total_room_charges=total_room_charges,
        resort_fee=resort_fee,
        tax_amount=tax_amount,
        total_amount=total_amount
    )

@app.route("/booking/<int:booking_id>/receipt/download")
def download_receipt(booking_id):
    """
    Generate and download a PDF receipt for a booking
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    booking = Bookings.query.get(booking_id)
    
    if not booking:
        flash("Booking not found.", "error")
        return redirect(url_for("bookings"))
    
    if booking.uid != session["user_id"]:
        flash("You don't have permission to download this receipt.", "error")
        return redirect(url_for("bookings"))
    
    today = datetime.now()

    num_nights = (booking.check_out - booking.check_in).days
    if num_nights == 0:
        num_nights = 1

    room_rate = booking.room.rate
    total_room_charges = room_rate * num_nights
    resort_fee = 30.00 * num_nights
    tax_amount = total_room_charges * 0.15
    total_amount = total_room_charges + resort_fee + tax_amount
    
    receipt_gen = ReceiptGenerator()
    
    pdf_buffer = receipt_gen.generate_receipt(
        booking=booking, 
        #num_nights=num_nights, 
        room_rate=room_rate,
        total_room_charges=total_room_charges,
        resort_fee=resort_fee,
        tax_amount=tax_amount,
        total_amount=total_amount,
        return_bytes=True
    )
    
    filename = f"OceanVista_Booking_Receipt_{booking.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

if __name__ == "__main__":
    app.run(debug=True)