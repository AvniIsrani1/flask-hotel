def register_blueprints(app):
    from .routes import bp_profile, bp_bookings, bp_reserve, bp_request_services, bp_search

    app.register_blueprint(bp_profile)
    app.register_blueprint(bp_bookings)
    app.register_blueprint(bp_reserve)
    app.register_blueprint(bp_request_services)
    app.register_blueprint(bp_search)