from flask import Blueprint, request, render_template, flash, redirect, session, url_for
from ..entities import User,  YesNo
from ..controllers import FormController
from ..db import db
class UserRoutes:
    """
    Create user-information-related routes and register them to a blueprint.
    
    Note: 
        Author: Devansh Sharma, Avni Israni
        Created: February 18, 2025
        Modified: April 17, 2025
    """

    def __init__(self, app, email_controller):
        """
        Create authentication- and user-related routes and register them to a blueprint.
        
        Parameters:
            app (Flask): The Flask app instance. 
            email_controller (EmailController): The email controller for sending notifications.
            
        Returns:
            None
        """
        self.bp = Blueprint('userinfo', __name__)
        self.email_controller = email_controller
        self.setup_routes()
        app.register_blueprint(self.bp)

    def setup_routes(self):
        """
        Map the user-related HTTP routes to their respective handler functions.

        Parameters:
            None

        Returns:
            None 
        """
        self.bp.route('/signup', methods=["GET", "POST"])(self.sign_up)
        self.bp.route('/login', methods=["GET", "POST"])(self.login)
        self.bp.route('/logout')(self.logout)
        self.bp.route('/profile', methods=["GET", "POST"])(self.profile)

    def sign_up(self):
        """
        Handle user sign-up requests.
        
        GET: Display the sign-up form.
        POST: Process the sign-up form submission.
        
        Returns:
            Template: The sign-up form or a redirect to the login page on success.
        """
        if request.method == "POST":
            # Get form data
            name, email, password, confirm_password = FormController.get_signup_information()
            
            # Check if passwords match
            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return redirect(url_for("userinfo.sign_up"))
            
            # Check if email already exists
            if not User.unique_email(email):
                flash("Email already registered. Please use a different email or login.", "error")
                return redirect(url_for("userinfo.sign_up"))
            
            # Create a new user
            user = User.create_initial_user(name, email, password)
            
            try:
                # Save the new user to the database
                db.session.add(user)
                db.session.commit()
                flash("Account created successfully! Please log in.", "success")
                
                # If you have email functionality, you might want to send a welcome email here
                self.email_controller.send_welcome_email(user=user)
                
                return redirect(url_for("userinfo.login"))
            except Exception as e:
                # Roll back the session if there is an error
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "error")
                return redirect(url_for("userinfo.sign_up"))
        
        return render_template("signup.html")

    def login(self):
        """
        Handle user login requests.
        
        GET: Display the login form.
        POST: Process the login form submission.
        
        Returns:
            Template: The login form or a redirect to the home page on success.
        """
        if request.method == "POST":
            email, password = FormController.get_login_information()
            
            # Find user by email
            user = User.get_user_by_email(email)

            # Check if user exists and if the password is correct
            if user and user.verify_password(password):
                # Save user's id and name in session so we know they are logged in
                session["user_id"] = user.id
                session["user_name"] = user.name
                is_staff = user.type == 'staff'
                session["staff"] = is_staff
                session["staff_position"] = user.position.label if is_staff and user.position else ''

                if user.first_login == YesNo.Y:
                    return redirect(url_for('userinfo.profile'))
                else:
                    flash("Logged in successfully!", "success")
                    return redirect(url_for("info.home"))
            else:
                flash("Invalid email or password.", "error")
                return redirect(url_for("userinfo.login"))
        
        return render_template("login.html")

    def logout(self):
        """
        Handle user logout requests by clearing the session.
        
        Returns:
            Redirect: Redirect to the home page.

        Note: 
            Author: Devansh Sharma
            Created: February 16, 2025
            Modified: February 18, 2025
        """
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("info.home"))
        
    def profile(self):
        """
        Handle user profile viewing and updates.
        
        GET: Display the user profile page.
        POST: Process profile updates based on the form type submitted.
        
        Returns:
            Template: The profile template with user data.
            Redirect: Redirect to login page if not logged in.

        Note: 
            Author: Avni Israni
            Created: February 16, 2025
            Modified: April 17, 2025
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("userinfo.login"))
        
        user = User.get_user(session["user_id"])
        if not user:
            flash('Account not found','error')
            session.clear()
            return redirect(url_for("userinfo.login"))
        if user.first_login is YesNo.Y:
            flash("Please update your profile information!", "action")
        message = status = ''
        if request.method == "POST":
            ptype = request.form.get('ptype')
            if ptype == 'profile':
                name, phone, address_line1, address_line2, city, state, zipcode = FormController.get_profile_update_information()
                user.update_profile(
                    name = name, phone = phone, address_line1 = address_line1, address_line2 = address_line2,
                    city = city, state = state, zipcode = zipcode
                )
                message = 'Profile has been updated!'
                status = 'success'
            elif ptype=='notifications':
                tremind, eremind = FormController.get_profile_notification_information()
                user.update_notifications(tremind,eremind)
                message = 'Notification preferences have been updated!'
                status = 'success'
            elif ptype=='password_change':
                cur_password = request.form.get("cur_pass")
                if user.verify_password(cur_password):
                    new_password = request.form.get("new_pass")
                    user.change_password(new_password)
                    message = 'Password has been changed.'
                    status = 'success'
                else:
                    message = 'Unable to update password.'
                    status = 'error'
            elif ptype=='account_deletion': 
                db.session.delete(user)
                session.clear()
                db.session.commit()
                return render_template("home.html")
            try:
                db.session.commit()
                flash(message, status)
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}. Please try again later.", "error")
            finally:
                return redirect(url_for("userinfo.profile"))
        return render_template("profile.html", user=user, YesNo = YesNo)