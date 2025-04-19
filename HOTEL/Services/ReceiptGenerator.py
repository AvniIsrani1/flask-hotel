import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

class ReceiptGenerator:
    """
    Generate PDF receipts for hotel bookings. 

    Note:
        Author: Devansh Sharma
        Documentation: Devansh Sharma
        Created: April 6, 2025
        Modified: April 17, 2025
    """
    
    def __init__(self):
        """
        Initialize the ReceiptGenerator with necessary directories and styling.
        
        Sets up the receipt directory, registers fonts, and creates style objects
        for consistent PDF formatting.
        """
        # Create a directory for receipts if it doesn't exist
        self.receipt_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'receipts')
        os.makedirs(self.receipt_dir, exist_ok=True)
        
        # Register fonts to match website styling
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'fonts')
        try:
            # Register custom fonts if available
            pdfmetrics.registerFont(TTFont('NotoSans', os.path.join(font_path, 'NotoSans-Regular.ttf')))
            pdfmetrics.registerFont(TTFont('NotoSans-Bold', os.path.join(font_path, 'NotoSans-Bold.ttf')))
        except:
            # Fallback if fonts aren't available
            pass
        
        # Set up styles
        self.styles = getSampleStyleSheet()
        
        # Create styles matching website
        self.styles.add(ParagraphStyle(
            name='Center', 
            alignment=TA_CENTER,
            fontName='NotoSans' if 'NotoSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
            fontSize=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader', 
            alignment=TA_LEFT,
            fontName='NotoSans-Bold' if 'NotoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold',
            fontSize=12,
            textColor=colors.HexColor('#002B5A'),
            spaceAfter=12,
            spaceBefore=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReceiptItem', 
            alignment=TA_LEFT,
            fontName='NotoSans' if 'NotoSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
            fontSize=10,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='ReceiptValue', 
            alignment=TA_RIGHT,
            fontName='NotoSans' if 'NotoSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica',
            fontSize=10
        ))
        
    def _format_currency(self, amount):
        """
        Format a number as USD currency.
        
        Args:
            amount (float): The amount to format.
            
        Returns:
            str: The formatted currency string.
        """
        return f"${amount:.2f}"
        
    def generate_receipt(self, booking, room_rate, total_room_charges, resort_fee, tax_amount, total_amount, save_path=None, return_bytes=False):
        """
        Generate a PDF receipt for a booking.
        
        Args:
            booking (Booking): The booking object containing reservation details.
            room_rate (float): The rate per night for the room.
            total_room_charges (float): The total charges for the room stay.
            resort_fee (float): The resort fee amount.
            tax_amount (float): The tax amount.
            total_amount (float): The total amount of the booking.
            save_path (str, optional): Custom path to save the receipt. Defaults to None.
            return_bytes (bool, optional): Whether to return the PDF as bytes. Defaults to False.
            
        Returns:
            str | BytesIO: The path to the saved PDF file or the PDF as a BytesIO object.
        """
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
            doc = SimpleDocTemplate(buffer, pagesize=letter, 
                                   topMargin=0.75*inch, 
                                   leftMargin=0.75*inch, 
                                   rightMargin=0.75*inch)
        else:
            doc = SimpleDocTemplate(pdf_path, pagesize=letter, 
                                   topMargin=0.75*inch, 
                                   leftMargin=0.75*inch, 
                                   rightMargin=0.75*inch)
            
        elements = []
        
        # Create a table for the header with logo and hotel info side by side
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'logo2.png')
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=1*inch, height=1*inch)
            
            header_data = [[logo, Paragraph(
                f'<font color="#002B5A" size="14"><b>Ocean Vista Hotel</b></font><br/><br/>' +
                f'<font color="#666666">Malibu Location</font><br/>' +
                f'<font color="#666666">1234 Sunset Blvd, Malibu, CA 90265</font>', 
                self.styles['Normal'])]]
            
            header_table = Table(header_data, colWidths=[1.2*inch, 4.8*inch])
            header_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (1, 0), (1, 0), 'LEFT'),
                ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
                ('RIGHTPADDING', (0, 0), (0, 0), 10),
            ]))
            elements.append(header_table)
        
        # Add yellow horizontal line matching website
        elements.append(Paragraph(
            f'<hr width="100%" color="#F1DF75" thickness="1"/>', 
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Receipt Information - styled as on website
        elements.append(Paragraph("Receipt Information", self.styles['SectionHeader']))
        
        receipt_date = datetime.now().strftime("%B %d, %Y")
        receipt_info = [
            ["Receipt Number:", f"R-{booking.id}-{booking.check_in.strftime('%Y%m%d')}"],
            ["Receipt Date:", receipt_date]
        ]
        
        receipt_table = Table(receipt_info, colWidths=[1.5*inch, 4*inch])
        receipt_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'NotoSans-Bold' if 'NotoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'NotoSans' if 'NotoSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(receipt_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Add yellow divider line matching image 2
        elements.append(Paragraph(
            f'<hr width="100%" color="#F1DF75" thickness="1"/>', 
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Guest Information
        elements.append(Paragraph("Guest Information", self.styles['SectionHeader']))
        
        guest_info = [
            ["Name:", booking.name],
            ["Email:", booking.email],
            ["Phone:", booking.phone]
        ]
        
        guest_table = Table(guest_info, colWidths=[1.5*inch, 4*inch])
        guest_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'NotoSans-Bold' if 'NotoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'NotoSans' if 'NotoSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(guest_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Add yellow divider line matching image 2
        elements.append(Paragraph(
            f'<hr width="100%" color="#F1DF75" thickness="1"/>', 
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Reservation Details
        elements.append(Paragraph("Reservation Details", self.styles['SectionHeader']))
        
        check_in_str = booking.check_in.strftime("%A, %B %d, %Y")
        check_out_str = booking.check_out.strftime("%A, %B %d, %Y")
        
        num_nights = (booking.check_out - booking.check_in).days
        if num_nights == 0:
            num_nights = 1
        
        room_type_str = f"{room.number_beds}-Bedroom {room.room_type.value}"
        if room.wheelchair_accessible.value == 'Y':
            room_type_str += " (Wheelchair Accessible)"
        if room.smoking.value == 'N':
            room_type_str += " | Non-Smoking"
            
        reservation_info = [
            ["Check-In:", check_in_str],
            ["Check-Out:", check_out_str],
            ["Number of Nights:", str(num_nights)],
            ["Room Type:", room_type_str],
            ["Number of Guests:", str(booking.num_guests)]
        ]
        
        reservation_table = Table(reservation_info, colWidths=[1.5*inch, 4*inch])
        reservation_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'NotoSans-Bold' if 'NotoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'NotoSans' if 'NotoSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(reservation_table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Add yellow divider line matching image 2
        elements.append(Paragraph(
            f'<hr width="100%" color="#F1DF75" thickness="1"/>', 
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Charges Table - styled to match website
        elements.append(Paragraph("Charges", self.styles['SectionHeader']))
        
        data = [
            ["Description", "Rate", "Amount"],
            [f"{room.number_beds}-Bedroom {room.room_type.value}", 
             self._format_currency(room_rate), 
             self._format_currency(total_room_charges)],
            ["Resort Fee", self._format_currency(resort_fee / num_nights), self._format_currency(resort_fee)],
            ["Tax (15%)", "", self._format_currency(tax_amount)],
            ["Total", "", self._format_currency(total_amount)]
        ]
        
        table = Table(data, colWidths=[3.0*inch, 1.0*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#F5F5F5')),
            ('TEXTCOLOR', (0, 0), (2, 0), colors.HexColor('#002B5A')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (2, 0), 'NotoSans-Bold' if 'NotoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'NotoSans-Bold' if 'NotoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F5F5F5')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.1*inch))
        
        # Add yellow divider line matching image 2
        elements.append(Paragraph(
            f'<hr width="100%" color="#F1DF75" thickness="1"/>', 
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))
        
        # Payment Information
        elements.append(Paragraph("Payment Information", self.styles['SectionHeader']))
        
        payment_date = booking.check_in.strftime("%B %d, %Y")
        payment_info = [
            ["Payment Method:", "Credit Card"],
            ["Payment Status:", "Paid"],
            ["Payment Date:", payment_date]
        ]
        
        payment_table = Table(payment_info, colWidths=[1.5*inch, 4*inch])
        payment_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'NotoSans-Bold' if 'NotoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'NotoSans' if 'NotoSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        elements.append(Paragraph(
            '<i>Thank you for choosing Ocean Vista Hotels!</i>', 
            self.styles['Center']
        ))

        elements.append(Paragraph(
            '<i>This receipt was generated electronically.</i>', 
            self.styles['Center']
        ))
        
        doc.build(elements)
        
        if return_bytes:
            buffer.seek(0)
            return buffer
        
        return pdf_path