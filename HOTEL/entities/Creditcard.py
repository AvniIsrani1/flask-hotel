from datetime import datetime

class Creditcard:
    """
    Credit card validation class implementing the Luhn algorithm.
    
    This class provides methods to validate credit card numbers,
    expiration dates, and CVV codes.
    """
    
    def __init__(self, credit_card_number, exp_date, cvv):
        """
        Initialize a credit card validation object.
        
        Args:
            credit_card_number (str): The credit card number.
            exp_date (str): The expiration date in MM/YY format.
            cvv (str): The CVV code.
        """
        self.credit_card_number = credit_card_number.replace('-', '').replace(' ', '')

        if "/" not in exp_date and len(exp_date) == 4:
            exp_date = exp_date[:2] + "/" + exp_date[2:]
        self.exp_date = exp_date
        
        self.cvv = cvv
        
    def validate_CC(self):
        """
        Validate credit card number using the Luhn algorithm.
        
        Returns:
            bool: True if the card number is valid, False otherwise.
        """
        # First check if the card number has valid digits
        if not self.credit_card_number.isdigit():
            return False
            
        sum_odd_digits = 0
        sum_even_digits = 0
        total = 0
        
        reverse_credit_card_number = self.credit_card_number[::-1]

        for x in reverse_credit_card_number[::2]:
            sum_odd_digits += int(x)

        for x in reverse_credit_card_number[1::2]:
            x = int(x) * 2 

            if x >= 10:
                sum_even_digits += (1 + (x % 10))
            else:
                sum_even_digits += x
            
        total = sum_odd_digits + sum_even_digits
        return total % 10 == 0
    
    def validate_exp_date(self):
        """
        Validate the expiration date.
        
        Returns:
            bool: True if the expiration date is valid, False otherwise.
        """
        try:
            exp_month, exp_year = map(int, self.exp_date.split('/'))
            exp_year += (2000 if exp_year < 100 else 0)

            now = datetime.now()

            return exp_year > now.year or (exp_year == now.year and exp_month >= now.month)
        
        except Exception:
            return False
        
    def validate_cvv(self):
        """
        Validate the CVV code.
        
        Returns:
            bool: True if the CVV is valid, False otherwise.
        """
        if self.credit_card_number and self.credit_card_number[0] == '3':
            return len(self.cvv) == 4 and self.cvv.isdigit()
        else:
            return len(self.cvv) == 3 and self.cvv.isdigit()   
        
    def is_valid(self):
        """
        Check if the credit card information is valid.
        
        Returns:
            bool: True if all validations pass, False otherwise.
        """
        return (self.validate_CC() and 
                self.validate_exp_date() and 
                self.validate_cvv())