from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from .db import db
from sqlalchemy import DateTime, distinct, desc, asc, cast, func, not_, String, Computed
from datetime import datetime, timedelta
from .model_dbs import Users, Bookings, Services, Hotel, Floor, Room, YesNo, Assistance, Locations, Availability, RoomType
from .model_objects import Service
from .model_general import SearchController
from .model_general import RoomAvailability
from datetime import datetime

bp_profile = Blueprint('profile',__name__)
@bp_profile.route("/profile",methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    user_db = Users.query.get(session["user_id"])
    if not user_db:
        flash('Account not found','error')
        session.clear()
        return redirect(url_for("log_in"))
    user = user_db.create_user_object()
    if user.first_login:
        flash("Please update your profile information!", "action")
    message = status = ''
    if request.method == "POST":
        ptype = request.form.get('ptype')
        if ptype == 'profile':
            user.update_profile(
                name = request.form.get("name"),
                phone = request.form.get("phone"),
                address_line1 = request.form.get("address"),
                address_line2 = request.form.get("address2"),
                city = request.form.get("city"),
                state = request.form.get("state"),
                zipcode = request.form.get("zipcode")
            )
            message = 'Profile has been updated!'
            status = 'success'
        elif ptype=='notifications':
            tremind = request.form.get('tremind') is not None
            eremind = request.form.get('eremind') is not None
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
            db.session.delete(user_db)
            session.clear()
            db.session.commit()
            return render_template("home.html")
        try:
            result = Users.update_users_db(user)
            print(f'Update result: {result}')
            db.session.commit()
            print('Successful commit')
            flash(message, status)
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}. Please try again later.", "error")
        finally:
            return redirect(url_for("profile.profile"))
    return render_template("profile.html", user=user_db, YesNo = YesNo)


bp_bookings = Blueprint('bookings',__name__)
@bp_bookings.route("/bookings", methods=["GET", "POST"])
def bookings():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])

    current = Bookings.get_current_user_bookings(Bookings.uid==user.id).all()
    print(current)
    future = Bookings.get_future_user_bookings(Bookings.uid==user.id).all()
    print(future)
    past = Bookings.get_past_user_bookings(Bookings.uid==user.id).all()
    canceled = Bookings.get_canceled_user_bookings(Bookings.uid==user.id).all()

    return render_template('bookings.html', current=current, future=future, past=past, canceled=canceled, YesNo=YesNo)

@bp_bookings.route("/modify/<int:bid>", methods=["GET", "POST"])
def modify(bid):
    modifying = True
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])
    booking_db = Bookings.query.get(bid)
    booking = booking_db.create_booking_object()

    if not booking:
        flash('Unable to modify booking. Please try again later', 'error')
        return redirect(url_for('bookings.bookings'))
    
    startdate = booking.check_in.strftime("%B %d, %Y")
    enddate = booking.check_out.strftime("%B %d, %Y")

    room_availability = RoomAvailability(startdate=startdate,enddate=enddate)
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
                            name=booking_db.name, phone=booking_db.phone,email=booking_db.email,guests=booking_db.num_guests,rooms=rooms,requests=booking_db.special_requests, 
                            modifying=modifying, bid=bid)

@bp_bookings.route("/save/<int:bid>", methods=["GET", "POST"])
def save(bid): #currently not able to add more rooms by modifying existing booking
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])
    booking_db = Bookings.query.get(bid)
    booking = booking_db.create_booking_object()
    message = status = ''
    if booking:
        canceled = request.form.get('canceled', 'false')
        if canceled=='true':
            booking.cancel()
            # send_email(subject='Ocean Vista Booking Canceled!',recipients=[user.email], body="Your booking has been canceled!",
            #            body_template='emails/canceled.html',user=user, booking=b, YesNo=YesNo)
            message='Booking canceled!'
            status = 'success'
        else:
            booking.update_booking(special_requests=request.form.get('requests'), 
                             name=request.form.get('name', booking.name), 
                             email = request.form.get('email', booking.email), 
                             phone=request.form.get('phone', booking.phone), 
                             num_guests=request.form.get('guests'))
            # send_email(subject=f'Ocean Vista Booking Updated - {b.id}!',recipients=[user.email], body="Your booking has been updated!",
            #            body_template='emails/updated.html',user=user, booking=b, YesNo=YesNo)
            message='Booking updated!'
            status='success'
        try:
            result = Bookings.update_bookings_db(booking)
            print(f'Update result: {result}')
            db.session.commit()
            print('Successful commit')
            flash(message, status)
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}. Please try again later.", "error")
    return redirect(url_for('bookings.bookings'))

bp_reserve = Blueprint('reserve',__name__)
@bp_reserve.route("/reserve", methods=["GET", "POST"])
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
            return redirect(url_for('search.search'))
        print(f"Received rid: {rid}, location_type: {location_type}, startdate: {startdate}, enddate: {enddate}") 
        room_availability = RoomAvailability(startdate=startdate,enddate=enddate)
        room_availability.set_rid_room(rid=rid)
        room=room_availability.get_similar_quantities(status='open').first()
        if not room:
            flash('Room not found',"error")
            return redirect(url_for('search.search'))
        if request.method=='POST':
            name=request.form.get('name', user.name)
            phone=request.form.get('phone', user.phone)
            email=request.form.get('email', user.email)
            guests=request.form.get('guests',1)
            rooms=request.form.get('rooms',1)
            requests=request.form.get('requests','')
            return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=room_availability.get_duration(), startdate=startdate, enddate=enddate,
                                   name=name, phone=phone,email=email,guests=guests,rooms=rooms,requests=requests)
        
        return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=room_availability.get_duration(), startdate=startdate, enddate=enddate)

bp_request_services = Blueprint('request_services',__name__)
@bp_request_services.route("/request-services/<int:bid>", methods=["GET","POST"])
def request_services(bid):
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    user = Users.query.get(session["user_id"])
    if request.method == 'POST':
        #making sure user has active bid
        booking = Bookings.get_current_user_bookings(uid=user.id).filter(Bookings.id==bid).first()
        if not booking:
            flash("You do not have an active booking for this request.",'error')
            return redirect(url_for('bookings.bookings'))
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
        service_objects = []
        if robes or btowels or htowels or soap or shampoo or conditioner or wash or lotion or hdryer or pillows or blankets or sheets:
            service_objects.append(Service.add_item(bid=bid,robes=robes,btowels=btowels,htowels=htowels,soap=soap,shampoo=shampoo,
                                                    conditioner=conditioner,wash=wash,lotion=lotion,hdryer=hdryer,pillows=pillows,
                                                    blankets=blankets,sheets=sheets))
        housetime = request.form.get('housetime')
        if housetime:
            print('before',housetime)
            housetime = datetime.strptime(housetime,"%H:%M").time()
            print('after',housetime)
            service_objects.append(Service.add_housekeeping(bid=bid,housetime=housetime,validate_check_out=booking.check_out))
        trash = request.form.get('trash')
        if trash:
            service_objects.append(Service.add_trash(bid=bid))
        calltime = request.form.get('calltime')
        recurrent = request.form.get('recurrent')
        if calltime:
            print('before',calltime)
            calltime = datetime.strptime(calltime, "%H:%M").time()
            print('after',calltime)
            if recurrent:
                service_objects.extend(Service.add_call(bid=bid,calltime=calltime,recurrent=True,validate_check_out=booking.check_out))
            else:
                service_objects.extend(Service.add_call(bid=bid,calltime=calltime,recurrent=False,validate_check_out=booking.check_out))
        # restaurant = request.form.get('restaurant')
        # if restaurant:
        #     service_objects.append(Service.add_re(bid=bid,housetime=housetime,validate_check_out=booking.check_out))
        assistance = request.form.get('assistance')
        if assistance:
            assistance = Assistance(assistance)
            service_objects.append(Service.add_assistance(bid=bid,assistance=assistance))
        other = request.form.get('other')
        if other:
            service_objects.append(Service.add_other(bid=bid,other=other))
        try:
            results=Services.create_services_db(service_objects)
            print(f'Update result: {results}')
            db.session.add_all(results)
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
    locations = db.session.query(distinct(Hotel.location)).all()
    roomtypes = db.session.query(distinct(cast(Room.room_type, String))).order_by(desc(cast(Room.room_type, String))).all()
    
    search_controller = SearchController()
    if request.method == "GET":
        stype = request.args.get('stype')
        # if stype == 'apply_search':
        location = request.args.get('location_type')
        start = request.args.get('startdate') 
        end = request.args.get('enddate') 
        starting, ending,result = search_controller.main_search(location=location,start=start,end=end)
        if(not result):
            flash('Please enter both the start and end dates',"error")
            return redirect(url_for('search.search', startdate=starting, enddate=ending))
        if stype=='apply_filters':
            room_type = request.args.get('room_type')
            bed_type = request.args.get('bed_type')
            view = request.args.get('view')
            balcony = request.args.get('balcony')
            smoking_preference = request.args.get('smoking_preference')
            accessibility = request.args.get('accessibility')
            price_range = request.args.get('price_range')
            search_controller.filter_search(room_type=room_type,bed_type=bed_type,view=view,balcony=balcony,
                           smoking_preference=smoking_preference,accessibility=accessibility,
                           price_range=price_range)
    sort = request.args.get('sort-by')
    search_controller.sort_search(sort=sort)
    search_controller.get_quantities()
    rooms = search_controller.get_search()
    print(rooms)
    return render_template('search.html', locations=locations, roomtypes=roomtypes, rooms=rooms, YesNo = YesNo)
