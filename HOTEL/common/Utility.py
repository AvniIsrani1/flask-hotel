from functools import wraps
from flask import flash, redirect, session, url_for, g

from ..entities import User, Staff

class Utility:
    """
    Utility class for system-wide methods. 

    Note:
        Author: Avni Israni, Devansh Sharma
        Documentation: Avni Israni
        Created: May 14, 2025
        Modified: May 14, 2025
    """
    @staticmethod
    def login_required(view):
        """
        Make sure that user is logged in and valid.

        Parameters:
            view (function): The view function to decorate.
        
        Returns:
            function: Wrapper function that allows original view if user is valid or redirects to login page.
        """
        @wraps(view)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "error")
                return redirect(url_for("userinfo.login"))
            user = User.query.get(session["user_id"])

            if not user:
                flash('Account not found','error')
                session.clear()
                return redirect(url_for("userinfo.login"))
            
            g.user = user
            return view(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def staff_login_required(view):
        """
        Make sure that user is logged in and is a staff member. 

        Parameters:
            None

        Returns:
            function: Wrapper function that allows original view if user is valid or redirects to login page.
        """
        @wraps(view)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "error")
                return redirect(url_for("userinfo.login"))
            staff = Staff.query.get(session["user_id"])

            if not staff:
                flash("You don't have permission to view this resource.", "error")
                session.clear()
                return redirect(url_for("userinfo.login"))
            
            g.staff = staff
            return view(*args, **kwargs)
        return wrapper

