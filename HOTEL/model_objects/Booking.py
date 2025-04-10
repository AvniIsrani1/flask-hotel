from datetime import datetime, timedelta


class Booking:
    def __init__(self, uid, rid, check_in, check_out, fees, name, email, phone, id=None,num_guests=1, cancel_date=None, refund_type=None, special_requests=None, services=None):
        self.id=id
        self.uid = uid
        self.rid = rid
        self.check_in = check_in 
        self.check_out = check_out 
        self.fees = fees 
        self.cancel_date = cancel_date 
        self.refund_type = refund_type
        self.special_requests = special_requests 
        self.name = name 
        self.email = email 
        self.phone = phone 
        self.num_guests = num_guests 
        self.services = services or []

    def update_booking(self, special_requests, name, email, phone, num_guests):
        self.special_requests = special_requests
        self.name = name
        self.email = email
        self.phone = phone
        self.num_guests=num_guests

    def full_refund(self):
        today = datetime.now()
        if (self.check_in - today).days >=2:
            return True
        return False
    
    def cancel(self):
        today = datetime.now()
        self.refund_type = self.full_refund()
        self.cancel_date = today
        
    
    def to_dict(self):
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'rid': self.rid,
            'guest_id': self.guest_id,
            'check_in': self.check_in.strftime("%B %d, %Y %H:%M") if self.check_in else None,
            'check_out': self.check_out.strftime("%B %d, %Y %H:%M") if self.check_out else None
        }
