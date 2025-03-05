from flask import render_template, Flask
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__,
            static_folder='static',     # Define the static folder (default is 'static')
            template_folder='templates')
app.secret_key = 'GITGOOD_12345'  # This key keeps your session data safe.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://hotel_user:sairamji080369@hotel-db-instance.cvwasiw2g3h6.us-west-1.rds.amazonaws.com:3306/hotel_db'
# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

# Define the User model/table
class User(db.Model):
    __tablename__ = 'users'  # Name of the table in the database
    id = db.Column(db.Integer, primary_key=True)  # Unique id for each user
    name = db.Column(db.String(150), nullable=False)  # User's name
    email = db.Column(db.String(150), unique=True, nullable=False)  # User's email (must be unique)
    password = db.Column(db.String(255), nullable=False)  # Hashed password

# Create all database tables (if they don't exist already)
with app.app_context():
    db.create_all()

# ----- Routes -----

# Home page route
@app.route("/")
def home():
    return render_template("home.html")

# Sign Up route: Display form on GET, process form on POST
@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("sign_up"))
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please use a different email or login.", "error")
            return redirect(url_for("sign_up"))
        
        # Hash the password before storing for security
        hashed_pw = generate_password_hash(password)
        
        # Create a new user instance
        new_user = User(name=name, email=email, password=hashed_pw)
        
        try:
            # Save the new user to the database
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("log_in"))
        except Exception as e:
            # Roll back the session if there is an error
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "error")
            return redirect(url_for("sign_up"))
    
    return render_template("signup.html")

# Login route: Display form on GET, process form on POST
@app.route("/login", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and if the password is correct
        if user and check_password_hash(user.password, password):
            # Save user's id and name in session so we know they are logged in
            session["user_id"] = user.id
            session["user_name"] = user.name
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for("log_in"))
    
    return render_template("login.html")

# Logout route: Clear the session and log the user out
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

# Profile route: Only accessible if the user is logged in
@app.route("/profile")
def profile():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    
    # Retrieve the logged-in user's information from the database
    user = User.query.get(session["user_id"])
    return render_template("profile.html", user=user)

@app.route("/my-bookings")
def my_bookings():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    return render_template('bookings.html')

@app.route("/request-services")
def request_services():
    if "user_id" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("log_in"))
    return render_template('request_services.html')

@app.route("/bookings")
def bookings():
    return render_template('bookings.html')

@app.route("/search")
def search():
    return render_template('search.html')

@app.route("/terms")
def terms():
    return render_template('terms.html')


if __name__ == "__main__":
    app.run(debug=True)