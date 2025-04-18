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
from .entities import Users, Bookings, Services, Hotel, Floor, Room, FAQ, Saved, YesNo, Locations, RoomType, Availability, Assistance, Creditcard
from .controllers import EmailController
from .db import db

from .controllers import RoomAvailability, FormController
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from HOTEL.AImodels.ai_model import load_ai_model, generate_ai_response
from HOTEL.AImodels.csv_retriever import setup_csv_retrieval, get_answer_from_csv
from .response import format_response  
from io import BytesIO
from .Services.ReceiptGenerator import ReceiptGenerator
from flask import send_file
from .blueprints import register_blueprints

app = Flask(__name__,
            static_folder='static',
            template_folder='templates')
app.secret_key = 'GITGOOD_12345'

rds_secret_name = "rds!db-d319020b-bb3f-4784-807c-6271ab3293b0"
ses_secret_name = "oceanvista_ses"


def get_secrets(secret_name):
    """
    Retrieve secrets from AWS Secrets Manager.
    
    Args:
        secret_name (str): The name of the secret to retrieve.
        
    Returns:
        tuple: A tuple containing username and password.
        
    Raises:
        ClientError: If there is an error retrieving the secret.
    """
    client = boto3.client(service_name='secretsmanager', region_name='us-west-1')
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e
    secret = json.loads(response['SecretString'])
    username = secret.get("username")
    pwd = secret.get("password")
    return username, pwd

rds_username, rds_pwd = get_secrets(rds_secret_name)
rds_pwd = quote(rds_pwd)
ses_username, ses_pwd = get_secrets(ses_secret_name)

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

# ----- Routes -----

@app.route("/")
def home():
    """
    Render the home page with a list of available hotel locations.
    
    Returns:
        Template: The rendered home page template.
    """
    locations = db.session.query(distinct(Hotel.location)).all()
    return render_template("home.html", locations=locations)

@app.route("/success")
def success():
    """
    Render the success page.
    
    Returns:
        Template: The success page template.
    """
    return render_template('success.html')

@app.route("/terms")
def terms():
    """
    Render the terms and conditions page.
    
    Returns:
        Template: The terms page template.
    """
    return render_template('terms.html')

@app.route("/events")
def events():
    """
    Render the events page.
    
    Returns:
        Template: The events page template.
    """
    return render_template('events.html')

@app.route("/menu")
def menu():
    """
    Render the restaurant menu page.
    
    Returns:
        Template: The menu page template.
    """
    return render_template('menus2.html')

@app.route("/faq")
def faq():
    """
    Render the FAQ page with all FAQs from the database.
    
    Returns:
        Template: The FAQ page template with FAQs.
    """
    faqs = FAQ.query.all()
    return render_template('faq.html', faqs=faqs)

@app.route("/about")
def about():
    """
    Render the about page.
    
    Returns:
        Template: The about page template.
    """
    return render_template('about.html')

def add_sample_data():
    """
    Add sample data to the database if tables are empty.
    
    Creates sample hotels, rooms, and users for testing.
    """
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
        
        with open('sample_layout.json', 'r') as f:
            add_room_params = json.load(f)
        malibu_hotel.add_layout(base_floor_number=1, number_floors=4, add_room_params=add_room_params)
        sm_hotel.add_layout(base_floor_number=1, number_floors=4, add_room_params=add_room_params)
        print("Sample rooms added")

        users = []
        avni = Users(name="avni", email="avni@gmail.com", password=generate_password_hash("avni"))
        devansh = Users(name="devansh", email="devansh@gmail.com", password=generate_password_hash("devansh"))
        elijah = Users(name="elijah", email="elijah@gmail.com", password=generate_password_hash("elijah"))
        andrew = Users(name="andrew", email="andrew@gmail.com", password=generate_password_hash("andrew"))
        users.extend([avni, devansh, elijah, andrew])
        db.session.add_all(users)
        db.session.commit()
        print('sample users added')

        print("sample bookings")

def add_sample_faq():
    """
    Add sample FAQs to the database.
    """
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
    """
    Process a user query using CSV data first, falling back to AI.
    
    Args:
        user_question (str): The user's question.
        
    Returns:
        str: The formatted response to the question.
    """
    csv_answer = get_answer_from_csv(ai_db, user_question)
    formatted_response = format_response(csv_answer, user_question)
    
    # If we got a valid formatted response, return it
    if formatted_response:
        return formatted_response
    
    # Otherwise, use the AI model to generate a response
    return generate_ai_response(ai_model, user_question)

@app.route("/")
def index():
    """
    Render the chat interface.
    
    Returns:
        Template: The chat page template.
    """
    return render_template("chat.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    """
    Process an AI chat request.
    
    Returns:
        JSON: The AI response as JSON.
    """
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

if __name__ == "__main__":
    app.run(debug=True)