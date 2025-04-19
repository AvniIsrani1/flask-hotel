from .routes import bp_profile, bp_reserve, bp_request_services, bp_search, bp_staff, booking_routes, bp_auth, payment_routes, chat_routes

def register_blueprints(app, email_controller):
    app.register_blueprint(bp_profile)
    bp_bookings = booking_routes(email_controller)
    app.register_blueprint(bp_bookings)
    app.register_blueprint(bp_reserve)
    app.register_blueprint(bp_request_services)
    app.register_blueprint(bp_search)
    app.register_blueprint(bp_staff)
    app.register_blueprint(bp_auth)
    bp_payment = payment_routes(email_controller)
    app.register_blueprint(bp_payment)
    bp_chat = chat_routes()
    app.register_blueprint(bp_chat)