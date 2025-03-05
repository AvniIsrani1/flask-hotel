from flask import Flask, render_template
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# def connecting():
#     connection = None
#     try:
#         # Connecting to MySQL database 
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",  
#             password="admin",  
#             database="testdb"  
#         )
#         if connection.is_connected():
#                 return connection
#     except Error as e:
#         print(f"Error: {e}")
#     return None

#initalize tables in database
# def run_sql_script():
#     connection = connecting()
#     if connection is None:
#         print("Not able to connect. Exiting...")
#         return
#     try:
#         cursor = connection.cursor()
#         print("Connection established")
#         with open('./sql/initial.sql','r') as file:
#             sql_file = file.read()
#         lines = sql_file.split(';')
#         for line in lines:
#             if line.strip():
#                 cursor.execute(line.strip())
#         connection.commit()
#         print("Done initializing tables")

#     except Error as e:
#         print(f"Error executing SQL script: {e}")
#     finally:
#         connection.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route("/signup")
def sign_up():
    return render_template('signup.html')

@app.route("/login")
def log_in():
    return render_template('login.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/request-services")
def request_services():
    return render_template('request_services.html')

@app.route("/bookings")
def bookings():
    return render_template('bookings.html')

@app.route("/search")
def search():
    return render_template('search.html')

@app.route("/faq")
def faq():
    return render_template('faq.html')


if __name__ == "__main__":
    # run_sql_script()
    app.run(debug=True)

