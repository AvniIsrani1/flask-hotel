from flask import Blueprint, send_file, session, redirect, url_for, flash
from io import BytesIO
from datetime import datetime
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from ..entities import User

class EventRoutes:
    """
    Class containing event-related routes (event registration and event-pdf download) for Ocean Vista Hotel.

    Note:
        Author: Devansh Sharma
        Documentation: Devansh Sharma
        Created: April 28, 2025
        Modified: April 28, 2025
    """
    def __init__(self, app):
        """
        Initialize Blueprint and register routes.

        Parameters:
            app (Flask): The Flask application instance.
        """
        self.bp = Blueprint('events', __name__)
        self.bp.route(
            "/event/<int:event_id>/invitation/download"
        )(self.download_invitation)
        app.register_blueprint(self.bp)

    def download_invitation(self, event_id):
        """
        Generate and download a PDF invitation for a given event.

        Args:
            event_id (int): The ID of the event.

        Returns:
            Response: PDF invitation file.
        """
        if "user_id" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("userinfo.login"))

        user = User.query.get(session["user_id"])
        if not user:
            flash("User not found.", "error")
            return redirect(url_for("info.events"))

        # Event definitions
        events = {
            1: {
                "event_id": 1,
                "title": "Beach Volleyball",
                "description": "Join us for this amazing volleyball event! Create a team of 4 to enter in this volleyball event. The team with the most points wins a free night stay plus free drinks for one day.",
                "date_time": "June 20, 2025 | 8:00 AM - 3:00 PM",
                "location": "Ocean Vista Beach Front, Malibu",
                "dress_code": "Beach Attire",
                "additional_guests": 3,
                "additional_info": (
                    "• Teams must have exactly 4 players.\n"
                    "• Equipment will be provided.\n"
                    "• Water stations will be available.\n"
                    "• Please arrive 30 minutes early for team registration."
                )
            },
            2: {
                "event_id": 2,
                "title": "Spa Day",
                "description": "We are having a free Spa session on the beach. Enjoy a nice relaxing spa day while hearing the ocean tides. Free Spa, no appointments needed, walk in Spa for all members.",
                "date_time": "June 25, 2025 | 8:00 AM - 3:00 PM",
                "location": "Ocean Vista Beach Front, Malibu",
                "dress_code": "Casual/Beach Attire",
                "additional_guests": 1,
                "additional_info": (
                    "• Bring your own towel if you prefer.\n"
                    "• Spa services are first come, first served.\n"
                    "• Refreshments will be provided."
                )
            },
            3: {
                "event_id": 3,
                "title": "Dining in the Water",
                "description": "Join us for this amazing event that you won't want to miss. We have arranged seating and tables in the water so that you can eat while enjoying the warm water. We are serving a 5 star all you can eat buffet, including crab legs and lobster.",
                "date_time": "June 29, 2025 | 5:00 PM - 10:00 PM",
                "location": "Ocean Vista Beach Front, Malibu",
                "dress_code": "Smart Casual/Swimwear",
                "additional_guests": 2,
                "additional_info": (
                    "• Tables are set up in shallow water - approximately 2 feet deep.\n"
                    "• Changes of clothing are recommended.\n"
                    "• Waterproof containers will be available for personal items."
                )
            },
            4: {
                "event_id": 4,
                "title": "DJ on the Beach",
                "description": "Join us for this amazing event that you won't want to miss. DJ Khalid will be performing out on the beach. There will be drinks, food, and other activities for the whole family.",
                "date_time": "July 3, 2025 | 5:00 PM - 10:00 PM",
                "location": "Ocean Vista Beach Front, Malibu",
                "dress_code": "Beach Party Attire",
                "additional_guests": 4,
                "additional_info": (
                    "• This is a family-friendly event.\n"
                    "• Dance floor set up on the beach.\n"
                    "• Food and drink tickets included with registration."
                )
            },
            5: {
                "event_id": 5,
                "title": "4th of July",
                "description": "Happy 4th of July. Don't miss out, we are hosting a firework show off the coast and everyone is welcome to join. Head down to the beach, save your spot on the sand and enjoy the show.",
                "date_time": "July 4, 2025 | 9:00 PM - 11:00 PM",
                "location": "Ocean Vista Beach Front, Malibu",
                "dress_code": "Casual",
                "additional_guests": 5,
                "additional_info": (
                    "• Bring beach chairs or blankets for seating.\n"
                    "• Fireworks display begins at 9:30 PM.\n"
                    "• Glow sticks and American flags will be provided."
                )
            }
        }
        event_data = events.get(event_id, {
            "event_id": event_id,
            "title": f"Ocean Vista Event #{event_id}",
            "description": "Join us for this special event at Ocean Vista Hotel.",
            "date_time": "TBA",
            "location": "Ocean Vista Hotel, Malibu",
            "dress_code": "Resort Casual",
            "additional_guests": 0,
            "additional_info": (
                "• This invitation is non-transferable.\n"
                "• Please arrive 15 minutes before the event starts.\n"
                "• For any questions, please contact our concierge desk."
            )
        })

        buffer = self.generate_invitation_pdf(user, event_data)
        filename = f"OceanVista_Event_Invitation_{event_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    @staticmethod
    def generate_invitation_pdf(user, event_data):
        """
        Build and return a PDF invitation as a BytesIO buffer.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.75*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='EventTitle',
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=colors.HexColor('#002B5A'),
            spaceAfter=20,
            spaceBefore=10
        ))
        styles.add(ParagraphStyle(
            name='EventHeading',
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#002B5A'),
            spaceAfter=12,
            spaceBefore=6
        ))
        styles.add(ParagraphStyle(
            name='EventDetail',
            alignment=TA_LEFT,
            fontName='Helvetica',
            fontSize=12,
            leading=14
        ))
        styles.add(ParagraphStyle(
            name='CenteredText',
            alignment=TA_CENTER,
            fontName='Helvetica',
            fontSize=10
        ))

        elements = []
        # Header
        elements.append(Paragraph(
            f'<font color="#002B5A" size="20"><b>Ocean Vista Hotel</b></font>',
            styles['EventTitle']
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Event Title
        elements.append(Paragraph(event_data['title'], styles['EventTitle']))

        # QR Code generation
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr_data = f"EVENT:{event_data['event_id']}|USER:{user.id}|TIME:{datetime.now().strftime('%Y%m%d%H%M%S')}"
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer)
        qr_buffer.seek(0)
        qr_pdf_img = Image(qr_buffer, width=2*inch, height=2*inch)
        qr_pdf_img.hAlign = 'CENTER'
        elements.append(qr_pdf_img)
        elements.append(Spacer(1, 0.2*inch))

        # Invitation message
        elements.append(Paragraph(
            f"Dear {user.name},",
            styles['EventDetail']
        ))
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(
            "You are cordially invited to join us for this special event at Ocean Vista Hotel. "
            "Please present this invitation (digital or printed) at the event entrance.",
            styles['EventDetail']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Event Details Table
        event_info = [
            ["Date & Time:", event_data['date_time']],
            ["Location:", event_data['location']],
            ["Dress Code:", event_data['dress_code']],
            ["Guest(s):", f"1 + {event_data['additional_guests']} additional"]
        ]
        event_table = Table(event_info, colWidths=[1.5*inch, 4*inch])
        event_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(event_table)
        elements.append(Spacer(1, 0.2*inch))

        # Event Description
        elements.append(Paragraph("Event Description", styles['EventHeading']))
        elements.append(Paragraph(
            event_data['description'],
            styles['EventDetail']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # DividerLine
        elements.append(Paragraph(
            f'<hr width="100%" color="#F1DF75" thickness="1"/>',
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Additional Information
        elements.append(Paragraph("Additional Information", styles['EventHeading']))
        elements.append(Paragraph(
            event_data['additional_info'],
            styles['EventDetail']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Confirmation ID
        elements.append(Paragraph(
            f"Confirmation ID: OV-{event_data['event_id']}-{user.id}-{datetime.now().strftime('%Y%m%d')}",
            styles['EventDetail']
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Footer
        elements.append(Paragraph(
            '<i>We look forward to seeing you!</i>',
            styles['CenteredText']
        ))
        elements.append(Paragraph(
            '<i>Ocean Vista Hotel</i>',
            styles['CenteredText']
        ))

        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
