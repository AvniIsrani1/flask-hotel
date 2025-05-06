from .AIRoutes import AIRoutes
from .views import StaffRoutes, BookingRoutes, InfoRoutes, UserRoutes, DetailRoutes, PaymentRoutes
from .event_routes import get_events_blueprint

"""
Register the blueprints so each route is accessible. 

Note:
    Author: Avni Israni, Devansh Sharma
    Documentation: Avni Israni
    Created: March 2, 2025
    Modified: April 28, 2025
"""
def register_blueprints(app, email_controller):
    DetailRoutes(app)
    UserRoutes(app, email_controller)
    InfoRoutes(app)
    BookingRoutes(app, email_controller)
    StaffRoutes(app)
    PaymentRoutes(app, email_controller)
    AIRoutes(app)
    
    # Register events blueprint
    bp_events = get_events_blueprint()
    app.register_blueprint(bp_events)

