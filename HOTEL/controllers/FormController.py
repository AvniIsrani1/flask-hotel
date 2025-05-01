from flask import request
from ..entities import YesNo

class FormController():
    """
    Handles form data extraction from HTTP requests for various pages. 
    Returns parsed and validated data to be used for further operations.

    Author: Avni Israni
    Documentation: Avni Israni
    Created: April 17, 2025
    Modified: April 18, 2025
    """

    @classmethod
    def get_signup_information(cls):
        """
        Retrieve signup information from the POST form on the signup page.

        Parameters: 
            None

        Returns:
            tuple: A tuple containing:
                str: name - The user's name.
                str: email - The user's email address.
                str: password - The user's plaintext password.
                str: confirm_password - The user's plaintext confirmation password.
        """
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        return name, email, password, confirm_password
    
    @classmethod
    def get_login_information(cls):
        """
        Retrieve login information from the POST form on the login page.

        Parameters: 
            None

        Returns:
            tuple: A tuple containing:
                str: email - The user's email address.
                str: password - The user's plaintext password.
        """
        email = request.form.get("email")
        password = request.form.get("password")
        return email, password
    
    @classmethod
    def get_profile_update_information(cls):
        """
        Retrieve profile information from the POST form on the profile page.

        Parameters:
            None

        Returns:
            tuple: A tuple containing: 
                str: name - The new name.
                str: phone - The new phone number.
                str: address_line1 - The new address line 1.
                str: address_line2 - The new address line 2.
                str: city - The new city.
                str: state - The new state.
                str: zipcode - The new zipcode.
        """
        name = request.form.get("name")
        phone = request.form.get("phone")
        address_line1 = request.form.get("address")
        address_line2 = request.form.get("address2")
        city = request.form.get("city")
        state = request.form.get("state")
        zipcode = request.form.get("zipcode")
        return name, phone, address_line1, address_line2, city, state, zipcode
    
    @classmethod
    def get_profile_notification_information(cls):
        """
        Retrieve notification information from the POST form on the profile page. 

        Parameters:
            None
        
        Returns:
            tuple: A tuple containing:
                YesNo: tremind - YesNo.Y if text notifications were checked, else YesNo.N.
                YesNo: eremind - YesNo.Y if email notifications were checked, else YesNo.N.
        """
        tremind = YesNo.Y if request.form.get('tremind') is not None else YesNo.N
        eremind = YesNo.Y if request.form.get('eremind') is not None else YesNo.N
        return tremind, eremind

    @classmethod
    def get_main_search(cls):
        """
        Retrieve broad search information from the GET form on the search page. 

        Parameters:
            None

        Returns:
            tuple: A tuple containing:
                str: location - The retrieved location.
                str: start - The retrieved start date.
                str: end - The retrieved end date.
        """
        location = request.args.get('location_type')
        start = request.args.get('startdate') 
        end = request.args.get('enddate') 
        return location, start, end
    
    @classmethod
    def get_filters_search(cls):
        """
        Retrieve filters to be applied on the search from the GET form on the search page.

        Parameters:
            None

        Returns:
            tuple: A tuple containing:
                str: room_type - The type of room to search for.
                str: bed_type - The number of beds in the room.
                str: view - The type of view (ocean or city).
                str: balcony - The balcony status (balcony or no_balcony).
                str: smoking_preference - The smoking preference (Smoking or Non-Smoking).
                str: accessibility - The accessibility needs desired (wheelchair or '').
                str: price_range - The maximum price range to search through.
        """
        room_type = request.args.get('room_type')
        bed_type = request.args.get('bed_type')
        view = request.args.get('view')
        balcony = request.args.get('balcony')
        smoking_preference = request.args.get('smoking_preference')
        accessibility = request.args.get('accessibility')
        price_range = request.args.get('price_range')
        return room_type, bed_type, view, balcony, smoking_preference, accessibility, price_range

    @classmethod
    def get_booking_reservation_information(cls):
        """
        Retrieve overarching booking reservation information from the GET form.

        Parameters:
            None

        Returns:
            tuple: A tuple containing:
                str: rid - The room ID that represents the desired room characteristics.
                str: location_type - The location of the hotel.
                str: startdate - The start date of the booking.
                str: enddate - The end date of the booking.
        """
        rid = request.args.get('rid')
        location_type = request.args.get('location_type')
        startdate = request.args.get('startdate')
        enddate = request.args.get('enddate')
        return rid, location_type, startdate, enddate

    @classmethod
    def get_make_reservation_information(cls, user):
        """
        Retrieve user-specific booking reservation details from the POST form.

        Parameters:
            None

        Returns:
            tuple: A tuple containing:
                str: name - The name to be associated with the reservation(s).
                str: phone - The phone number to be associated with the reservation(s).
                str: email - The email address to be associated with the reservation(s).  
                str: guests - The number of guests to be associated with the reservation(s).
                str: rooms - The number of rooms to be reserved.
                str: requests - Special requests to be associated with the reservation(s).
        """
        name=request.form.get('name', user.name)
        phone=request.form.get('phone', user.phone)
        email=request.form.get('email', user.email)
        guests=request.form.get('guests',1)
        rooms=request.form.get('rooms',1)
        requests=request.form.get('requests','')
        return name, phone, email, guests, rooms, requests
    
    @classmethod
    def get_summary_reservation_information(cls, user):
        """
        Retrieve all booking reservation details from the POST form.

        Parameters:
            None

        Returns:
            tuple: A tuple containing:
                str: rid - The room ID that represents the desired room characteristics.
                str: location_type - The location of the hotel.
                str: startdate - The start date of the booking.
                str: enddate - The end date of the booking.
                str: name - The name to be associated with the reservation(s).
                str: phone - The phone number to be associated with the reservation(s).
                str: email - The email address to be associated with the reservation(s).  
                str: guests - The number of guests to be associated with the reservation(s).
                str: rooms - The number of rooms to be reserved.
                str: requests - Special requests to be associated with the reservation(s).
        """
        rid = request.form.get('rid') 
        location_type = request.form.get('location_type')
        startdate = request.form.get('startdate')
        enddate = request.form.get('enddate')
        name, phone, email, guests, rooms, requests = cls.get_make_reservation_information(user)
        return rid, location_type, startdate, enddate, name, phone, email, guests, rooms, requests
    
    @classmethod
    def get_update_booking_information(cls, booking):
        """
        Retrieve booking reservation details from the form on the modify page. 

        Parameters: 
            booking (Booking): The booking object whose details should be defaulted to if missing information is provided. 
        
        Returns:
            tuple: A tuple containing:
                str: special_requests - Updated requests for the booking.
                str: name - Updated name for the booking, defaults to booking's name information if none is provided.
                str: email - Updated email for the booking, defaults to booking's email information if none is provided.
                str: phone - Updated phone number for the booking, defaults to booking's phone number information if none is provided.
                str: num_guests - Updated num_guests for the booking, defaults to booking's num_guests information if none is provided.
        """
        special_requests=request.form.get('requests')
        name=request.form.get('name', booking.name)
        email = request.form.get('email', booking.email)
        phone=request.form.get('phone', booking.phone)
        num_guests=request.form.get('guests')
        return special_requests, name, email, phone, num_guests
    
    @classmethod
    def get_service_request_information(cls):
        """
        Retrieve service request information from the form on the request services page.

        Parameters:
            None

        Returns:
            tuple: A tuple containing:
                str: robes - The number of robes requested, defaults to 0 if empty.
                str: btowels - The number of bath towels requested, defaults to 0 if empty.
                str: htowels - The number of hand towels requested, defaults to 0 if empty.
                str: soap - The number of soap bottles requested, defaults to 0 if empty.
                str: shampoo - The number of shampoo bottles requested, defaults to 0 if empty.
                str: conditioner - The number of conditioner bottles requested, defaults to 0 if empty.
                str: wash - The number of bath wash bottles requested, defaults to 0 if empty.
                str: lotion - The number of lotion bottles requested, defaults to 0 if empty.
                str: hdryer - The number of hair dryers requested, defaults to 0 if empty.
                str: pillows - The number of pillows requested, defaults to 0 if empty.
                str: blankets - The number of blankets requested, defaults to 0 if empty.
                str: sheets - The number of sheets requested, defaults to 0 if empty.
                str: housetime - The time at which housekeeping is requested.
                str: trash - A trash pickup request if not empty.
                str: calltime - The time at which a wakeup call is requested.
                str: recurrent - The status on if a wakeup call should be recurrent (every day until check out).
                str: restaurant - The restaurant to be reserved.
                str: assistance - The type of assistance that is needed.
                str: other - Other services that are needed.
        """
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

        housetime = request.form.get('housetime')
        trash = request.form.get('trash')

        calltime = request.form.get('calltime')
        recurrent = request.form.get('recurrent')

        restaurant = request.form.get('restaurant')

        assistance = request.form.get('assistance')

        other = request.form.get('other')
        return robes, btowels, htowels, soap, shampoo, conditioner, wash, lotion, hdryer, pillows, blankets, sheets, housetime, trash, calltime, recurrent, restaurant, assistance, other


    @classmethod
    def get_payment_information(cls):
        """
        Retrieve credit card information from POST form on payment page.

        Parameters: 
            None

        Returns:
            tuple: A tuple containing:
                str: credit_card_number - The entered credit card number.
                str: exp_date - The expiration date of the credit card.
                str: cvv - The cvv of the credit card.
            
        """
        credit_card_number = request.form.get("card-number")
        exp_date = request.form.get("expiry")
        cvv = request.form.get("cvv")
        return credit_card_number, exp_date, cvv