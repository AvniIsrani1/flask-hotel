from flask import Blueprint, request, render_template, flash, redirect, session, url_for
from sqlalchemy import distinct
from ..entities import Hotel, FAQ
from ..db import db
from datetime import datetime 

class InfoRoutes:
    """
    Class containing information-related (generally static) routes. 

    Note:
        Author: Devansh Sharma, Andrew Ponce, Elijah Cortez, Avni Israni
        Documentation: Devansh Sharma, Andrew Ponce, Elijah Cortez, Avni Israni
        Created: February 21, 2025
        Modified: May 1, 2025
    """
    def __init__(self, app):
        """
        Create information-related routes and register them to a blueprint.
        
        Parameters:
            app: The app instance to register the blueprints on.
            
        Returns:
            None

        Note: 
            Author: Avni Israni
            Created: May 1, 2025
            Modified: May 1, 2025
        """
        self.bp = Blueprint('info', __name__)
        self.setup_routes()
        app.register_blueprint(self.bp)

    def setup_routes(self):
        """
        Map the info-related HTTP routes to their respective handler functions.

        Parameters:
            None

        Returns:
            None 
        
        Note:
            Author: Avni Israni
            Modified: May 10, 2025
        """
        self.bp.route('/')(self.home)
        self.bp.route('/terms')(self.terms)
        self.bp.route('/events')(self.events)
        self.bp.route('/menu')(self.menu)
        self.bp.route('/about')(self.about)
        self.bp.route('/amenities')(self.amenities)
        self.bp.route('/faq')(self.faq)

    def home(self):
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

    def terms(self):
        """
        Render the terms and conditions page.
        
        Returns:
            Template: The terms page template.

        Note:
            Author: Devansh Sharma
            Modified: April 17, 2025
        """
        return render_template('terms.html')

    def events(self):
        """
        Render the events page.
        
        Returns:
            Template: The events page template.

        Note:
            Author: Elijah Cortez
            Modified: April 17, 2025
        """
        return render_template('events.html')

    def menu(self):
        """
        Render the restaurant menu page.
        
        Returns:
            Template: The menu page template.

        Note:
            Author: Andrew Ponce
            Modified: April 17, 2025
        """
        return render_template('menus2.html')

    def about(self):
        """
        Render the about page.
        
        Returns:
            Template: The about page template.

        Note:
            Author: Eiji Cortez
            Modified: April 17, 2025
        """
        return render_template('about.html')

    def amenities(self):
        """
        Render the amenities page.
        
        Returns:
            Template: The amenities page template.

        Note:
            Author: Eiji Cortez
            Modified: April 29, 2025
        """
        return render_template('amenities.html')

    def faq(self):
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
