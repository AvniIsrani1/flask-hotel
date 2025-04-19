from .routes import bp_profile, bp_reserve, bp_request_services, bp_search, bp_staff, bp_info, booking_routes, auth_routes, payment_routes, chat_routes

"""
Register the blueprints so each route is accessible. 

Note:
    Author: Avni Israni, Devansh Sharma
    Documentation: Avni Israni
    Created: March 2, 2025
    Modified: April 17, 2025
"""
def register_blueprints(app, email_controller):
    app.register_blueprint(bp_profile)

    bp_bookings = booking_routes(email_controller)
    app.register_blueprint(bp_bookings)

    app.register_blueprint(bp_reserve)
    app.register_blueprint(bp_request_services)
    app.register_blueprint(bp_search)
    app.register_blueprint(bp_staff)

    bp_auth = auth_routes(email_controller)
    app.register_blueprint(bp_auth)

    bp_payment = payment_routes(email_controller)
    app.register_blueprint(bp_payment)
    bp_chat = chat_routes()
    app.register_blueprint(bp_chat)

    app.register_blueprint(bp_info)
