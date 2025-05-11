from flask import Blueprint, request, render_template, flash, redirect, session, url_for, send_file
from ..entities import User, Booking, YesNo, Creditcard
from ..controllers import FormController
from ..services import ReceiptGenerator, RoomAvailability
from ..db import db
from datetime import datetime

class PaymentRoutes:
    """
    Create payment related routes.

    Note:
        Author: Devansh Sharma, Andrew Ponce
        Created: March 11, 2025
        Modified: May 1, 2025
    """

    def __init__(self, app, email_controller):
        """
        Create payment-related routes and register them to a blueprint.
        
        Parameters:
            email_controller (EmailController): The email controller for sending notifications.
            
        Returns:
            Blueprint: The blueprint with payment routes registered.
        """
        self.bp = Blueprint('payment', __name__)
        self.email_controller = email_controller
        self.setup_routes()
        app.register_blueprint(self.bp)

    def setup_routes(self):
        """
        Map the payment-related HTTP routes to their respective handler functions.

        Parameters:
            None

        Returns:
            None 
        """
        self.bp.route('/payment', methods=["GET", "POST"])(self.payment)
        self.bp.route('/process-payment', methods=["POST"])(self.process_payment)
        self.bp.route('/booking/<int:booking_id>/receipt/view')(self.view_receipt)
        self.bp.route('/booking/<int:booking_id>/receipt/download')(self.download_receipt)

    def payment(self):
        """
        Handle the payment page.
        
        GET: Display the payment form.
        POST: Process the payment form data and show the payment form.
        
        Returns:
            Template: The payment form template.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("userinfo.login"))
        user = User.query.get(session["user_id"])
        if user is None:
            flash("User is not valid","error")
            return redirect(url_for("userinfo.login"))
        if request.method == 'POST':
            rid, location_type, startdate, enddate, name, phone, email, guests, rooms, requests = FormController.get_summary_reservation_information(user)
            try:
                startdate_asdatetime = datetime.strptime(startdate, "%B %d, %Y")
                enddate_asdatetime = datetime.strptime(enddate, "%B %d, %Y")
            except ValueError as e:
                flash("Invalid date format. Please ensure the dates are in the correct format.", "error")
                return redirect(url_for('details.search'))
            if startdate_asdatetime >= enddate_asdatetime:
                print("startdate >= enddate, redirecting...")
                flash('Please enter a valid start and end date',"error")
                return redirect(url_for('details.search'))
            room_availability = RoomAvailability(startdate=startdate, enddate=enddate)
            room_availability.set_rid_room(rid=rid)
            similar_rooms = room_availability.get_similar_rooms(status='open')
            if not similar_rooms:
                flash('This room no longer available. Please search for a new room.', 'error')
                return redirect(url_for('details.search'))

            rooms_to_book = similar_rooms.limit(int(rooms))
            rooms_to_book_count = rooms_to_book.count()
            if rooms_to_book_count < int(rooms):
                flash('Not able to book ' + rooms + ' rooms. ' + str(rooms_to_book_count) + ' rooms available.', 'error') 
            one_room = rooms_to_book.first()
            return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate, duration=room_availability.get_duration(),
                               YesNo=YesNo, one_room=one_room, 
                               guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                               requests=requests)

    def process_payment(self):
        """
        Process a payment submission.
        
        Validates credit card information and creates bookings.
        
        Returns:
            Redirect: Redirect to bookings or search page based on result.
        """
        print("processing payment...")
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("userinfo.login"))
        
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
            return redirect(url_for('details.search'))
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
                    return redirect(url_for('details.search'))
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
                self.email_controller.send_booking_created(user=user, bookings=new_bookings, YesNo=YesNo)
                print("Done sending email")
                print("Card accepted...")
                flash("YOUR CARD HAS BEEN ACCEPTED", "success")
                return redirect(url_for("bookings.bookings"))
                
            except Exception as e:
                db.session.rollback()
                print(f"Database error: {str(e)}", "database_error")
                flash(f"Database error: {str(e)}", "database_error")
                return redirect(url_for('details.search'))
        else:
            # Card is invalid, display appropriate error messages
            flash("INVALID CREDIT CARD DETAILS", "error")
            return render_template('payment.html', rid=rid, location_type=location_type, startdate=startdate, enddate=enddate, duration=room_availability.get_duration(),
                               YesNo=YesNo, one_room=one_room, 
                               guests=guests, rooms=rooms_to_book_count, name=name, email=email, phone=phone,
                               requests=requests)
    
    def view_receipt(self, booking_id):
        """
        Display an HTML receipt for a booking.
        
        Parameters:
            booking_id (int): The ID of the booking.
            
        Returns:
            Template: The receipt template with booking details.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("userinfo.login"))
        
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

    def download_receipt(self, booking_id):
        """
        Generate and download a PDF receipt for a booking.
        
        Parameters:
            booking_id (int): The ID of the booking.
            
        Returns:
            Response: The PDF receipt file download.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("userinfo.login"))
        
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

