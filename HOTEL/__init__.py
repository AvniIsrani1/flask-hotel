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
from .model_objects import User, Booking
from .model_dbs import Users, Bookings

from .db import db
#all will evantually become plural here
from .models import Hotel, Floor, Room, FAQ, YesNo, Locations, RoomType, Availability, Assistance, Saved, Service

from .adding import add_layout
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from HOTEL.AImodels.ai_model import load_ai_model, generate_ai_response
from HOTEL.AImodels.csv_retriever import setup_csv_retrieval, get_answer_from_csv
from .response import format_response  
from io import BytesIO
from .receipt_generator import ReceiptGenerator
from flask import send_file
from .routes import bp_profile

app = Flask(__name__,
            static_folder='static',     # Define the static folder (default is 'static')
            template_folder='templates')
app.secret_key = 'GITGOOD_12345'  # This key keeps your session data safe.

rds_secret_name = "rds!db-d319020b-bb3f-4784-807c-6271ab3293b0"
ses_secret_name = "oceanvista_ses"

app.register_blueprint(bp_profile)

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


model = [Users, Hotel, Floor, Room, Bookings, FAQ, YesNo, Locations, RoomType, Availability, Saved]
admin = Admin(app, name="Admin", template_mode="bootstrap4")



# Create all database tables (if they don't exist already)
with app.app_context():
    db.create_all()

    # admin.add_view(ModelView(Users, db.session))

# ----- Routes -----

def send_email(subject, recipients, body, body_template, user=None, booking=None, YesNo=YesNo, attachment=None, attachment_type=None):
    msg = Message(subject,
                  recipients=['ocean.vista.hotels@gmail.com'], #we are in sandbox mode right now (can only send to verified emails) (need to create a dns record first to move to prod mode)
                  body=body)
    try:
        formatting = render_template(body_template, user=user, booking=booking, YesNo=YesNo)
        msg.html = formatting
    except Exception as e:
        print(f"Unable to format email: {e}")
    if attachment:
        with open(attachment, 'rb') as f:
            content = f.read()
            name = attachment.split('/')[-1]
            if attachment_type=='pdf':
                ft = 'application/pdf'
            elif attachment_type=='png':
                ft = 'image/png'
            elif attachment_type=='jpg':
                ft = 'image/jpeg'
            else:
                ft = 'application/octet-stream'
            msg.attach(name,ft,content)
    try:
        mail.send(msg)
        print("Message sent successfully")
    except Exception as e:
        print(f"Not able to send message:{e}")
    
    return 'Email sent!'

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
        existing_user = Users.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please use a different email or login.", "error")
            return redirect(url_for("sign_up"))
        
        # Hash the password before storing for security
        hashed_pw = generate_password_hash(password)
        
        # Create a new user instance
        new_user = Users(name=name, email=email, password=hashed_pw)
        
        try:
            # Save the new user to the database
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            send_email(subject='Welcome to Ocean Vista',recipients=[new_user.email], body="Thank you for creating your Ocean Vista account!",
                       body_template='emails/account_created.html',user=new_user, YesNo=YesNo)
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
        user = Users.query.filter_by(email=email).first()
        
        # Check if user exists and if the password is correct
        if user and check_password_hash(user.password, password):
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


@app.route("/bookings", methods=["GET", "POST"])
def bookings():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])

    current = Bookings.get_current_bookings().join(Room).join(Hotel).filter(Bookings.uid==user.id).all()
    future = Bookings.get_future_bookings().filter(Bookings.uid==user.id).all()
    past = Bookings.get_past_bookings().filter(Bookings.uid==user.id).all()
    canceled = Bookings.get_canceled_bookings().filter(Bookings.uid==user.id).all()

    return render_template('bookings.html', current=current, future=future, past=past, canceled=canceled, YesNo=YesNo)

@app.route("/request-services/<int:bid>", methods=["GET","POST"])
def request_services(bid):
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])
    if request.method == 'POST':
        #making sure user has active bid
        booking = Bookings.get_current_bookings().filter(Bookings.id==bid, Bookings.uid==user.id).first()
        if not booking:
            flash("You do not have an active booking for this request.",'error')
            return redirect(url_for('bookings'))
        robes = int(request.form.get('robes','') or 0)
        btowels = int(request.form.get('btowels','') or 0)
        htowels = int(request.form.get('htowels','') or 0)
        soap = int(request.form.get('soap','') or 0)
        shampoo = int(request.form.get('shampoo','') or 0)
        conditioner = int(request.form.get('conditioner','') or 0)
        wash = int(request.form.get('wash','') or 0)
        lotion = int(request.form.get('lotion','') or 0)
        hdryer = int(request.form.get('hdryer','') or 0)
        pillows = int(request.form.get('pillows','') or 0)
        blankets = int(request.form.get('blankets','') or 0)
        sheets = int(request.form.get('sheets','') or 0)
        print(robes,btowels,htowels,soap,shampoo,conditioner,wash,lotion,hdryer,pillows,blankets,sheets)
        if robes or btowels or htowels or soap or shampoo or conditioner or wash or lotion or hdryer or pillows or blankets or sheets:
            Service.add_item(bid=bid,robes=robes,btowels=btowels,htowels=htowels,soap=soap,shampoo=shampoo,conditioner=conditioner,wash=wash,lotion=lotion,hdryer=hdryer,pillows=pillows,blankets=blankets,sheets=sheets)
        housetime = request.form.get('housetime')
        if housetime:
            print('before',housetime)
            housetime = datetime.strptime(housetime,"%H:%M").time()
            print('after',housetime)
            Service.add_housekeeping(bid=bid,housetime=housetime)
        trash = request.form.get('trash')
        if trash:
            Service.add_trash(bid=bid)
        calltime = request.form.get('calltime')
        recurrent = request.form.get('recurrent')
        if calltime:
            print('before',calltime)
            calltime = datetime.strptime(calltime, "%H:%M").time()
            print('after',calltime)
            if recurrent:
                Service.add_call(bid=bid,calltime=calltime,recurrent=YesNo.Y)
            else:
                Service.add_call(bid=bid,calltime=calltime,recurrent=YesNo.N)
        restaurant = request.form.get('restaurant')
        if restaurant:
            Service.add_dining(bid=bid,restaurant=restaurant)
        assistance = request.form.get('assistance')
        if assistance:
            assistance = Assistance(assistance)
            Service.add_assistance(bid=bid,assistance=assistance)
        other = request.form.get('other')
        if other:
            Service.add_other(bid=bid,other=other)
        return render_template("success.html")
    return render_template('request_services.html')

@app.route("/success")
def success():
    return render_template('success.html')



@app.route("/search", methods=["GET", "POST"])
def search():
    locations = db.session.query(distinct(Hotel.location)).all()
    roomtypes = db.session.query(distinct(cast(Room.room_type, String))).order_by(desc(cast(Room.room_type, String))).all()
    
    rooms = Room.query.all()
    query = Room.query.join(Hotel).filter(Room.available==Availability.A)

    if request.method == "GET":
        stype = request.args.get('stype')
        # if stype == 'apply_search':
        location = request.args.get('location_type')
        start = request.args.get('startdate') 
        end = request.args.get('enddate') 
        if not start and not end: #only time this can happen is when user clicks to search page via home search bar or search button (otherwise always have at least start)
            starting = datetime.now().strftime("%B %d, %Y")
            ending = (datetime.now() + timedelta(days=1)).strftime("%B %d, %Y")
            flash('Please enter both the start and end dates',"error")
            return redirect(url_for('search', startdate=starting, enddate=ending))
        if location:
            location = Locations(location)
            query = query.filter(Hotel.location == location)
        if start:
            starting = datetime.strptime(str(start), "%B %d, %Y").replace(hour=15,minute=0,second=0) #check in is at 3:00 PM
            ending = (starting + timedelta(days=1)).replace(hour=11,minute=0,second=0)
        if end: 
            ending = datetime.strptime(str(end), "%B %d, %Y").replace(hour=11,minute=0,second=0) #check out is at 11:00 AM
            if not start: #impossible to have only end (must have at least start) (will never reach this condition)
                starting = (ending - timedelta(days=1)).replace(hour=15,minute=0,second=0)
        query = query.filter(not_(db.exists().where(Bookings.rid == Room.id).where(Bookings.check_in < ending).where(Bookings.check_out>starting)))
        if stype=='apply_filters':
            room_type = request.args.get('room_type')
            bed_type = request.args.get('bed_type')
            view = request.args.get('view')
            balcony = request.args.get('balcony')
            smoking_preference = request.args.get('smoking_preference')
            accessibility = request.args.get('accessibility')
            price_range = request.args.get('price_range')
            if room_type:
                room_type = RoomType(room_type)
                query = query.filter(Room.room_type == room_type)
            if bed_type:
                query = query.filter(Room.number_beds == bed_type)
            if view:
                if view=='ocean':
                    query = query.filter(Room.ocean_view==YesNo.Y)
                elif view=='city':
                    query = query.filter(Room.city_view==YesNo.Y)
            if balcony:
                if balcony=='balcony':
                    query = query.filter(Room.balcony==YesNo.Y)
                elif balcony=='no_balcony':
                    query = query.filter(Room.balcony==YesNo.N)
            if smoking_preference:
                if smoking_preference == 'Smoking':
                    smoking_preference = YesNo.Y
                else:
                    smoking_preference = YesNo.N
                query = query.filter(Room.smoking == smoking_preference)
            if accessibility:
                accessibility = YesNo.Y
                query = query.filter(Room.wheelchair_accessible == accessibility)
            if price_range:
                price_range = int(price_range)
                query = query.filter(Room.rate <= price_range)
    sort = request.args.get('sort-by')
    if sort=='priceL':
        query = query.order_by(Room.rate.asc())
    elif sort=='priceH':
        query = query.order_by(Room.rate.desc())
    query = query.group_by(
        Room.hid, Room.room_type, Room.number_beds, Room.rate, Room.balcony, Room.city_view, Room.ocean_view, 
        Room.smoking, Room.max_guests, Room.wheelchair_accessible
    )
    query = query.with_entities(Room, func.count(distinct(Room.id)).label('number_rooms'), func.min(Room.id).label('min_rid'))
    rooms = query.all()
    print(rooms)
    return render_template('search.html', locations=locations, roomtypes=roomtypes, rooms=rooms, YesNo = YesNo)


def get_start_end_duration(startdate, enddate):
    starting = datetime.strptime(str(startdate), "%B %d, %Y").replace(hour=15,minute=0,second=0)
    ending = datetime.strptime(str(enddate), "%B %d, %Y").replace(hour=11,minute=0,second=0)
    duration = (ending - starting).days + 1
    return starting, ending, duration

def get_similar_rooms(rid, starting, ending, status): #status refers to if room is available within starting and ending periods
    query = Room.query.join(Hotel).filter(Room.available==Availability.A)
    room = query.filter(Room.id==rid).first()
    similar_rooms = Room.query.join(Hotel).filter(
        Room.hid==room.hid, Room.room_type==room.room_type, Room.number_beds==room.number_beds, Room.rate==room.rate, Room.balcony==room.balcony, Room.city_view==room.city_view,
        Room.ocean_view==room.ocean_view, Room.smoking==room.smoking, Room.max_guests==room.max_guests, Room.wheelchair_accessible==room.wheelchair_accessible
    )
    if status=='open':
        similar_rooms = similar_rooms.filter(not_(db.exists().where(Bookings.rid == Room.id).where(Bookings.check_in < ending).where(Bookings.check_out>starting))).order_by(asc(Room.room_number))
    return similar_rooms

def get_similar_quantities(rid, starting, ending, status):
    if status=='open':
        similar_rooms = get_similar_rooms(rid=rid, starting=starting, ending=ending, status='open')
    else:
        similar_rooms = get_similar_rooms(rid=rid, starting=starting, ending=ending, status='any')
    similar_rooms = similar_rooms.group_by(
        Room.hid, Room.room_type, Room.number_beds, Room.rate, Room.balcony, Room.city_view, Room.ocean_view, 
        Room.smoking, Room.max_guests, Room.wheelchair_accessible
    )
    similar_rooms = similar_rooms.with_entities(Room, Hotel.address, func.count(distinct(Room.id)).label('number_rooms'), func.min(Room.id).label('min_rid'))
    return similar_rooms

@app.route("/reserve", methods=["GET", "POST"])
def reserve():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])
    if request.method=='GET' or request.method=='POST':
        rid = request.args.get('rid')
        location_type = request.args.get('location_type')
        startdate = request.args.get('startdate')
        enddate = request.args.get('enddate')
        if not startdate or not enddate:
            if not rid:
                flash("Reservation details are missing. Please search for a room again.", "error")
            else:
                flash('Please enter both the start and end dates',"error")
            return redirect(url_for('search'))
        print(f"Received rid: {rid}, location_type: {location_type}, startdate: {startdate}, enddate: {enddate}") 
        starting, ending, duration = get_start_end_duration(startdate, enddate)
        room = get_similar_quantities(rid=rid, starting=starting, ending=ending, status='open').first()

        if not room:
            flash('Room not found',"error")
            return redirect(url_for('search'))
        if request.method=='POST':
            name=request.form.get('name', user.name)
            phone=request.form.get('phone', user.phone)
            email=request.form.get('email', user.email)
            guests=request.form.get('guests',1)
            rooms=request.form.get('rooms',1)
            requests=request.form.get('requests','')
            return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=duration, startdate=startdate, enddate=enddate,
                                   name=name, phone=phone,email=email,guests=guests,rooms=rooms,requests=requests)
        
        return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=duration, startdate=startdate, enddate=enddate)


@app.route("/modify/<int:bid>", methods=["GET", "POST"])
def modify(bid):
    modifying = True
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])
    booking = Bookings.query.get(bid)
    if not booking:
        flash('Unable to modify booking. Please try again later', 'error')
        return redirect(url_for('bookings'))
    
    startdate = booking.check_in.strftime("%B %d, %Y")
    enddate = booking.check_out.strftime("%B %d, %Y")
    starting, ending, duration = get_start_end_duration(startdate, enddate)
    room = get_similar_quantities(rid=booking.rid, starting=starting, ending=ending, status="any").first()
    print(room)
    rid = booking.rid
    rooms = 1 #user is able to modify 1 room at a time
    location_type = None
    return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=duration, startdate=startdate, enddate=enddate,
                            name=booking.name, phone=booking.phone,email=booking.email,guests=booking.num_guests,rooms=rooms,requests=booking.special_requests, 
                            modifying=modifying, bid=bid)


@app.route("/save/<int:bid>", methods=["GET", "POST"])
def save(bid): #currently not able to add more rooms by modifying existing booking
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])
    b = Bookings.query.get(bid)
    if b:
        canceled = request.form.get('canceled', 'false')
        if canceled=='true':
            b.cancel_booking()
            send_email(subject='Ocean Vista Booking Canceled!',recipients=[user.email], body="Your booking has been canceled!",
            body_template='emails/canceled.html',user=user, booking=b, YesNo=YesNo)
            flash('Booking canceled!','success')
        else:
            requests = request.form.get('requests', b.special_requests)
            name = request.form.get('name', b.name)
            email = request.form.get('email', b.email)
            phone = request.form.get('phone', b.phone)
            guests = request.form.get('guests', b.num_guests)
            b.update_booking(special_requests=requests, name=name, email=email, phone=phone, num_guests=guests)
            send_email(subject=f'Ocean Vista Booking Updated - {b.id}!',recipients=[user.email], body="Your booking has been updated!",
                       body_template='emails/updated.html',user=user, booking=b, YesNo=YesNo)
            flash('Booking updated!','success')
    return redirect(url_for('bookings'))

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
        malibu_id = Hotel.query.filter_by(location=Locations.MALIBU).first().id
        sm_id = Hotel.query.filter_by(location=Locations.SM).first().id
        
        add_layout(hid=malibu_id,base_floor_number=1,num_floors=4)
        add_layout(hid=sm_id,base_floor_number=1,num_floors=4)
        print("Sample rooms added")

        users = []
        avni = Users(name="avni",email="avni@gmail.com",password=generate_password_hash("avni"))
        devansh = Users(name="devansh",email="devansh@gmail.com",password=generate_password_hash("devansh"))
        elijah = Users(name="elijah",email="elijah@gmail.com",password=generate_password_hash("elijah"))
        andrew = Users(name="andrew",email="andrew@gmail.com",password=generate_password_hash("andrew"))
        users.extend([avni, devansh, elijah, andrew])
        db.session.add_all(users)
        db.session.commit()

        avni_id = Users.query.filter_by(email="avni@gmail.com").first().id
        malibu_room_1 = Room.query.filter_by(hid=malibu_id).first().id
        sm_room_1 = Room.query.filter_by(hid=sm_id).first().id
        Bookings.add_booking(uid=avni_id, rid=malibu_room_1, check_in=datetime.now(), check_out=datetime.now()+timedelta(5), fees=500, special_requests=None, name=Users.get_user(avni_id).name, email=Users.get_user(avni_id).email, phone="818", num_guests=1)
        Bookings.add_booking(uid=avni_id, rid=sm_room_1, check_in=datetime.now()+timedelta(5), check_out=datetime.now()+timedelta(days=10),fees=600, special_requests=None, name=Users.get_user(avni_id).name, email=Users.get_user(avni_id).email, phone="818", num_guests=1)
        Bookings.add_booking(uid=avni_id, rid=malibu_room_1, check_in=datetime.now()-timedelta(2), check_out=datetime.now()-timedelta(days=1), fees=400, special_requests=None, name=Users.get_user(avni_id).name, email=Users.get_user(avni_id).email, phone="818", num_guests=1)
        Bookings.add_booking(uid=avni_id, rid=sm_room_1, check_in=datetime.now()-timedelta(3), check_out=datetime.now()-timedelta(days=1), fees=300, special_requests=None, name=Users.get_user(avni_id).name, email=Users.get_user(avni_id).email, phone="818", num_guests=1)
        Bookings.add_booking(uid=avni_id, rid=malibu_room_1, check_in=datetime.now(), check_out=datetime.now()+timedelta(days=1), fees=300, special_requests=None, name=Users.get_user(avni_id).name, email=Users.get_user(avni_id).email, phone="818", num_guests=1)
        b = Bookings.query.get(1)
        if b:
            b.cancel_booking()

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

        starting, ending, duration = get_start_end_duration(startdate, enddate)
        similar_rooms = get_similar_rooms(rid=rid,starting=starting,ending=ending,status='open')

        rooms_to_book = similar_rooms.limit(int(rooms))
        rooms_to_book_count = rooms_to_book.count()
        if rooms_to_book_count==0:
            flash('Room no longer available. Please search for a new room.','error')
            return redirect(url_for('search'))
        elif rooms_to_book_count < int(rooms):
            flash('Not able to book ' + rooms + ' rooms. ' + str(rooms_to_book_count) + ' rooms available.', 'error') 
        one_room = rooms_to_book.first()
        return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate,duration=duration,
                               YesNo=YesNo, one_room=one_room, 
                               guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                               requests=requests)

# Process payment route (form submission handling)
@app.route("/process-payment", methods=["POST"])
def process_payment():
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
    starting, ending, duration = get_start_end_duration(startdate, enddate)
    similar_rooms = get_similar_rooms(rid=rid,starting=starting,ending=ending,status='open')
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
        try:
            user_id = session.get("user_id")
            
            if not rooms_to_book:
                flash('Room no longer available. Please search for a new room.','error')
                return redirect(url_for('search'))
            elif rooms_to_book_count < int(rooms):
                flash('Not able to book ' + rooms + ' rooms. ' + str(rooms_to_book_count) + ' rooms available.', 'error') 
                return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate,duration=duration,
                                    YesNo=YesNo, one_room=one_room, 
                                    guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                                    requests=requests)                
            # Set check-in and check-out dates
            check_in_date = starting
            check_out_date = ending
            
            # Create a new booking record
            for room in rooms_to_book:
                new_booking = Booking(
                    uid=user_id,
                    rid=room.id,  # Use a valid room ID
                    check_in=check_in_date,
                    check_out=check_out_date,
                    fees=Room.get_room(id==room.id).rate, #might need to update fees
                    special_requests=requests,
                    name=name, 
                    email=email,
                    phone=phone, 
                    num_guests=guests
                )
                # Update room availability
                #room.available = Availability.B
                db.session.add(new_booking)
                send_email(subject='Ocean Vista Booking Created!',recipients=[user.email], body="Thank you for creating a new booking!",
                           body_template='emails/booking_created.html',user=user, booking=new_booking, YesNo=YesNo)
            db.session.commit()

            
            flash("YOUR CARD HAS BEEN ACCEPTED", "success")
            return redirect(url_for("bookings"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Database error: {str(e)}", "database_error")
            return redirect(url_for('search'))
            # return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate,duration=duration,
            #             YesNo=YesNo, one_room=one_room, 
            #             guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
            #             requests=requests)
    else:
        # Card is invalid, display appropriate error messages
        flash("INVALID CREDIT CARD DETAILS", "error")
        return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate,duration=duration,
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