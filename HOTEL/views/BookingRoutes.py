from flask import Blueprint, request, render_template, flash, redirect, session, url_for
from ..entities import User, Booking, Service, YesNo, Assistance
from ..controllers import FormController
from ..Services import RoomAvailability
from ..db import db
from datetime import datetime 

class BookingRoutes:
    """
    Class containing booking-related routes. 

    Note: 
        Author: Avni Israni
        Created: February 18, 2025
        Modified: April 17, 2025
    """
    def __init__(self, app, email_controller):
        """
        Create booking-related routes and register them to a blueprint.
    
        Parameters:
            app (Flask): The Flask app instance
            email_controller (EmailController): The email controller for sending notifications.
        
        Returns:
            None
        """
        self.bp = Blueprint('bookings', __name__)
        self.email_controller = email_controller
        self.setup_routes()
        app.register_blueprint(self.bp)

    def setup_routes(self):
        self.bp.route('/bookings', methods=["GET", "POST"])(self.bookings)
        self.bp.route('/modify/<int:bid>', methods=["GET", "POST"])(self.modify)
        self.bp.route('/save/<int:bid>', methods=["GET", "POST"])(self.save)
        self.bp.route('/request-services/<int:bid>', methods=["GET", "POST"])(self.request_services)

    def bookings(self):
        """
        Display user's bookings organized by status.
        
        Returns:
            Template: The bookings template with all user bookings.
            Redirect: Redirect to login page if not logged in.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("userinfo.login"))
        user_id = session["user_id"]

        current = Booking.get_current_user_bookings(user_id)
        print(current)
        future = Booking.get_future_user_bookings(user_id)
        print(future)
        past = Booking.get_past_user_bookings(user_id)
        canceled = Booking.get_canceled_user_bookings(user_id)

        return render_template('bookings.html', current=current, future=future, past=past, canceled=canceled, YesNo=YesNo)

    def modify(self, bid):
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
            return redirect(url_for("userinfo.login"))
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

    def save(self, bid):
        """
        Save changes to a booking or cancel it.
        
        Parameters:
            bid (int): The booking ID to save changes for.
            
        Returns:
            Redirect: Redirect to bookings page after processing.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("userinfo.login"))
        user = User.query.get(session["user_id"])
        booking = Booking.query.get(bid)
        message = status = ''
        if booking:
            canceled = request.form.get('canceled', 'false')
            if canceled=='true':
                booking.cancel()
                self.email_controller.send_booking_canceled(user=user,booking=booking,YesNo=YesNo)
                message='Booking canceled!'
                status = 'success'
            else:
                special_requests, name, email, phone, num_guests = FormController.get_update_booking_information(booking)
                booking.update_booking(special_requests=special_requests, name = name, email = email, phone = phone, num_guests = num_guests)
                self.email_controller.send_booking_updated(user=user,booking=booking,YesNo=YesNo)
                message='Booking updated!'
                status='success'
            try:
                db.session.commit()
                flash(message, status)
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}. Please try again later.", "error")
        return redirect(url_for('bookings.bookings'))
    
    def request_services(self, bid):
        """
        Handle guest service requests for a booking.
        
        GET: Display the service request form.
        POST: Process the service request submissions.
        
        Parameters:
            bid (int): The booking ID to request services for.
            
        Returns:
            Template: The service request form template.
            Redirect: Redirect to bookings page after processing.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("userinfo.login"))
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
