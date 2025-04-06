import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from io import BytesIO

class ReceiptGenerator:
    def __init__(self):
        # Create a directory for receipts if it doesn't exist
        self.receipt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'receipts')
        os.makedirs(self.receipt_dir, exist_ok=True)
        
        # Set up styles
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Center', alignment=TA_CENTER))
        self.styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT))
        
    def _format_currency(self, amount):
        return f"${amount:.2f}"
        
    def generate_receipt(self, booking, room_rate, total_room_charges, resort_fee, tax_amount, total_amount, save_path=None, return_bytes=False):
        room = booking.room
        hotel = room.hotel
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"Receipt_{booking.id}_{timestamp}.pdf"
        
        if save_path:
            pdf_path = save_path
        else:
            pdf_path = os.path.join(self.receipt_dir, filename)
            
        if return_bytes:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
        else:
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            
        elements = []
        
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'pdf_logo.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
            elements.append(logo)
            
        elements.append(Paragraph("Ocean Vista Hotel", self.styles['Title']))
        elements.append(Paragraph(f"{hotel.location.value} Branch Location", self.styles['Normal']))
        elements.append(Paragraph(f"{hotel.address}", self.styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
        
        receipt_date = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph("Receipt Information", self.styles['Heading2']))
        elements.append(Paragraph(f"Receipt Number: R-{booking.id}-{booking.check_in.strftime('%Y%m%d')}", self.styles['Normal']))
        elements.append(Paragraph(f"Receipt Date: {receipt_date}", self.styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
        
        elements.append(Paragraph("Guest Information", self.styles['Heading2']))
        elements.append(Paragraph(f"Name: {booking.name}", self.styles['Normal']))
        elements.append(Paragraph(f"Email: {booking.email}", self.styles['Normal']))
        elements.append(Paragraph(f"Phone: {booking.phone}", self.styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
        
        elements.append(Paragraph("Reservation Details", self.styles['Heading2']))
        
        check_in_str = booking.check_in.strftime("%A, %B %d, %Y")
        check_out_str = booking.check_out.strftime("%A, %B %d, %Y")
        
        num_nights = (booking.check_out - booking.check_in).days
        if num_nights == 0:
            num_nights = 1
        
        elements.append(Paragraph(f"Check-In: {check_in_str}", self.styles['Normal']))
        elements.append(Paragraph(f"Check-Out: {check_out_str}", self.styles['Normal']))
        elements.append(Paragraph(f"Number of Nights: {num_nights}", self.styles['Normal']))
        
        room_type_str = f"{room.number_beds}-Bedroom {room.room_type.value}"
        if room.wheelchair_accessible.value == 'Y':
            room_type_str += " (Wheelchair Accessible)"
        if room.smoking.value == 'N':
            room_type_str += " | Non-Smoking"
            
        elements.append(Paragraph(f"Room Type: {room_type_str}", self.styles['Normal']))
        elements.append(Paragraph(f"Number of Guests: {booking.num_guests}", self.styles['Normal']))
        elements.append(Spacer(1, 0.25*inch))
        
        data = [
            ["Description", "Rate", "Amount"],
            [f"{room.number_beds}-Bedroom {room.room_type.value}", 
             self._format_currency(room_rate), 
             self._format_currency(total_room_charges)],
            ["Resort Fee", self._format_currency(30.00), self._format_currency(resort_fee)],
            ["Tax (15%)", "", self._format_currency(tax_amount)],
            ["Total", "", self._format_currency(total_amount)]
        ]
        
        table = Table(data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (2, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ]))
        
        elements.append(Paragraph("Charges", self.styles['Heading2']))
        elements.append(table)
        elements.append(Spacer(1, 0.25*inch))
        
        elements.append(Paragraph("Payment Information", self.styles['Heading2']))
        elements.append(Paragraph("Payment Method: Credit Card", self.styles['Normal']))
        elements.append(Paragraph("Payment Status: Paid", self.styles['Normal']))
        payment_date = booking.check_in.strftime("%B %d, %Y")
        elements.append(Paragraph(f"Payment Date: {payment_date}", self.styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        elements.append(Paragraph("Thank you for choosing Ocean Vista Hotels!", self.styles['Center']))
        elements.append(Paragraph("This receipt was generated electronically.", self.styles['Center']))
        
        doc.build(elements)
        
        if return_bytes:
            buffer.seek(0)
            return buffer
        
        return pdf_path