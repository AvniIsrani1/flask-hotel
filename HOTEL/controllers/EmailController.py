from flask import render_template
from flask_mail import Message
from ..entities import YesNo

class EmailController:
    """
    A class for managing email sending operations throughout the application.
    This controller handles the creation and delivery of various types of email notifications.
    """
    
    def __init__(self,mail):
        self.mail=mail
    """
    Initialize an EmailController object with the mail service.
    Args:
        mail: The mail service to use for sending emails.
    Returns:
        None
    """

    

    def send_email(self,subject, recipients, body, body_template, user=None, booking=None,YesNo=YesNo, attachment=None, attachment_type=None):
    """
    Initialize an EmailController object with the mail service.
    Args:
        mail: The mail service to use for sending emails.
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
    Args:
        user (User): The user object containing email and other details.
    Returns:
        str: A message indicating the email was sent.
    """
        return self.send_email(subject='Welcome to Ocean Vista',recipients=[user.email], 
                               body="Thank you for creating your Ocean Vista account!",
                               body_template='emails/account_created.html',user=user, YesNo=YesNo)


    def send_booking_created(self,user,bookings,YesNo):
    """
    Send a booking confirmation email when a new booking is created.

    Args:
        user (User): The user who created the booking.
        bookings (Booking): The booking object containing reservation details.
        YesNo (enum): The YesNo enumeration to use in the template.

    Returns:
        str: A message indicating the email was sent.
    """
        return self.send_email(subject='Ocean Vista Booking Created!',recipients=[user.email], body="Thank you for creating a new booking!",
                               body_template='emails/booking_created.html',user=user, booking=bookings, YesNo=YesNo)


    
    def send_booking_updated(self,user,booking,YesNo):
    """
    Send a notification email when a booking is updated.

    Args:
        user (User): The user whose booking was updated.
        booking (Booking): The updated booking object.
        YesNo (enum): The YesNo enumeration to use in the template.

    Returns:
        str: A message indicating the email was sent.
    """
        return self.send_email(subject=f'Ocean Vista Booking Updated - {booking.id}!',recipients=[user.email], body="Your booking has been updated!",
                               body_template='emails/updated.html',user=user, booking=booking, YesNo=YesNo)


    
    def send_booking_canceled(self,user,booking,YesNo):
    """
    Send a notification email when a booking is canceled.

    Args:
        user (User): The user whose booking was canceled.
        booking (Booking): The canceled booking object.
        YesNo (enum): The YesNo enumeration to use in the template.

    Returns:
        str: A message indicating the email was sent.
    """
        return self.send_email(subject='Ocean Vista Booking Canceled!',recipients=[user.email], body="Your booking has been canceled!",
                               body_template='emails/canceled.html',user=user, booking=booking, YesNo=YesNo)

