from ..db import db

class FAQ(db.Model):
    """
    A table for storing FAQ information.

    Note:
        Author: Avni Israni
        Documentation: Avni Israni
        Created: March 6, 2025
        Modified: April 17, 2025
    """
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(150), nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    subject = db.Column(db.String(150), nullable=False)

    @classmethod
    def add_faqs(cls, f):
        """
        Adds and commits a list of FAQs to the table.
        
        Parameters:
            f (list[dict]): A list of dictionaries with keys: question, answer, and subject

        Returns:
            None
        """
        faqs = []
        for item in f:
            faq = cls(question=item["question"], answer=item["answer"], subject=item["subject"])
            faqs.append(faq)
        db.session.add_all(faqs)
        db.session.commit()