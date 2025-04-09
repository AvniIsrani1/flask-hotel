from datetime import datetime, timedelta

class Service:
    def __init__(self,id,bid,issued,modified,stype,robes=0,btowels=0,htowels=0,soap=0,shampoo=0,conditioner=0,wash=0,lotion=0,hdryer=0,pillows=0,
                 blankets=0,sheets=0,housedatetime=None,trash=None,calldatetime=None,recurrent=None,restaurant=None,
                 assistance=None,other=None,status=None):
        self.id = id 
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

    def update_status(self, new_status):
        from ..model_dbs.Enums import Status
        self.modified = datetime.now()
        if isinstance(new_status,Status):
            self.status = new_status
            return True
        return False