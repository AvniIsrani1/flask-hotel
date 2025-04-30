"""
Create routes for each page.

Note:
    Author: Avni Israni, Devansh Sharma, Elijah Cortez, Andrew Ponce
    Documentation: Devansh Sharma
    Created: March 2, 2025
    Modified: April 17, 2025
"""

from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for, session, flash, get_flashed_messages, send_file
from .db import db
from sqlalchemy import DateTime, Date, cast, distinct, desc, asc, cast, func, not_, or_, String, Computed
from datetime import datetime, date, timedelta
from .entities import User, Staff, Booking, Service, Hotel, Floor, Room, YesNo, Assistance, Locations, Availability, RoomType, Status, SType, Creditcard, FAQ
from .controllers import SearchController, FormController, RoomAvailability
from datetime import datetime
from .Services import ReceiptGenerator, ReportGenerator
from flask import Blueprint, jsonify, render_template
from HOTEL.AImodels.csv_retriever import setup_csv_retrieval, get_answer_from_csv
from HOTEL.AImodels.ai_model import load_ai_model, generate_ai_response
from .Services.response import format_response  

ai_model = load_ai_model()
ai_db, ai_df = setup_csv_retrieval()


def auth_routes(email_controller):
    """
    Create authentication-related routes and register them to a blueprint.
    
    Parameters:
        email_controller (EmailController): The email controller for sending notifications.
        
    Returns:
        Blueprint: The blueprint with authentication routes registered.

    Note: 
        Author: Devansh Sharma
        Created: February 16, 2025
        Modified: April 17, 2025
    """
    bp_auth = Blueprint('auth', __name__)

    @bp_auth.route("/signup", methods=["GET", "POST"])
    def sign_up():
        """
        Handle user sign-up requests.
        
        GET: Display the sign-up form.
        POST: Process the sign-up form submission.
        
        Returns:
            Template: The sign-up form or a redirect to the login page on success.
        """
        if request.method == "POST":
            # Get form data
            name, email, password, confirm_password = FormController.get_signup_information()
            
            # Check if passwords match
            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return redirect(url_for("auth.sign_up"))
            
            # Check if email already exists
            if not User.unique_email(email):
                flash("Email already registered. Please use a different email or login.", "error")
                return redirect(url_for("auth.sign_up"))
            
            # Create a new user
            user = User.create_initial_user(name, email, password)
            
            try:
                # Save the new user to the database
                db.session.add(user)
                db.session.commit()
                flash("Account created successfully! Please log in.", "success")
                
                # If you have email functionality, you might want to send a welcome email here
                email_controller.send_welcome_email(user=user)
                
                return redirect(url_for("auth.login"))
            except Exception as e:
                # Roll back the session if there is an error
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "error")
                return redirect(url_for("auth.sign_up"))
        
        return render_template("signup.html")

    @bp_auth.route("/login", methods=["GET", "POST"])
    def login():
        """
        Handle user login requests.
        
        GET: Display the login form.
        POST: Process the login form submission.
        
        Returns:
            Template: The login form or a redirect to the home page on success.
        """
        if request.method == "POST":
            email, password = FormController.get_login_information()
            
            # Find user by email
            user = User.get_user_by_email(email)

            # Check if user exists and if the password is correct
            if user and user.verify_password(password):
                # Save user's id and name in session so we know they are logged in
                session["user_id"] = user.id
                session["user_name"] = user.name
                is_staff = user.type == 'staff'
                session["staff"] = is_staff
                session["staff_position"] = user.position.label if is_staff and user.position else ''

                if user.first_login == YesNo.Y:
                    return redirect(url_for('profile.profile'))
                else:
                    flash("Logged in successfully!", "success")
                    return redirect(url_for("info.home"))
            else:
                flash("Invalid email or password.", "error")
                return redirect(url_for("auth.login"))
        
        return render_template("login.html")

    @bp_auth.route("/logout")
    def logout():
        """
        Handle user logout requests by clearing the session.
        
        Returns:
            Redirect: Redirect to the home page.
        """
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("info.home"))
    
    return bp_auth

bp_profile = Blueprint('profile',__name__)
@bp_profile.route("/profile",methods=["GET", "POST"])
def profile():
    """
    Handle user profile viewing and updates.
    
    GET: Display the user profile page.
    POST: Process profile updates based on the form type submitted.
    
    Returns:
        Template: The profile template with user data.
        Redirect: Redirect to login page if not logged in.

    Note: 
        Author: Avni Israni
        Created: February 16, 2025
        Modified: April 17, 2025
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
    
    user = User.query.get(session["user_id"])
    if not user:
        flash('Account not found','error')
        session.clear()
        return redirect(url_for("auth.login"))
    if user.first_login is YesNo.Y:
        flash("Please update your profile information!", "action")
    message = status = ''
    if request.method == "POST":
        ptype = request.form.get('ptype')
        if ptype == 'profile':
            name, phone, address_line1, address_line2, city, state, zipcode = FormController.get_profile_update_information()
            user.update_profile(
                name = name, phone = phone, address_line1 = address_line1, address_line2 = address_line2,
                city = city, state = state, zipcode = zipcode
            )
            message = 'Profile has been updated!'
            status = 'success'
        elif ptype=='notifications':
            tremind, eremind = FormController.get_profile_notification_information()
            user.update_notifications(tremind,eremind)
            message = 'Notification preferences have been updated!'
            status = 'success'
        elif ptype=='password_change':
            cur_password = request.form.get("cur_pass")
            if user.verify_password(cur_password):
                new_password = request.form.get("new_pass")
                user.change_password(new_password)
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
            db.session.rollback()
            flash(f"An error occurred: {str(e)}. Please try again later.", "error")
        finally:
            return redirect(url_for("profile.profile"))
    return render_template("profile.html", user=user, YesNo = YesNo)


def booking_routes(email_controller):
    """
    Create booking-related routes and register them to a blueprint.
    
    Parameters:
        email_controller (EmailController): The email controller for sending notifications.
        
    Returns:
        Blueprint: The blueprint with booking routes registered.

    Note: 
        Author: Avni Israni
        Created: February 18, 2025
        Modified: April 17, 2025
    """
    bp_bookings = Blueprint('bookings',__name__)

    @bp_bookings.route("/bookings", methods=["GET", "POST"])
    def bookings():
        """
        Display user's bookings organized by status.
        
        Returns:
            Template: The bookings template with all user bookings.
            Redirect: Redirect to login page if not logged in.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        user_id = session["user_id"]
        user = User.get_user(user_id)

        current = Booking.get_current_user_bookings(user_id)
        print(current)
        future = Booking.get_future_user_bookings(user_id)
        print(future)
        past = Booking.get_past_user_bookings(user_id)
        canceled = Booking.get_canceled_user_bookings(user_id)

        return render_template('bookings.html', current=current, future=future, past=past, canceled=canceled, YesNo=YesNo)

    @bp_bookings.route("/modify/<int:bid>", methods=["GET", "POST"])
    def modify(bid):
        """
        Modify an existing booking.
        
        Parameters:
            bid (int): The booking ID to modify.
            
        Returns:
            Template: The reservation form with booking data.
            Redirect: Redirect to bookings page if booking not found.
        """
        modifying = True
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        user_id = session["user_id"]
        user = User.get_user(user_id)
        booking = Booking.get_booking(bid)

        if not booking:
            flash('Unable to modify booking. Please try again later', 'error')
            return redirect(url_for('bookings.bookings'))
        
        startdate = booking.check_in.strftime("%B %d, %Y")
        enddate = booking.check_out.strftime("%B %d, %Y")

        room_availability = RoomAvailability(startdate=startdate, enddate=enddate)
        room_availability.set_rid_room(rid=booking.rid)
        room=room_availability.get_similar_quantities(status='any').first() #any because just trying to pull up the room details again (not doing any actual booking)
        print(room)
        if not room:
            flash('An error occured. Please try again later','error')
            return redirect(url_for('bookings.bookings'))
        rid = booking.rid
        rooms = 1 #user is able to modify 1 room at a time
        location_type = None
        return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=room_availability.get_duration(), startdate=startdate, enddate=enddate,
                                name=booking.name, phone=booking.phone,email=booking.email,guests=booking.num_guests,rooms=rooms,requests=booking.special_requests, 
                                modifying=modifying, bid=bid)

    @bp_bookings.route("/save/<int:bid>", methods=["GET", "POST"])
    def save(bid):
        """
        Save changes to a booking or cancel it.
        
        Parameters:
            bid (int): The booking ID to save changes for.
            
        Returns:
            Redirect: Redirect to bookings page after processing.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        user = User.query.get(session["user_id"])
        booking = Booking.query.get(bid)
        message = status = ''
        if booking:
            canceled = request.form.get('canceled', 'false')
            if canceled=='true':
                booking.cancel()
                email_controller.send_booking_canceled(user=user,booking=booking,YesNo=YesNo)
                message='Booking canceled!'
                status = 'success'
            else:
                special_requests, name, email, phone, num_guests = FormController.get_update_booking_information(booking)
                booking.update_booking(special_requests=special_requests, name = name, email = email, phone = phone, num_guests = num_guests)
                email_controller.send_booking_updated(user=user,booking=booking,YesNo=YesNo)
                message='Booking updated!'
                status='success'
            try:
                db.session.commit()
                flash(message, status)
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}. Please try again later.", "error")
        return redirect(url_for('bookings.bookings'))
    return bp_bookings

bp_reserve = Blueprint('reserve',__name__)
@bp_reserve.route("/reserve", methods=["GET", "POST"])
def reserve():
    """
    Handle room reservation requests.
    
    GET: Display reservation form with room details.
    POST: Process the reservation form data.
    
    Returns:
        Template: The reservation form template.
        Redirect: Redirect to search page if data is missing.

    Note: 
        Author: Avni Israni
        Created: March 18, 2025
        Modified: April 17, 2025
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
    user = User.query.get(session["user_id"])
    if request.method=='GET' or request.method=='POST':
        rid, location_type, startdate, enddate = FormController.get_booking_reservation_information()
        if not startdate or not enddate:
            if not rid:
                flash("Reservation details are missing. Please search for a room again.", "error")
            else:
                flash('Please enter both the start and end dates',"error")
            return redirect(url_for('search.search'))
        print(f"Received rid: {rid}, location_type: {location_type}, startdate: {startdate}, enddate: {enddate}") 
        room_availability = RoomAvailability(startdate=startdate,enddate=enddate)
        room_availability.set_rid_room(rid=rid)
        room=room_availability.get_similar_quantities(status='open').first()
        if not room:
            flash('Room not found',"error")
            return redirect(url_for('search.search'))
        if request.method=='POST':
            name, phone, email, guests, rooms, requests = FormController.get_make_reservation_information(user)
            return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=room_availability.get_duration(), startdate=startdate, enddate=enddate,
                                   name=name, phone=phone,email=email,guests=guests,rooms=rooms,requests=requests)
        
        return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=room_availability.get_duration(), startdate=startdate, enddate=enddate)

bp_request_services = Blueprint('request_services',__name__)
@bp_request_services.route("/request-services/<int:bid>", methods=["GET","POST"])
def request_services(bid):
    """
    Handle guest service requests for a booking.
    
    GET: Display the service request form.
    POST: Process the service request submissions.
    
    Parameters:
        bid (int): The booking ID to request services for.
        
    Returns:
        Template: The service request form template.
        Redirect: Redirect to bookings page after processing.

    Note: 
        Author: Avni Israni
        Created: February 16, 2025
        Modified: April 17, 2025
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
    user = User.query.get(session["user_id"])
    if request.method == 'POST':
        #making sure user has active bid
        booking = Booking.get_specific_current_user_bookings(uid=user.id, bid=bid)
        if not booking:
            flash("You do not have an active booking for this request.",'error')
            return redirect(url_for('bookings.bookings'))
        robes, btowels, htowels, soap, shampoo, conditioner, wash, lotion, hdryer, pillows, blankets, sheets, housetime, trash, calltime, recurrent, restaurant, assistance, other = FormController.get_service_request_information()
        print(robes,btowels,htowels,soap,shampoo,conditioner,wash,lotion,hdryer,pillows,blankets,sheets)
        services = []
        if robes or btowels or htowels or soap or shampoo or conditioner or wash or lotion or hdryer or pillows or blankets or sheets:
            services.append(Service.add_item(bid=bid, robes=robes, btowels=btowels, htowels=htowels, soap=soap, shampoo=shampoo,
                                                    conditioner=conditioner, wash=wash, lotion=lotion, hdryer=hdryer, pillows=pillows,
                                                    blankets=blankets, sheets=sheets))
        if housetime:
            print('before',housetime)
            housetime = datetime.strptime(housetime,"%H:%M").time()
            print('after',housetime)
            services.append(Service.add_housekeeping(bid=bid, housetime=housetime, validate_check_out=booking.check_out))
        if trash:
            services.append(Service.add_trash(bid=bid))
        if calltime:
            print('before',calltime)
            calltime = datetime.strptime(calltime, "%H:%M").time()
            print('after',calltime)
            if recurrent:
                services.extend(Service.add_call(bid=bid, calltime=calltime, recurrent=True, validate_check_out=booking.check_out))
            else:
                services.extend(Service.add_call(bid=bid, calltime=calltime, recurrent=False, validate_check_out=booking.check_out))
        if restaurant:
            services.append(Service.add_dining(bid=bid, restaurant=restaurant))
        if assistance:
            assistance = Assistance(assistance)
            services.append(Service.add_assistance(bid=bid, assistance=assistance))
        if other:
            services.append(Service.add_other(bid=bid, other=other))
        try:
            db.session.add_all(services)
            db.session.commit()
            print('Successful commit')
            flash('Your request has been receieved. We will do our best to meet your needs as quickly as possible. Thank you!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}. Please try again later.", "error")
        return redirect(url_for('bookings.bookings'))
    return render_template('request_services.html')


bp_search = Blueprint('search',__name__)
@bp_search.route("/search", methods=["GET", "POST"])
def search():
    """
    Handle room search and filtering.
    
    GET: Display search results based on query parameters.
    
    Returns:
        Template: The search results template.

    Note: 
        Author: Avni Israni
        Created: March 14, 2025
        Modified: April 17, 2025
    """
    locations = db.session.query(distinct(Hotel.location)).all()
    roomtypes = db.session.query(distinct(cast(Room.room_type, String))).order_by(desc(cast(Room.room_type, String))).all()
    
    search_controller = SearchController()
    if request.method == "GET":
        stype = request.args.get('stype')
        # if stype == 'apply_search':
        location, start, end = FormController.get_main_search()
        starting, ending,result = search_controller.main_search(location=location,start=start,end=end)
        if(not result):
            flash('Please enter both the start and end dates',"error")
            return redirect(url_for('search.search', startdate=starting, enddate=ending))
        if stype=='apply_filters':
            room_type, bed_type, view, balcony, smoking_preference, accessibility, price_range = FormController.get_filters_search()
            search_controller.filter_search(room_type=room_type,bed_type=bed_type,view=view,balcony=balcony,
                           smoking_preference=smoking_preference,accessibility=accessibility,
                           price_range=price_range)
    sort = request.args.get('sort-by')
    search_controller.sort_search(sort=sort)
    search_controller.get_quantities()
    rooms = search_controller.get_search()
    print(rooms)
    return render_template('search.html', locations=locations, roomtypes=roomtypes, rooms=rooms, YesNo=YesNo)


def payment_routes(email_controller):
    """
    Create payment-related routes and register them to a blueprint.
    
    Parameters:
        email_controller (EmailController): The email controller for sending notifications.
        
    Returns:
        Blueprint: The blueprint with payment routes registered.

    Note: 
        Author: Devansh Sharma and Andrew Ponce
        Created: March 11, 2025
        Modified: April 17, 2025
    """
    bp_payment = Blueprint('payment', __name__)

    @bp_payment.route("/payment", methods=["GET", "POST"])
    def payment():
        """
        Handle the payment page.
        
        GET: Display the payment form.
        POST: Process the payment form data and show the payment form.
        
        Returns:
            Template: The payment form template.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        user = User.query.get(session["user_id"])
        if user is None:
            flash("User is not valid","error")
            return redirect(url_for("auth.login"))
        if request.method == 'POST':
            rid, location_type, startdate, enddate, name, phone, email, guests, rooms, requests = FormController.get_summary_reservation_information(user)
            room_availability = RoomAvailability(startdate=startdate, enddate=enddate)
            room_availability.set_rid_room(rid=rid)
            similar_rooms = room_availability.get_similar_rooms(status='open')
            if not similar_rooms:
                flash('This room no longer available. Please search for a new room.', 'error')
                return redirect(url_for('search.search'))

            rooms_to_book = similar_rooms.limit(int(rooms))
            rooms_to_book_count = rooms_to_book.count()
            if rooms_to_book_count < int(rooms):
                flash('Not able to book ' + rooms + ' rooms. ' + str(rooms_to_book_count) + ' rooms available.', 'error') 
            one_room = rooms_to_book.first()
            return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate, duration=room_availability.get_duration(),
                               YesNo=YesNo, one_room=one_room, 
                               guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                               requests=requests)

    @bp_payment.route("/process-payment", methods=["POST"])
    def process_payment():
        """
        Process a payment submission.
        
        Validates credit card information and creates bookings.
        
        Returns:
            Redirect: Redirect to bookings or search page based on result.
        """
        print("processing payment...")
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        
        user = User.query.get(session["user_id"])
        
        # Extract payment information from the form
        credit_card_number, exp_date, cvv = FormController.get_payment_information()

        # Extract room information from form
        rid, location_type, startdate, enddate, name, phone, email, guests, rooms, requests = FormController.get_summary_reservation_information(user)

        # Find a valid room to book 
        room_availability = RoomAvailability(startdate=startdate, enddate=enddate)
        room_availability.set_rid_room(rid=rid)
        similar_rooms = room_availability.get_similar_rooms(status='open')
        if not similar_rooms:
            flash('Room no longer available. Please search for a new room.', 'error')
            return redirect(url_for('search.search'))
        rooms_to_book = similar_rooms.limit(int(rooms))
        rooms_to_book_count = rooms_to_book.count()
        one_room = rooms_to_book.first()
        print(one_room)
        rooms_to_book = rooms_to_book.all()
        
        # Create a new CreditCard instance with the provided information
        new_credit_card = Creditcard(credit_card_number, exp_date, cvv)
        
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
                    flash('Room no longer available. Please search for a new room.', 'error')
                    return redirect(url_for('search.search'))
                elif rooms_to_book_count < int(rooms):
                    flash('Not able to book ' + rooms + ' rooms. ' + str(rooms_to_book_count) + ' rooms available.', 'error') 
                    return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate, duration=room_availability.get_duration(),
                                    YesNo=YesNo, one_room=one_room, 
                                    guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                                    requests=requests)                
                # Set check-in and check-out dates
                check_in_date = room_availability.get_starting()
                check_out_date = room_availability.get_ending()
                
                # Create a new booking record
                new_bookings = []
                for room in rooms_to_book:
                    print('inside of loop', room.rate)
                    new_bookings.append(
                        Booking.add_booking(uid=user_id, rid=room.id, check_in=check_in_date, check_out=check_out_date,
                            fees=room.rate, special_requests=requests, name=name, email=email, phone=phone, num_guests=guests
                        )
                    )
                print('booking rooms', new_bookings)
                db.session.add_all(new_bookings)
                db.session.commit()
                print("sending email...")
                email_controller.send_booking_created(user=user, bookings=new_bookings, YesNo=YesNo)
                print("Done sending email")
                print("Card accepted...")
                flash("YOUR CARD HAS BEEN ACCEPTED", "success")
                return redirect(url_for("bookings.bookings"))
                
            except Exception as e:
                db.session.rollback()
                print(f"Database error: {str(e)}", "database_error")
                flash(f"Database error: {str(e)}", "database_error")
                return redirect(url_for('search.search'))
        else:
            # Card is invalid, display appropriate error messages
            flash("INVALID CREDIT CARD DETAILS", "error")
            return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate, duration=room_availability.get_duration(),
                               YesNo=YesNo, one_room=one_room, 
                               guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                               requests=requests)
    
    @bp_payment.route("/booking/<int:booking_id>/receipt/view")
    def view_receipt(booking_id):
        """
        Display an HTML receipt for a booking.
        
        Parameters:
            booking_id (int): The ID of the booking.
            
        Returns:
            Template: The receipt template with booking details.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        
        booking = Booking.query.get(booking_id)
        
        if not booking:
            flash("Booking not found.", "error")
            return redirect(url_for("bookings.bookings"))
        
        if booking.uid != session["user_id"]:
            flash("You don't have permission to view this receipt.", "error")
            return redirect(url_for("bookings.bookings"))
        
        today = datetime.now()
        
        num_nights = (booking.check_out - booking.check_in).days
        if num_nights == 0:
            num_nights = 1
        
        room_rate = booking.rooms.rate
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

    @bp_payment.route("/booking/<int:booking_id>/receipt/download")
    def download_receipt(booking_id):
        """
        Generate and download a PDF receipt for a booking.
        
        Parameters:
            booking_id (int): The ID of the booking.
            
        Returns:
            Response: The PDF receipt file download.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("auth.login"))
        
        booking = Booking.query.get(booking_id)
        
        if not booking:
            flash("Booking not found.", "error")
            return redirect(url_for("bookings.bookings"))
        
        if booking.uid != session["user_id"]:
            flash("You don't have permission to download this receipt.", "error")
            return redirect(url_for("bookings.bookings"))
        
        today = datetime.now()

        num_nights = (booking.check_out - booking.check_in).days
        if num_nights == 0:
            num_nights = 1

        room_rate = booking.rooms.rate
        total_room_charges = room_rate * num_nights
        resort_fee = 30.00 * num_nights
        tax_amount = total_room_charges * 0.15
        total_amount = total_room_charges + resort_fee + tax_amount
        
        receipt_gen = ReceiptGenerator()
        
        pdf_buffer = receipt_gen.generate_receipt(
            booking=booking,
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
    return bp_payment

bp_staff = Blueprint('staff', __name__)
@bp_staff.route("/tasks", methods=["GET", "POST"])
def tasks():
    """
    Display all current service tasks for staff to manage.
    
    Retrieves all service requests from today onwards and displays them
    in chronological order, grouped by booking ID and service type.
    
    Returns:
        Template: The tasks template with all current service requests.

    Note: 
        Author: Avni Israni
        Created: April 12, 2025
        Modified: April 17, 2025
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
    staff = Staff.get_user(session["user_id"])
    if not staff:
        flash("You don't have permission to view this resource.", "error")
        return redirect(url_for("info.home"))
    if request.method == "POST":
        try:
            for key in request.form.keys():
                if key.startswith("staffList_"):
                    sid = int(key.split("_")[1]) #service id
                    service = Service.query.get(sid)
                    if service:
                        staff_id = int(request.form.get(f'staffList_{sid}'))
                        status = request.form.get(f'statusType_{sid}')

                        print(staff_id, status)
                        service.staff_in_charge = staff_id
                        service.update_status(Status(status))
            db.session.commit()
            flash("Tasks updated successfully","success")
        except Exception as e:
            db.session.rollback()
            print(f"Error updating tasks: {str(e)}")
            flash("Unable to update tasks. Please try again later.","error")
    today = date.today()
    current_tasks = Service.get_active_tasks()
    print('Cur',current_tasks)
    assignable_staff = Staff.query.filter(or_(Staff.supervisor_id==staff.id, Staff.id==staff.id)).all()
    
    return render_template('tasks.html', current_tasks=current_tasks, assignable_staff=assignable_staff, Status=Status, SType=SType)


@bp_staff.route("/reports", methods=["GET", "POST"])
def reports():
    """
    Display booking-related reports for the manager to view.
    
    Returns:
        Template: The reports template with all booking-related views.

    Note: 
        Author: Avni Israni
        Created: April 28, 2025
        Modified: April 29, 2025
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
    staff = Staff.get_user(session["user_id"])
    if not staff:
        flash("You don't have permission to view this resource.", "error")
        return redirect(url_for("info.home"))
    

    locations = db.session.query(distinct(Hotel.location)).all()
    location  = request.args.get('location_type')

    if location:
        location = Locations(location)

    service_graph = ReportGenerator.get_service_stats(location)
    completed_booking_graph, pending_booking_graph = ReportGenerator.get_booking_stats(location)
    room_popularity_graph = ReportGenerator.get_room_popularity_stats(location)

    startdate = request.args.get('startdate')
    enddate = request.args.get('enddate')

    if startdate and enddate:
        print("Recieved startdate and enddate")
        try:
            startdate = datetime.strptime(startdate, '%Y-%m-%d')
            enddate = datetime.strptime(enddate, '%Y-%m-%d')
            enddate = enddate.replace(hour=23, minute=59, second=59)
            if enddate < startdate:
                flash("Please select a valid date range", 'error')
                return render_template('reports.html', locations=locations, service_graph=service_graph, completed_booking_graph=completed_booking_graph,
                                    pending_booking_graph=pending_booking_graph, room_popularity_graph=room_popularity_graph)
            print("Adding startdate and enddate to report graphs")
            service_graph = ReportGenerator.get_service_stats(location, startdate, enddate)
            completed_booking_graph, pending_booking_graph = ReportGenerator.get_booking_stats(location, startdate, enddate)
            room_popularity_graph = ReportGenerator.get_room_popularity_stats(location, startdate, enddate)
        except Exception as e:
            print(f'Message: {e}')
            flash("Invalid date format", "error")
    return render_template('reports.html', locations=locations, service_graph=service_graph, completed_booking_graph=completed_booking_graph,
                           pending_booking_graph=pending_booking_graph, room_popularity_graph=room_popularity_graph)


@bp_staff.route("/staff-reports", methods=["GET", "POST"])
def staff_reports():
    """
    Display staff-related reports for the manager to view.
    
    Returns:
        Template: The staff-reports template with all staff-related views.

    Note: 
        Author: Avni Israni
        Created: April 28, 2025
        Modified: April 29, 2025
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("auth.login"))
    staff = Staff.get_user(session["user_id"])
    if not staff:
        flash("You don't have permission to view this resource.", "error")
        return redirect(url_for("info.home"))
    assignable_staff = Staff.query.filter(or_(Staff.supervisor_id==staff.id, Staff.id==staff.id)).all()

    locations = db.session.query(distinct(Hotel.location)).all()
    location  = request.args.get('location_type')

    if location:
        location = Locations(location)

    startdate = request.args.get('startdate')
    enddate = request.args.get('enddate')

    if startdate and enddate:
        try:
            startdate = datetime.strptime(startdate, '%Y-%m-%d')
            enddate = datetime.strptime(enddate, '%Y-%m-%d')
            enddate = enddate.replace(hour=23, minute=59, second=59)
            if enddate < startdate:
                flash("Please select a valid date range", 'error')
                staff_graph = ReportGenerator.get_staff_insights(location, None, None, assignable_staff)
                return render_template('reports_staff.html', staff_graph=staff_graph, startdate=None, enddate=None)
            staff_graph = ReportGenerator.get_staff_insights(location, startdate, enddate, assignable_staff)
            return render_template('reports_staff.html', locations=locations, staff_graph=staff_graph, startdate=None, enddate=None)
        except ValueError:
            flash("Invalid date format", "error")
            staff_graph = ReportGenerator.get_staff_insights(location, None, None, assignable_staff)
    else:
        staff_graph = ReportGenerator.get_staff_insights(location, None, None, assignable_staff)
    return render_template('reports_staff.html', locations=locations, staff_graph=staff_graph, startdate=startdate, enddate=enddate)



def process_query(user_question):
    """
    Process a user query using CSV data first, falling back to AI.
    
    Parameters:
        user_question (str): The user's question.
        
    Returns:
        str: The formatted response to the question.
    """
    global ai_db, ai_model  # Using only the globals that are defined
    
    # Initialize or re-initialize the CSV retrieval system
    ai_db, ai_df = setup_csv_retrieval()  # Get both db and df from the function call
    
    # Use ai_df from the local scope, not trying to access a non-existent global
    csv_answer = get_answer_from_csv(ai_db, ai_df, user_question)
    formatted_response = format_response(csv_answer, user_question)
    
    # If we got a valid formatted response, return it
    if formatted_response:
        return formatted_response
    
    # Otherwise, use the AI model to generate a response
    return generate_ai_response(ai_model, user_question)

def process_query(user_question):
    """
    Process a user query using CSV data first, falling back to AI.
    
    Parameters:
        user_question (str): The user's question.
        
    Returns:
        str: The formatted response to the question.
    """
    global ai_db, ai_df, ai_model
    
    # Try to get an answer from the CSV data first
    csv_answer = get_answer_from_csv(ai_db, ai_df, user_question)
    formatted_response = format_response(csv_answer, user_question)
    
    # If we got a valid formatted response, return it
    if formatted_response:
        return formatted_response
    
    # Otherwise, use the AI model to generate a response
    return generate_ai_response(ai_model, user_question)

def chat_routes():
    """
    Create chat-related routes and register them to a blueprint.
    
    Returns:
        Blueprint: The blueprint with chat routes registered.
    """
    bp_chat = Blueprint('chat', __name__)

    @bp_chat.route("/chat")
    def chat():
        """
        Render the chat interface.
        
        Returns:
            Template: The chat page template.
        """
        return render_template("chat.html")

    @bp_chat.route("/get_response", methods=["POST"])
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
            
    return bp_chat




# static pages -----------------------------------------------------------------------------------------
bp_info = Blueprint('info',__name__)

@bp_info.route("/")
def home():
    """
    Render the home page with a list of available hotel locations.
    
    Returns:
        Template: The rendered home page template.

    Note:
        Author: Devansh Sharma
        Modified: April 17, 2025
    """
    locations = db.session.query(distinct(Hotel.location)).all()
    return render_template("home.html", locations=locations)

@bp_info.route("/terms")
def terms():
    """
    Render the terms and conditions page.
    
    Returns:
        Template: The terms page template.

    Note:
        Author: Devansh Sharma
        Modified: April 17, 2025
    """
    return render_template('terms.html')

@bp_info.route("/events")
def events():
    """
    Render the events page.
    
    Returns:
        Template: The events page template.

    Note:
        Author: Elijah Cortez
        Modified: April 17, 2025
    """
    return render_template('events.html')

@bp_info.route("/menu")
def menu():
    """
    Render the restaurant menu page.
    
    Returns:
        Template: The menu page template.

    Note:
        Author: Andrew Ponce
        Modified: April 17, 2025
    """
    return render_template('menus2.html')

@bp_info.route("/about")
def about():
    """
    Render the about page.
    
    Returns:
        Template: The about page template.

    Note:
        Author: Eiji Cortez
        Modified: April 17, 2025
    """
    return render_template('about.html')

@bp_info.route("/amenities")
def amenities():
    """
    Render the amenities page.
    
    Returns:
        Template: The amenities page template.

    Note:
        Author: Eiji Cortez
        Modified: April 29, 2025
    """
    return render_template('amenities.html')

@bp_info.route("/faq")
def faq():
    """
    Render the FAQ page with all FAQs from the database.
    
    Returns:
        Template: The FAQ page template with FAQs.

    Note:
        Author: Avni Israni
        Modified: April 17, 2025
    """
    faqs = FAQ.query.all()
    return render_template('faq.html', faqs=faqs)
