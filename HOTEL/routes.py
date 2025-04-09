from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from .db import db
from .model_dbs import Users, Bookings, YesNo
from .models import Room, Hotel
from .utility.RoomAvailability import RoomAvailability

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

    current = Bookings.get_current_bookings().join(Room).join(Hotel).filter(Bookings.uid==user.id).all()
    future = Bookings.get_future_bookings().filter(Bookings.uid==user.id).all()
    past = Bookings.get_past_bookings().filter(Bookings.uid==user.id).all()
    canceled = Bookings.get_canceled_bookings().filter(Bookings.uid==user.id).all()

    return render_template('bookings.html', current=current, future=future, past=past, canceled=canceled, YesNo=YesNo)

@bp_bookings.route("/modify/<int:bid>", methods=["GET", "POST"])
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
    starting, ending, duration = RoomAvailability.get_start_end_duration(startdate, enddate)
    room = RoomAvailability.get_similar_quantities(rid=booking.rid, starting=starting, ending=ending, status="any").first()
    print(room)
    rid = booking.rid
    rooms = 1 #user is able to modify 1 room at a time
    location_type = None
    return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=duration, startdate=startdate, enddate=enddate,
                            name=booking.name, phone=booking.phone,email=booking.email,guests=booking.num_guests,rooms=rooms,requests=booking.special_requests, 
                            modifying=modifying, bid=bid)

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
            return redirect(url_for('search'))
        print(f"Received rid: {rid}, location_type: {location_type}, startdate: {startdate}, enddate: {enddate}") 
        starting, ending, duration = RoomAvailability.get_start_end_duration(startdate, enddate)
        room = RoomAvailability.get_similar_quantities(rid=rid, starting=starting, ending=ending, status='open').first()

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

