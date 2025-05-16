from flask import Blueprint, g, request, render_template, flash, redirect, session, url_for
from ..entities import Hotel, Staff, Service, Status, Locations, SType
from ..services import ReportGenerator
from ..db import db
from datetime import datetime 
from sqlalchemy import distinct, or_
from ..common import Auth

class StaffRoutes:
    """
    Class containing staff-related routes. 

    Note: 
        Author: Avni Israni
        Created: February 18, 2025
        Modified: April 17, 2025
    """
    def __init__(self, app):
        """
        Create staff-related routes and register them to a blueprint.
    
        Parameters:
            app (Flask): The Flask app instance
        
        Returns:
            None
        """
        self.bp = Blueprint('staff', __name__)
        self.setup_routes()
        app.register_blueprint(self.bp)

    def setup_routes(self):
        """
        Map the staff-related HTTP routes to their respective handler functions.

        Parameters:
            None

        Returns:
            None 
        """
        self.bp.route('/tasks', methods=["GET", "POST"])(Auth.staff_login_required(self.tasks))
        self.bp.route('/reports', methods=["GET", "POST"])(Auth.staff_login_required(self.reports))
        self.bp.route('/staff-reports', methods=["GET", "POST"])(Auth.staff_login_required(self.staff_reports))

    def tasks(self):
        """
        Display all current service tasks for staff to manage.
        
        Retrieves all service requests from today onwards and displays them
        in chronological order, grouped by booking ID and service type.
        
        Returns:
            Template: The tasks template with all current service requests.
        """
        staff = g.staff
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
        current_tasks = Service.get_active_tasks()
        assignable_staff = staff.get_assignable_staff()
        print(assignable_staff)
        return render_template('tasks.html', current_tasks=current_tasks, assignable_staff=assignable_staff, Status=Status, SType=SType)


    def reports(self):
        """
        Display booking-related reports for the manager to view.
        
        Returns:
            Template: The reports template with all booking-related views.
        """
        staff = g.staff

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


    def staff_reports(self):
        """
        Display staff-related reports for the manager to view.
        
        Returns:
            Template: The staff-reports template with all staff-related views.
        """
        staff = g.staff
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
                    return render_template('reports_staff.html', locations=locations, staff_graph=staff_graph, startdate=None, enddate=None)
                staff_graph = ReportGenerator.get_staff_insights(location, startdate, enddate, assignable_staff)
                return render_template('reports_staff.html', locations=locations, staff_graph=staff_graph, startdate=None, enddate=None)
            except ValueError:
                flash("Invalid date format", "error")
                staff_graph = ReportGenerator.get_staff_insights(location, None, None, assignable_staff)
        else:
            staff_graph = ReportGenerator.get_staff_insights(location, None, None, assignable_staff)
        return render_template('reports_staff.html', locations=locations, staff_graph=staff_graph, startdate=startdate, enddate=enddate)

