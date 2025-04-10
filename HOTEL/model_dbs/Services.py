from ..db import db
from sqlalchemy import DateTime, distinct, Computed
from datetime import datetime
from .Enums import YesNo, Assistance, SType, Status
from ..model_objects import Service


class Services(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bid = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False) 
    issued = db.Column(DateTime, nullable=False)
    modified = db.Column(DateTime)
    stype = db.Column(db.Enum(SType), nullable=False)
    robes = db.Column(db.Integer)
    btowels = db.Column(db.Integer)
    htowels = db.Column(db.Integer)
    soap = db.Column(db.Integer)
    shampoo = db.Column(db.Integer)
    conditioner = db.Column(db.Integer)
    wash = db.Column(db.Integer)
    lotion = db.Column(db.Integer)
    hdryer = db.Column(db.Integer)
    pillows = db.Column(db.Integer)
    blankets = db.Column(db.Integer)
    sheets = db.Column(db.Integer)
    housedatetime = db.Column(DateTime)
    trash = db.Column(db.Enum(YesNo)) 
    calldatetime = db.Column(DateTime)
    recurrent = db.Column(db.Enum(YesNo)) 
    restaurant = db.Column(db.String(200)) 
    assistance = db.Column(db.Enum(Assistance))
    other = db.Column(db.String(300)) 
    status = db.Column(db.Enum(Status),default=Status.N)


    def create_service_object(self):
        from .Bookings import Bookings 
        validate_check_out = Bookings.query.get(self.bid).check_out
        return Service(id=self.id, bid=self.bid, issued=self.issued,modified=self.modified,stype=self.stype,
                       robes=self.robes,btowels=self.btowels,htowels=self.htowels,soap=self.soap,shampoo=self.shampoo,
                       conditioner=self.conditioner,wash=self.wash,lotion=self.lotion,hdryer=self.hdryer,
                       pillows=self.pillows,blankets=self.blankets,sheets=self.sheets,housedatetime=self.housedatetime,
                       trash=self.trash,calldatetime=self.calldatetime,recurrent=self.recurrent,
                       restaurant=self.restaurant,assistance=self.assistance,other=self.other,
                       status=self.status.value, validate_check_out=validate_check_out
        )
    
    #can add multiple db rows at once (services is a list)
    @classmethod
    def create_services_db(cls, services):
        service_rows = []
        for service in services:
            service_rows.append(
                cls(
                    bid=service.bid,issued=service.issued,modified=service.modified,stype=SType(service.stype), 
                    robes=service.robes,btowels=service.btowels,htowels=service.htowels,
                    soap=service.soap,shampoo=service.shampoo,conditioner=service.conditioner,wash=service.wash,
                    lotion=service.lotion,hdryer=service.hdryer,pillows=service.pillows,
                    blankets=service.blankets,sheets=service.sheets,
                    housedatetime=service.housedatetime,
                    calldatetime=service.calldatetime,
                    restaurant=service.restaurant,
                    assistance=service.assistance,
                    other=service.other,
                    status=service.status
                )
            )
        return service_rows
    
    @classmethod
    def update_services_db(cls,service):
        model=cls.query.get(service.id)
        if model:
            model.modified=service.modified
            return True
        return False