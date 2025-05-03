import pytest 
from datetime import datetime
from HOTEL.entities import Creditcard


class TestCreditcard:
    
    def test_valid_credit_card(self):
        card = Creditcard("4111111111111111", "12/25", "123")
        assert card.validate_CC() is True
        assert card.validate_exp_date() is True
        assert card.validate_cvv() is True
        assert card.is_valid() is True
        
    def test_invalid_credit_card_number(self):
        card1 = Creditcard("1234567890123456", "12/25", "123")
        card2 = Creditcard("411111111111111", "12/25", "123")
        card3 = Creditcard("4111-1111-1111-1111", "12/25", "123")
        card4 = Creditcard("4111 1111 1111 1111", "12/25", "123")
        card5 = Creditcard("411111111111111a", "12/25", "123")
        
        assert card1.validate_CC() is False
        assert card2.validate_CC() is False
        assert card3.validate_CC() is True
        assert card4.validate_CC() is True
        assert card5.validate_CC() is False
        
    def test_expired_date(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        past_month = current_month - 1 if current_month > 1 else 12
        past_year = current_year if current_month > 1 else current_year - 1
        past_date = f"{past_month:02d}/{str(past_year)[2:]}"
        
        card = Creditcard("4111111111111111", past_date, "123")
        assert card.validate_exp_date() is False
        
    def test_future_date(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        future_date = f"{current_month:02d}/{str(current_year + 1)[2:]}"
        
        card = Creditcard("4111111111111111", future_date, "123")
        assert card.validate_exp_date() is True
        
    def test_current_month_date(self):
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_date = f"{current_month:02d}/{str(current_year)[2:]}"
        
        card = Creditcard("4111111111111111", current_date, "123")
        assert card.validate_exp_date() is True
        
    def test_invalid_date_format(self):
        card1 = Creditcard("4111111111111111", "1225", "123")
        card2 = Creditcard("4111111111111111", "12-25", "123")
        card3 = Creditcard("4111111111111111", "2512", "123")
        
        assert card1.validate_exp_date() is True
        assert card2.validate_exp_date() is False
        assert card3.validate_exp_date() is False
        
    def test_invalid_cvv(self):
        card1 = Creditcard("4111111111111111", "12/25", "12")
        card2 = Creditcard("4111111111111111", "12/25", "12345")
        card3 = Creditcard("4111111111111111", "12/25", "12a")
        
        assert card1.validate_cvv() is False
        assert card2.validate_cvv() is False
        assert card3.validate_cvv() is False
        
    def test_amex_cvv(self):
        amex_card = Creditcard("378282246310005", "12/25", "1234")
        assert amex_card.validate_cvv() is True
        
        amex_card_short = Creditcard("378282246310005", "12/25", "123")
        assert amex_card_short.validate_cvv() is False
        
        visa_card_long = Creditcard("4111111111111111", "12/25", "1234")
        assert visa_card_long.validate_cvv() is False
        
    def test_is_valid(self):
        valid_card = Creditcard("4111111111111111", "12/25", "123")
        invalid_number = Creditcard("1234567890123456", "12/25", "123")
        expired_date = Creditcard("4111111111111111", "01/20", "123")
        invalid_cvv = Creditcard("4111111111111111", "12/25", "12")
        
        assert valid_card.is_valid() is True
        assert invalid_number.is_valid() is False
        assert expired_date.is_valid() is False
        assert invalid_cvv.is_valid() is False
        
    def test_formatting_cleanup(self):
        card_with_spaces = Creditcard("4111 1111 1111 1111", "12/25", "123")
        card_with_dashes = Creditcard("4111-1111-1111-1111", "12/25", "123")
        
        assert card_with_spaces.credit_card_number == "4111111111111111"
        assert card_with_dashes.credit_card_number == "4111111111111111"
        
    def test_exp_date_formatting(self):
        card_no_slash = Creditcard("4111111111111111", "1225", "123")
        assert card_no_slash.exp_date == "12/25"
        
        card_long_year = Creditcard("4111111111111111", "12/2025", "123")
        assert card_long_year.exp_date == "12/2025"
        
    @pytest.mark.parametrize("card_number, exp_date, cvv, expected", [
        ("4111111111111111", "12/25", "123", True),
        ("5555555555554444", "12/25", "123", True),
        ("378282246310005", "12/25", "1234", True),
        ("6011111111111117", "12/25", "123", True),
        ("1234567890123456", "12/25", "123", False),
        ("4111111111111111", "01/20", "123", False),
        ("4111111111111111", "12/25", "12", False),
        ("378282246310005", "12/25", "123", False),
    ])
    def test_multiple_card_types(self, card_number, exp_date, cvv, expected):
        card = Creditcard(card_number, exp_date, cvv)
        assert card.is_valid() == expected