from flask import Flask
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from urllib.parse import quote
import boto3
from botocore.exceptions import ClientError
import json

from HOTEL.controllers import EmailController
from HOTEL.db import db

from flask_admin import Admin
from flask_apscheduler import APScheduler


mail = Mail()
scheduler = APScheduler()


class Factory:
    """
    A class responsible for the application setup (configuring the database, mail, and scheduling services,
    the routes, and adding sample data). 

    Note:
        Author: Avni Israni, Devansh Sharma
        Documentation: Devansh Sharma, Avni Israni
        Created: March 1, 2025
        Modified: May 7, 2025
    """

    def get_secrets(self, secret_name):
        """
        Retrieve secrets from AWS Secrets Manager.
        
        Parameters:
            secret_name (str): The name of the secret to retrieve.
            
        Returns:
            tuple: A tuple containing username and password.
            
        Raises:
            ClientError: If there is an error retrieving the secret.

        Note:
            Author: Avni Israni
            Documentation: Devansh Sharma
            Created: March 3, 2025
            Modified: April 17, 2025
        """
        client = boto3.client(service_name='secretsmanager', region_name='us-west-1')
        try:
            response = client.get_secret_value(SecretId=secret_name)
        except ClientError as e:
            raise e
        secret = json.loads(response['SecretString'])
        username = secret.get("username")
        pwd = secret.get("password")
        return username, pwd
    
    def register_blueprints(self, app, email_controller):
        """
        Register the blueprints so each route is accessible. 

        Note:
            Author: Avni Israni, Devansh Sharma
            Documentation: Avni Israni
            Created: March 2, 2025
            Modified: April 28, 2025
        """
        from HOTEL.views import StaffRoutes, BookingRoutes, InfoRoutes, UserRoutes, DetailRoutes, PaymentRoutes, EventRoutes
        from HOTEL.views.AIRoutes import AIRoutes
        DetailRoutes(app)
        UserRoutes(app, email_controller)
        InfoRoutes(app)
        BookingRoutes(app, email_controller)
        StaffRoutes(app)
        PaymentRoutes(app, email_controller)
        AIRoutes(app)
        EventRoutes(app)

    def create_app(self, test_config = None):
        """
        Configure and initialize the Flask application. 

        Parameters:
            test_config (dict, optional): A dictionary of configuration settings. 

        Returns:
            app (Flask): The Flask application instance. 

        Note:
            Author: Avni Israni, Devansh Sharma
            Documentation: Avni Israni
            Created: March 1, 2025
            Modified: May 7, 2025
        """
        app = Flask("HOTEL",
                    static_folder='static',
                    template_folder='templates')
        app.secret_key = 'GITGOOD_12345'

        if test_config:
            app.config.update(test_config)
        else:
            
            scheduler.init_app(app)
            def clean_service_tasks():
                with app.app_context():
                    from ..entities import Service
                    print("cleaning tasks...")
                    Service.clean_tasks()
                    print("done cleaning tasks...")
            scheduler.add_job(
                id='clean_service_tasks', 
                func=clean_service_tasks,
                trigger='interval', 
                hours=1
            )
            scheduler.start()

            rds_secret_name = "rds!db-d319020b-bb3f-4784-807c-6271ab3293b0"
            ses_secret_name = "oceanvista/gmail"

            rds_username, rds_pwd = self.get_secrets(rds_secret_name)
            rds_pwd = quote(rds_pwd)
            ses_username, ses_pwd = self.get_secrets(ses_secret_name)

            app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{rds_username}:{rds_pwd}@hotel-db-instance.cvwasiw2g3h6.us-west-1.rds.amazonaws.com:3306/hotel_db'

            app.config['MAIL_SERVER'] = 'smtp.gmail.com'
            app.config['MAIL_PORT'] = 587
            app.config['MAIL_USE_TLS'] = True
            app.config['MAIL_USE_SSL'] = False
            app.config['MAIL_USERNAME'] = ses_username
            app.config['MAIL_PASSWORD'] = ses_pwd
            app.config['MAIL_DEFAULT_SENDER'] = 'ocean.vista.hotels@gmail.com'

        db.init_app(app)
        mail.init_app(app)
        email_controller = EmailController(mail)
        self.register_blueprints(app, email_controller)

        admin = Admin(app, name="Admin", template_mode="bootstrap4")
        from HOTEL.entities import User, Staff, Booking, Hotel, Floor, Room, Service, FAQ
        from HOTEL.views import AdminRoutes

        with app.app_context():
            from ..entities import FAQ
            db.create_all()
            self.add_sample_data()
            if not FAQ.query.first():
                self.add_sample_faq()
            admin.add_views(
                AdminRoutes(User, db.session),
                AdminRoutes(Booking, db.session),
                AdminRoutes(Hotel, db.session),
                AdminRoutes(Floor, db.session), 
                AdminRoutes(Room, db.session),
                AdminRoutes(Service, db.session),
                AdminRoutes(FAQ, db.session)
            )

        return app

    def add_sample_data(self):
        """
        Add sample data to the database if tables are empty.
        Creates sample hotels, rooms, and users for testing.

        Note:
            Author: Avni Israni, Devansh Sharma
            Documentation: Devansh Sharma
            Created: March 1, 2025
            Modified: April 17, 2025
        """
        from HOTEL.entities import Hotel, Room, Staff, Locations, Position
        from HOTEL.db import db
        # Check if we have any rooms
        if not Room.query.first():
            print("Adding sample rooms")
            # First check if we have hotels
            if not Hotel.query.first():
                malibu_hotel = Hotel(location=Locations.MALIBU, address="1234 Sunset Blvd, Malibu, CA 90265")
                sm_hotel = Hotel(location=Locations.SM, address="5678 Ocean Drive, Santa Monica, CA 90401")
                db.session.add(malibu_hotel)
                db.session.add(sm_hotel)
                db.session.commit()

            # Get hotel IDs
            malibu_hotel = Hotel.get_hotels_by_location("Malibu")[0]
            sm_hotel = Hotel.get_hotels_by_location("Santa Monica")[0]
            
            with open('sample_layout.json', 'r') as f:
                add_room_params = json.load(f)
            malibu_hotel.add_layout(base_floor_number=1, number_floors=4, add_room_params=add_room_params)
            sm_hotel.add_layout(base_floor_number=1, number_floors=4, add_room_params=add_room_params)
            print("Sample rooms added")

            users = []
            avni = Staff(name="avni", email="avni.israni.292@my.csun.edu", password=generate_password_hash("avni"), position=Position.MANAGER)
            devansh = Staff(name="danny", email="devansh.sharma.574@my.csun.edu", password=generate_password_hash("1230"), position=Position.CONCIERGE, supervisor_id=1)
            elijah = Staff(name="elijah", email="elijah.cortez.213@my.csun.edu", password=generate_password_hash("elijah"), position=Position.MANAGER, supervisor_id=1)
            andrew = Staff(name="andrew", email="andrew.ponce.047@my.csun.edu", password=generate_password_hash("andrew"), position=Position.MAINTENANCE, supervisor_id=3)
            admin = Staff(name="admin", email="ocean.vista.hotels@gmail.com", password=generate_password_hash("admin"), position=Position.ADMIN)
            users.extend([avni, devansh, elijah, andrew, admin])
            db.session.add_all(users)
            db.session.commit()
            print('sample users added')

            print("sample bookings")

    def add_sample_faq(self):
        """
        Add sample FAQs to the database.
        
        Note:
            Author: Avni Israni
            Documentation: Avni Israni
            Created: March 10, 2025
            Modified: May 10, 2025
        """
        from HOTEL.entities import FAQ

        with open('sample_faqs.json', 'r') as f:
            sample_faqs = json.load(f)
        FAQ.add_faqs(sample_faqs)
