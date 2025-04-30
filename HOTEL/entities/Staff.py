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


    @classmethod
    def get_staff(cls, id):
        """
        Retrieve a staff member by their unique ID.

        Parameters: 
            id (int): The unique ID of the staff member.

        Returns:
            Staff | None: The Staff object if found, else None.
        """
        return cls.query.filter(cls.id==id).first()
