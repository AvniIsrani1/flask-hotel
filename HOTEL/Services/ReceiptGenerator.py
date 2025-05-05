import os
from datetime import datetime
from io import BytesIO

import reportlab.platypus as platypus
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class ReceiptGenerator:
    """
    Generate PDF receipts for hotel bookings.

    Note:
        Author: Devansh Sharma
        Documentation: Devansh Sharma
        Created: April 6, 2025
        Modified: May 2, 2025
    """

    def __init__(self):
        """
        Initialize the ReceiptGenerator with directories and styling.
        """
        # Directory for receipts
        self.receipt_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static', 'receipts'
        )
        try:
            os.makedirs(self.receipt_dir, exist_ok=True)
        except Exception:
            pass

        # Register fonts if available
        font_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'static', 'fonts'
        )
        try:
            ttf = os.path.join(font_dir, 'NotoSans-Regular.ttf')
            if os.path.exists(ttf):
                pdfmetrics.registerFont(TTFont('NotoSans', ttf))
            ttf_b = os.path.join(font_dir, 'NotoSans-Bold.ttf')
            if os.path.exists(ttf_b):
                pdfmetrics.registerFont(TTFont('NotoSans-Bold', ttf_b))
        except Exception:
            pass

        # Styles
        self.styles = getSampleStyleSheet()
        base_font = 'NotoSans' if 'NotoSans' in pdfmetrics.getRegisteredFontNames() else 'Helvetica'
        bold_font = 'NotoSans-Bold' if 'NotoSans-Bold' in pdfmetrics.getRegisteredFontNames() else 'Helvetica-Bold'

        self.styles.add(ParagraphStyle(
            name='Center', alignment=TA_CENTER,
            fontName=base_font, fontSize=10
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader', alignment=TA_LEFT,
            fontName=bold_font, fontSize=12,
            textColor=colors.HexColor('#002B5A'),
            spaceAfter=12, spaceBefore=6
        ))
        self.styles.add(ParagraphStyle(
            name='ReceiptItem', alignment=TA_LEFT,
            fontName=base_font, fontSize=10, leading=14
        ))
        self.styles.add(ParagraphStyle(
            name='ReceiptValue', alignment=TA_LEFT,
            fontName=base_font, fontSize=10
        ))

    def _format_currency(self, amount):
        """Format a number as USD currency."""
        return f"${amount:.2f}"

    def generate_receipt(
        self,
        booking,
        room_rate,
        total_room_charges,
        resort_fee,
        tax_amount,
        total_amount,
        save_path=None,
        return_bytes=False
    ):
        """
        Generate a PDF receipt for a booking.
        Returns file path or BytesIO.
        """
        room = booking.rooms
        hotel = room.floors.hotels
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"Receipt_{booking.id}_{timestamp}.pdf"
        pdf_path = save_path or os.path.join(self.receipt_dir, filename)

        if return_bytes:
            buffer = BytesIO()
            doc = platypus.SimpleDocTemplate(
                buffer, pagesize=letter,
                topMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch
            )
        else:
            doc = platypus.SimpleDocTemplate(
                pdf_path, pagesize=letter,
                topMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch
            )

        elements = []

        # Divider
        elements.append(platypus.Paragraph(
            '<hr width="100%" color="#F1DF75" thickness="1"/>',
            self.styles['Normal']
        ))
        elements.append(platypus.Spacer(1, 0.2*inch))

        # Receipt Info
        elements.append(platypus.Paragraph("Receipt Information", self.styles['SectionHeader']))
        receipt_date = datetime.now().strftime("%B %d, %Y")
        info_data = [
            ["Receipt Number:", f"R-{booking.id}-{booking.check_in.strftime('%Y%m%d')}"] ,
            ["Receipt Date:", receipt_date]
        ]
        info_table = platypus.Table(info_data, colWidths=[1.5*inch, 4*inch])
        elements.append(info_table)
        elements.append(platypus.Spacer(1,0.2*inch))

        # Guest Info
        elements.append(platypus.Paragraph("Guest Information", self.styles['SectionHeader']))
        guest_data = [
            ["Name:", booking.name],
            ["Email:", booking.email],
            ["Phone:", booking.phone]
        ]
        guest_table = platypus.Table(guest_data, colWidths=[1.5*inch,4*inch])
        elements.append(guest_table)
        elements.append(platypus.Spacer(1,0.2*inch))

        # Reservation Details
        elements.append(platypus.Paragraph("Reservation Details", self.styles['SectionHeader']))
        check_in_str = booking.check_in.strftime("%A, %B %d, %Y")
        check_out_str = booking.check_out.strftime("%A, %B %d, %Y")
        nights = max(1, (booking.check_out-booking.check_in).days)
        room_desc = f"{room.number_beds}-Bedroom {room.room_type.value}"
        if room.wheelchair_accessible.value=='Y': room_desc += " (Wheelchair Accessible)"
        if room.smoking.value=='N': room_desc += " | Non-Smoking"
        res_data = [
            ["Check-In:", check_in_str],
            ["Check-Out:", check_out_str],
            ["Nights:", str(nights)],
            ["Room Type:", room_desc],
            ["Guests:", str(booking.num_guests)]
        ]
        res_table = platypus.Table(res_data, colWidths=[1.5*inch,4*inch])
        elements.append(res_table)
        elements.append(platypus.Spacer(1,0.2*inch))

        # Charges
        elements.append(platypus.Paragraph("Charges", self.styles['SectionHeader']))
        charges = [
            ["Description","Rate","Amount"],
            [room_desc, self._format_currency(room_rate), self._format_currency(total_room_charges)],
            ["Resort Fee", self._format_currency(resort_fee/nights), self._format_currency(resort_fee)],
            ["Tax (15%)","", self._format_currency(tax_amount)],
            ["Total","", self._format_currency(total_amount)]
        ]
        charge_table = platypus.Table(charges, colWidths=[3*inch,1*inch,1.5*inch])
        elements.append(charge_table)
        elements.append(platypus.Spacer(1,0.2*inch))

        # Payment Info
        elements.append(platypus.Paragraph("Payment Information", self.styles['SectionHeader']))
        pay_date = booking.check_in.strftime("%B %d, %Y")
        pay_data = [["Method:","Credit Card"],["Status:","Paid"],["Date:",pay_date]]
        pay_table = platypus.Table(pay_data, colWidths=[1.5*inch,4*inch])
        elements.append(pay_table)
        elements.append(platypus.Spacer(1,0.3*inch))

        # Footer
        elements.append(platypus.Paragraph(
            '<i>Thank you for choosing Ocean Vista Hotel!</i>',
            self.styles['Center']
        ))
        elements.append(platypus.Paragraph(
            '<i>This receipt was generated electronically.</i>',
            self.styles['Center']
        ))

        # Build
        doc.build(elements)

        if return_bytes:
            buffer.seek(0)
            return buffer
        return pdf_path