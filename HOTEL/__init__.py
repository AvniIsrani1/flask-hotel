from flask import render_template, Flask

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/signup")
def sign_up():
    return render_template('signup.html')

@app.route("/login")
def log_in():
    return render_template('login.html')

@app.route("/request-services")
def request_services():
    return render_template('request_services.html')