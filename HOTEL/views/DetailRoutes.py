from flask import Blueprint, request, render_template, flash, redirect, session, url_for
from ..entities import User, Hotel, Room, YesNo
from ..controllers import FormController, RoomAvailability, SearchController
from ..db import db
from sqlalchemy import distinct, cast, String, desc

class DetailRoutes:
    """
    Create room-detail and booking-detail related routes.

    Note:
        Author: Avni Israni
        Created: March 18, 2025
        Modified: May 1, 2025
    """

    def __init__(self, app):
        """
        Create room/booking detail-related routes and register them to a blueprint.
        
        Parameters:
            app (Flask): The Flask app instance. 
            
        Returns:
            None
        """
        self.bp = Blueprint('details', __name__)
        self.setup_routes()
        app.register_blueprint(self.bp)

    def setup_routes(self):
        self.bp.route('/search', methods=["GET", "POST"])(self.search)
        self.bp.route('/reserve', methods=["GET", "POST"])(self.reserve)

    def reserve(self):
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
            return redirect(url_for("userinfo.login"))
        user = User.query.get(session["user_id"])
        if request.method=='GET' or request.method=='POST':
            rid, location_type, startdate, enddate = FormController.get_booking_reservation_information()
            if not startdate or not enddate:
                if not rid:
                    flash("Reservation details are missing. Please search for a room again.", "error")
                else:
                    flash('Please enter both the start and end dates',"error")
                return redirect(url_for('details.search'))
            print(f"Received rid: {rid}, location_type: {location_type}, startdate: {startdate}, enddate: {enddate}") 
            if startdate >= enddate:
                flash('Please enter a valid start and end date',"error")
                return redirect(url_for('details.search'))
            room_availability = RoomAvailability(startdate=startdate,enddate=enddate)
            room_availability.set_rid_room(rid=rid)
            room=room_availability.get_similar_quantities(status='open').first()
            if not room:
                flash('Room not found',"error")
                return redirect(url_for('details.search'))
            if request.method=='POST':
                name, phone, email, guests, rooms, requests = FormController.get_make_reservation_information(user)
                return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=room_availability.get_duration(), startdate=startdate, enddate=enddate,
                                    name=name, phone=phone,email=email,guests=guests,rooms=rooms,requests=requests)
            
            return render_template('reserve.html', user=user, room=room, YesNo=YesNo, rid=rid, location_type=location_type, duration=room_availability.get_duration(), startdate=startdate, enddate=enddate)

    def search(self):
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
            starting, ending, result = search_controller.main_search(location=location,start=start,end=end)
            if(not result):
                flash('Please enter a valid start and end date',"error")
                return redirect(url_for('details.search', startdate=starting, enddate=ending))
            if starting >= ending:
                flash('Please select a valid range.', 'error')
                return redirect(url_for('details.search'))
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

