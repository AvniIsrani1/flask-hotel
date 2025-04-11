from werkzeug.security import generate_password_hash, check_password_hash

class User:

    def __init__(self, name, email, password, id=None, phone=None, address_line1=None, address_line2=None, city=None, state=None, zipcode=None, 
                 rewards=None, first_login=True, text_notifications=False, email_notifications=False, bookings=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.phone = phone
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.rewards = rewards
        self.first_login = first_login
        self.text_notifications = text_notifications
        self.email_notifications = email_notifications
        self.bookings = bookings or []

    @classmethod
    def create_initial_user(cls,name,email,password):
        return cls(name=name,email=email,password=generate_password_hash(password))

    def update_profile(self, name=None, phone=None, address_line1=None, address_line2=None, city=None, state=None, zipcode=None):
        self.name = name
        self.phone = phone
        self.address_line1 = address_line1
        self.address_line2 = address_line2
        self.city = city
        self.state = state
        self.zipcode = zipcode
        if self.name and self.phone: #what information do we most want from user??
            self.first_login = False

    def update_notifications(self, text_notifications, email_notifications):
        self.text_notifications = text_notifications
        self.email_notifications = email_notifications
    
    def verify_password(self, entered_password):
        return check_password_hash(self.password, entered_password)
    
    def change_password(self, new_password):
        self.password = generate_password_hash(new_password)

    # def add_booking(self, booking):
    #     self.bookings.append(booking)
    
    # def cancel_booking(self, booking): #booking is a Booking object
    #     self.bookings.remove(booking)

