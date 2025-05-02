import pytest
from datetime import datetime, timedelta, time
from HOTEL.entities import Service, SType, YesNo, Assistance, Status

class TestService:
    def test_add_item(session):
        service = Service.add_item(bid=1, robes=2, shampoo=3)
        assert service.stype == SType.I
        assert service.bid == 1
        assert service.robes == 2
        assert service.shampoo == 3
        assert isinstance(service.issued, datetime)

    def test_add_housekeeping_valid(session):
        future = datetime.now() + timedelta(days=1)
        service = Service.add_housekeeping(bid=1, housetime=time(10, 0), validate_check_out=future)
        assert service is not None
        assert service.stype == SType.H
        assert service.housedatetime.date() <= future.date()

    def test_add_housekeeping_invalid_past_checkout(session):
        past = datetime.now() - timedelta(days=1)
        service = Service.add_housekeeping(bid=1, housetime=time(1, 0), validate_check_out=past)
        assert service is None

    def test_add_housekeeping_past_housetime(session):
        future = datetime.now() + timedelta(days=1)
        past = (datetime.now() -timedelta(hours=5)).time()
        service = Service.add_housekeeping(bid=1, housetime=past, validate_check_out=future)
        assert service is not None
        assert service.stype == SType.H
        assert service.housedatetime.date() == service.issued.date()

    def test_add_call_non_recurrent(session):
        future = datetime.now() + timedelta(days=1)
        calls = Service.add_call(bid=1, calltime=time(7, 0), recurrent=False, validate_check_out=future)
        assert len(calls) == 1
        assert calls[0].stype == SType.C

    def test_add_call_non_recurrent_past_calldatetime(session):
        expected = datetime.now() - timedelta(hours=3) + timedelta(days=1)
        past = (datetime.now() - timedelta(hours=3)).time()
        future = datetime.now() + timedelta(days=1)
        calls = Service.add_call(bid=1, calltime=past, recurrent=False, validate_check_out=future)
        assert len(calls) == 1
        assert calls[0].stype == SType.C
        assert calls[0].calldatetime == expected

    def test_add_call_recurrent(session):
        start = datetime.now()
        end = start + timedelta(days=2)
        calls = Service.add_call(bid=1, calltime=time(6, 30), recurrent=True, validate_check_out=end)
        assert len(calls) in [2, 3]  
        for call in calls:
            assert call.stype == SType.C

    def test_add_trash(session):
        service = Service.add_trash(bid=1)
        assert service.stype == SType.T
        assert service.trash == YesNo.Y

    def test_add_dining(session):
        service = Service.add_dining(bid=1, restaurant="Restaurant by the Sea")
        assert service.stype == SType.D
        assert service.restaurant == "Restaurant by the Sea"

    def test_add_assistance(session):
        service = Service.add_assistance(bid=1, assistance=Assistance.B)
        assert service.stype == SType.A
        assert service.assistance == Assistance.B

    def test_add_other(session):
        service = Service.add_other(bid=1, other="Fix AC")
        assert service.stype == SType.O
        assert service.other == "Fix AC"

    def test_update_status_valid(session):
        service = Service.add_trash(bid=1)
        updated = service.update_status(Status.C)
        assert updated is True
        assert service.status == Status.C
        assert isinstance(service.modified, datetime)

    def test_update_status_invalid(session):
        service = Service.add_trash(bid=1)
        updated = service.update_status("invalid")
        assert updated is False