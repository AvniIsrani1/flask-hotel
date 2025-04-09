from datetime import datetime, timedelta

class Service: #what are some things I do to a single Service object?
    def __init__(self,bid,id=None,issued=None,modified=None,stype=None,robes=0,btowels=0,htowels=0,soap=0,shampoo=0,conditioner=0,wash=0,lotion=0,hdryer=0,pillows=0,
                 blankets=0,sheets=0,housedatetime=None,trash=None,calldatetime=None,recurrent=None,restaurant=None,
                 assistance=None,other=None,status=None,validate_checkout=None):
        self.id=id 
        self.bid=bid
        self.issued=issued
        self.modified=modified
        self.stype=stype
        self.robes=robes
        self.btowels=btowels
        self.htowels=htowels
        self.soap=soap
        self.shampoo=shampoo
        self.conditioner=conditioner
        self.wash=wash
        self.lotion=lotion
        self.hdryer=hdryer
        self.pillows=pillows
        self.blankets=blankets
        self.sheets=sheets
        self.housedatetime=housedatetime
        self.trash=trash
        self.calldatetime=calldatetime
        self.recurrent=recurrent
        self.restaurant=restaurant
        self.assistance=assistance
        self.other = other
        self.status = status #might need to change this to (status or Status.N) but need to check for internal loop
        self.validate_checkout=validate_checkout #not practically used by db viewers, just used for 2 methods below since they are time-sensitive

    @classmethod
    def add_item(cls, bid,robes=0,btowels=0,htowels=0,soap=0,shampoo=0,conditioner=0,wash=0,lotion=0,hdryer=0,pillows=0,blankets=0,sheets=0):
        today = datetime.now()
        return cls(
            bid=bid,
            issued=today,modified=today,
            stype = 'Items',
            robes=robes,btowels=btowels,htowels=htowels,soap=soap,shampoo=shampoo,conditioner=conditioner,wash=wash,lotion=lotion,
            hdryer=hdryer,pillows=pillows,blankets=blankets,sheets=sheets
        )
    
    @classmethod
    def add_housekeeping(cls,bid,housetime,validate_check_out):
        today = datetime.now()
        housedatetime = datetime.combine(today.date(), housetime)
        if housedatetime < today:
            housedatetime = today
        if housedatetime <= validate_check_out: #this probably does not work, this method probably needs to be self instead!!!
            return cls(id=id,bid=bid,issued=today,stype='Housekeeping',housedatetime=housedatetime)
    
    @classmethod
    def add_call(cls, bid, calltime, recurrent, validate_check_out): #when calltime is recieved from form, it is of type time (not datetime)
        today = datetime.now()
        calls = []
        calldatetime = datetime.combine(today.date(), calltime)
        if calldatetime < today:
            calldatetime = calldatetime + timedelta(days=1)
        if calldatetime <= validate_check_out: #probably does not work (likely need self instead of cls for validate_check_out)
            if recurrent:
                while(calldatetime <= validate_check_out):
                    call = cls(bid=bid,issued=today,stype='Call',calldatetime=calldatetime)
                    calls.append(call)
                    calldatetime = calldatetime + timedelta(days=1)
            else:
                call = cls(bid=bid,issued=today,stype='Call',calldatetime=calldatetime)
                calls.append(call)
            return calls #calls is a list of Call objects!!
        
    @classmethod
    def add_trash(cls,bid):
        return cls(bid=bid,issued=datetime.now(),stype='Trash',trash=True)

    @classmethod
    def add_dining(cls,bid, restaurant):
        return cls(bid=bid,issued=datetime.now(),stype='Dining',restaurant=restaurant)
    
    @classmethod
    def add_assistance(cls,bid, assistance):
        return cls(bid=bid,issued=datetime.now(),stype='Assistance',assistance=assistance)

    @classmethod
    def add_other(cls,bid, other):
        return cls(bid=bid,issued=datetime.now(),stype='Other',other=other)

    def update_status(self, new_status):
        from ..model_dbs.Enums import Status
        self.modified = datetime.now()
        if isinstance(new_status,Status):
            self.status = new_status
            return True
        return False