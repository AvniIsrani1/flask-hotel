import pytest
from unittest.mock import patch, MagicMock, mock_open
from io import BytesIO
from datetime import datetime, timedelta
from HOTEL.Services import ReceiptGenerator
from HOTEL.entities import Booking, Room, Hotel, YesNo, RoomType, Availability

class TestReceiptGenerator:
    
    @pytest.fixture
    def mock_booking(self):
        """Create a mock booking object with all necessary attributes and relationships."""
        # Create mock room
        mock_room = MagicMock(spec=Room)
        mock_room.rate = 150
        mock_room.number_beds = 2
        mock_room.room_type = RoomType.STRD
        mock_room.wheelchair_accessible = YesNo.N
        mock_room.smoking = YesNo.N
        
        # Create mock hotel
        mock_hotel = MagicMock(spec=Hotel)
        mock_hotel.location = "Malibu"
        mock_hotel.address = "1234 Sunset Blvd, Malibu, CA 90265"
        
        # Link mock room to mock hotel
        mock_room.hotels = mock_hotel
        
        # Create mock booking
        mock_booking = MagicMock(spec=Booking)
        mock_booking.id = 12345
        mock_booking.name = "John Doe"
        mock_booking.email = "john.doe@example.com"
        mock_booking.phone = "555-123-4567"
        mock_booking.check_in = datetime.now()
        mock_booking.check_out = datetime.now() + timedelta(days=3)
        mock_booking.num_guests = 2
        
        # Link mock room to mock booking
        mock_booking.rooms = mock_room
        
        return mock_booking
    
    def test_init(self):
        """Test that the ReceiptGenerator initializes correctly."""
        receipt_gen = ReceiptGenerator()
        assert hasattr(receipt_gen, 'receipt_dir')
        assert hasattr(receipt_gen, 'styles')
    
    def test_format_currency(self):
        """Test that currency formatting works correctly."""
        receipt_gen = ReceiptGenerator()
        assert receipt_gen._format_currency(100) == "$100.00"
        assert receipt_gen._format_currency(99.99) == "$99.99"
        assert receipt_gen._format_currency(0) == "$0.00"
    
    @patch('os.path.exists')
    @patch('reportlab.platypus.SimpleDocTemplate')
    def test_generate_receipt_to_file(self, mock_simple_doc, mock_path_exists, mock_booking):
        """Test generating a receipt to a file."""
        mock_path_exists.return_value = True
        receipt_gen = ReceiptGenerator()
        
        # Call the method
        result = receipt_gen.generate_receipt(
            booking=mock_booking,
            room_rate=150,
            total_room_charges=450,
            resort_fee=30,
            tax_amount=67.5,
            total_amount=547.5,
            save_path="/fake/path/receipt.pdf"
        )
        
        # Check that SimpleDocTemplate was called
        mock_simple_doc.assert_called_once()
        assert result == "/fake/path/receipt.pdf"
    
    @patch('reportlab.platypus.SimpleDocTemplate')
    def test_generate_receipt_to_bytes(self, mock_simple_doc, mock_booking):
        """Test generating a receipt to a BytesIO object."""
        receipt_gen = ReceiptGenerator()
        
        # Call the method with return_bytes=True
        result = receipt_gen.generate_receipt(
            booking=mock_booking,
            room_rate=150,
            total_room_charges=450,
            resort_fee=30,
            tax_amount=67.5,
            total_amount=547.5,
            return_bytes=True
        )
        
        # Check that SimpleDocTemplate was called
        mock_simple_doc.assert_called_once()
        assert isinstance(result, BytesIO)
    
    @patch('os.path.exists')
    @patch('os.path.join')
    @patch('reportlab.platypus.SimpleDocTemplate')
    def test_generate_receipt_default_path(self, mock_simple_doc, mock_path_join, mock_path_exists, mock_booking):
        """Test generating a receipt with a default path."""
        mock_path_exists.return_value = True
        mock_path_join.return_value = "/default/path/receipt.pdf"
        receipt_gen = ReceiptGenerator()
        
        # Call the method without a save_path
        result = receipt_gen.generate_receipt(
            booking=mock_booking,
            room_rate=150,
            total_room_charges=450,
            resort_fee=30,
            tax_amount=67.5,
            total_amount=547.5
        )
        
        # Check that SimpleDocTemplate was called
        mock_simple_doc.assert_called_once()
        assert result == "/default/path/receipt.pdf"
    
    @patch('os.makedirs')
    def test_receipt_dir_creation(self, mock_makedirs):
        """Test that the receipt directory is created if it doesn't exist."""
        ReceiptGenerator()
        mock_makedirs.assert_called_once()