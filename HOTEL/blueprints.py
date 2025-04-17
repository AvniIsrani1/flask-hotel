from .routes import bp_profile, bp_reserve, bp_request_services, bp_search, bp_staff, booking_routes

def register_blueprints(app, email_controller):
    app.register_blueprint(bp_profile)
    bp_bookings = booking_routes(email_controller)
    app.register_blueprint(bp_bookings)
    app.register_blueprint(bp_reserve)
    app.register_blueprint(bp_request_services)
    app.register_blueprint(bp_search)
    app.register_blueprint(bp_staff)