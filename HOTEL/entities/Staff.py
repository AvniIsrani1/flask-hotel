from .User import User
from ..db import db
from sqlalchemy import DateTime
from .Enums import Position


class Staff(User):
    """
    A table for storing staff information. 

    Inherits from the users table. 

    Note:
        Author: Avni Israni
        Documentation: Avni Israni
        Created: April 28, 2025
        Modified: April 28, 2025
    """
    position = db.Column(db.Enum(Position))
    salary = db.Column(db.Integer())
    supervisor_id = db.Column(db.Integer())
    startdate = db.Column(DateTime)

    services = db.relationship('Service', backref='staff', lazy=True, cascade='all, delete-orphan')  

    __mapper_args__ = {
        'polymorphic_identity': 'staff'
    }
