from flask import render_template
from flask_mail import Message
from ..entities import YesNo

class EmailController:
    """
    A class for managing email sending operations throughout the application.
    This controller handles the creation and delivery of various types of email notifications.

    Author: Avni Israni
    Documentation: Andrew Ponce
    Created: April 6, 2025
    Modified: April 17, 2025
    """

    __instance = None

    def __new__(cls, mail):
        if cls.__instance is None:
            cls.__instance = super(EmailController, cls).__new__(cls)
            cls.__instance.mail = mail
        return cls.__instance
    
    def __init__(self, mail):
        """
        Initialize the EmailController with a Flask-Mail instance.

        Parameters:
            mail: The mail object to use for sending emails.

        Returns:
            None
        """
        if not hasattr(self, 'mail'):
            self.mail = mail

    def send_email(self,subject, recipients, body, body_template, user=None, booking=None,YesNo=YesNo, attachment=None, attachment_type=None):
        """
        Send email using Flask-Mail instance.

        Parameters:
            subject (str): The subject line of the email.
            recipients (list): List of recipient emails.
            body (str): Text body of the email (used when body_template cannot be used).
            body_template (str): Path to the HTML template for the email content.
            user (User, optional): User object to pass to the template.
            booking (Booking): Booking object to pass to the template.
            YesNo (Enum, Optional): YesNo enum to pass to the template.
            attachment (str, optional): Path to the file to attach.
            attchment_type (str, optional): Type of file to attach.

        Returns:
            None
        """
        msg = Message(subject,
                    recipients=['ocean.vista.hotels@gmail.com'], #we are in sandbox mode right now (can only send to verified emails) (need to create a dns record first to move to prod mode)
                    body=body)
        try:
            formatting = render_template(body_template, user=user, booking=booking, YesNo=YesNo)
            msg.html = formatting
        except Exception as e:
            print(f"Unable to format email: {e}")
        if attachment:
            with open(attachment, 'rb') as f:
                content = f.read()
                name = attachment.split('/')[-1]
                if attachment_type=='pdf':
                    ft = 'application/pdf'
                elif attachment_type=='png':
                    ft = 'image/png'
                elif attachment_type=='jpg':
                    ft = 'image/jpeg'
                else:
                    ft = 'application/octet-stream'
                msg.attach(name,ft,content)
        try:
            self.mail.send(msg)
            print("Message sent successfully")
        except Exception as e:
            print(f"Not able to send message:{e}")
        
        return 'Email sent!'


    def send_welcome_email(self,user):
        """
        Send a welcome email to a new user.

        Parameters:
            user (User): The new user who just signed up.

        Returns:
            str: A message indicating the email was sent.
        """
        return self.send_email(subject='Welcome to Ocean Vista',recipients=[user.email], 
                               body="Thank you for creating your Ocean Vista account!",
                               body_template='emails/account_created.html',user=user, YesNo=YesNo)


    def send_booking_created(self,user,bookings,YesNo):
        """
        Send a booking confirmation email when a new booking is created.
    
        Parameters:
            user (User): The user who created the booking.
            bookings (list): The list of booking objects.
            YesNo (enum): The YesNo enum to use in the template.
    
        Returns:
            str: A message indicating the email was sent.
        """
        return self.send_email(subject='Ocean Vista Booking Created!',recipients=[user.email], body="Thank you for creating a new booking!",
                               body_template='emails/booking_created.html',user=user, booking=bookings, YesNo=YesNo)


    
    def send_booking_updated(self,user,booking,YesNo):
        """
        Send a notification email when a booking is updated.
    
        Parameters:
            user (User): The user whose booking was updated.
            booking (Booking): The updated booking object.
            YesNo (enum): The YesNo enum to use in the template.
    
        Returns:
            str: A message indicating the email was sent.
        """
        return self.send_email(subject=f'Ocean Vista Booking Updated - ID#{booking.id}!',recipients=[user.email], body="Your booking has been updated!",
                               body_template='emails/updated.html',user=user, booking=booking, YesNo=YesNo)


    
    def send_booking_canceled(self,user,booking,YesNo):
        """
        Send a notification email when a booking is canceled.
    
        Parameters:
            user (User): The user whose booking was canceled.
            booking (Booking): The canceled booking object.
            YesNo (enum): The YesNo enum to use in the template.
    
        Returns:
            str: A message indicating the email was sent.
        """
        return self.send_email(subject='Ocean Vista Booking Canceled!',recipients=[user.email], body="Your booking has been canceled!",
                               body_template='emails/canceled.html',user=user, booking=booking, YesNo=YesNo)

