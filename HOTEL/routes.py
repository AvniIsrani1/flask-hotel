from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from .db import db
from sqlalchemy import DateTime, Date, cast, distinct, desc, asc, cast, func, not_, String, Computed
from datetime import datetime, date, timedelta
from .entities import Users, Bookings, Services, Hotel, Floor, Room, YesNo, Assistance, Locations, Availability, RoomType, Status, SType
from .controllers import SearchController, FormController, RoomAvailability
from datetime import datetime

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
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.sign_up"))
        
        # Check if email already exists
        if not Users.unique_email(email):
            flash("Email already registered. Please use a different email or login.", "error")
            return redirect(url_for("auth.sign_up"))
        
        # Create a new user
        user = Users.create_initial_user(name, email, password)
        
        try:
            # Save the new user to the database
            db.session.add(user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            
            # If you have email functionality, you might want to send a welcome email here
            email_controller.send_welcome_email(user=user)
            
            return redirect(url_for("auth.log_in"))
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
            return redirect(url_for("auth.log_in"))
    
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
    return redirect(url_for("home"))

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
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    user = Users.query.get(session["user_id"])
    if not user:
        flash('Account not found','error')
        session.clear()
        return redirect(url_for("log_in"))
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
    
    Args:
        email_controller (EmailController): The email controller for sending notifications.
        
    Returns:
        Blueprint: The blueprint with booking routes registered.
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
            return redirect(url_for("log_in"))
        user_id = session["user_id"]
        user = Users.get_user(user_id)

        current = Bookings.get_current_user_bookings(user_id)
        print(current)
        future = Bookings.get_future_user_bookings(user_id)
        print(future)
        past = Bookings.get_past_user_bookings(user_id)
        canceled = Bookings.get_canceled_user_bookings(user_id)

        return render_template('bookings.html', current=current, future=future, past=past, canceled=canceled, YesNo=YesNo)

    @bp_bookings.route("/modify/<int:bid>", methods=["GET", "POST"])
    def modify(bid):
        """
        Modify an existing booking.
        
        Args:
            bid (int): The booking ID to modify.
            
        Returns:
            Template: The reservation form with booking data.
            Redirect: Redirect to bookings page if booking not found.
        """
        modifying = True
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("log_in"))
        user_id = session["user_id"]
        user = Users.get_user(user_id)
        booking = Bookings.get_booking(bid)

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
        
        Args:
            bid (int): The booking ID to save changes for.
            
        Returns:
            Redirect: Redirect to bookings page after processing.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("log_in"))
        user = Users.query.get(session["user_id"])
        booking = Bookings.query.get(bid)
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
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])
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
    
    Args:
        bid (int): The booking ID to request services for.
        
    Returns:
        Template: The service request form template.
        Redirect: Redirect to bookings page after processing.
    """
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])
    if request.method == 'POST':
        #making sure user has active bid
        booking = Bookings.get_specific_current_user_bookings(uid=user.id, bid=bid)
        if not booking:
            flash("You do not have an active booking for this request.",'error')
            return redirect(url_for('bookings.bookings'))
        robes, btowels, htowels, soap, shampoo, conditioner, wash, lotion, hdryer, pillows, blankets, sheets, housetime, trash, calltime, recurrent, restaurant, assistance, other = FormController.get_service_request_information()
        print(robes,btowels,htowels,soap,shampoo,conditioner,wash,lotion,hdryer,pillows,blankets,sheets)
        services = []
        if robes or btowels or htowels or soap or shampoo or conditioner or wash or lotion or hdryer or pillows or blankets or sheets:
            services.append(Services.add_item(bid=bid, robes=robes, btowels=btowels, htowels=htowels, soap=soap, shampoo=shampoo,
                                                    conditioner=conditioner, wash=wash, lotion=lotion, hdryer=hdryer, pillows=pillows,
                                                    blankets=blankets, sheets=sheets))
        if housetime:
            print('before',housetime)
            housetime = datetime.strptime(housetime,"%H:%M").time()
            print('after',housetime)
            services.append(Services.add_housekeeping(bid=bid, housetime=housetime, validate_check_out=booking.check_out))
        if trash:
            services.append(Services.add_trash(bid=bid))
        if calltime:
            print('before',calltime)
            calltime = datetime.strptime(calltime, "%H:%M").time()
            print('after',calltime)
            if recurrent:
                services.extend(Services.add_call(bid=bid, calltime=calltime, recurrent=True, validate_check_out=booking.check_out))
            else:
                services.extend(Services.add_call(bid=bid, calltime=calltime, recurrent=False, validate_check_out=booking.check_out))
        if restaurant:
            services.append(Services.add_dining(bid=bid, restaurant=restaurant))
        if assistance:
            assistance = Assistance(assistance)
            services.append(Services.add_assistance(bid=bid, assistance=assistance))
        if other:
            services.append(Services.add_other(bid=bid, other=other))
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

bp_staff = Blueprint('staff', __name__)
@bp_staff.route("/tasks", methods=["GET", "POST"])
def tasks():
    """
    Display all current service tasks for staff to manage.
    
    Retrieves all service requests from today onwards and displays them
    in chronological order, grouped by booking ID and service type.
    
    Returns:
        Template: The tasks template with all current service requests.
    """
    today = date.today()
    current_tasks = Services.query.filter(cast(Services.issued, Date) >= today).order_by(
            asc(Services.issued), asc(Services.bid), asc(Services.stype)
        ).all()
    print(current_tasks)
    return render_template('tasks.html', current_tasks=current_tasks, Status=Status, SType=SType)