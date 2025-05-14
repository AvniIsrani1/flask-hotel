from flask_admin.contrib.sqla import ModelView
from flask import session, redirect, url_for, flash

class AdminRoutes(ModelView):
    """
    Protect Admin routes by overriding Flask ModelView access control methods. 

    Note:
        Author: Avni Israni
        Documentation: Avni Israni
        Created: May 14, 2025
        Modified: May 14, 2025
    """
    def is_accessible(self):
        """
        Check if the current user is an admin and provide access to admin views if so. 

        Parameters:
            None

        Returns:
            bool: True is user is an admin, else False
        """
        if "user_id" in session:
            from ..entities import Staff, Position
            staff = Staff.get_user(session["user_id"])
            return staff and staff.position == Position.ADMIN
        return False
    
    def inaccessible_callback(self, name, **kwargs):
        """
        Redirect to home page if user is not allowed to view admin routes. 

        Parameters:
            name (str): The name of the view that was accessed.
            **kwargs (dict): Other keyword arguments related to the request.

        Returns:
            Template: Redirect endpoint.
        """
        return redirect(url_for("info.home"))
    
