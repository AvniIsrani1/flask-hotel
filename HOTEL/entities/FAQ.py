from ..db import db

class FAQ(db.Model):
    __tablename__ = 'faq'
    """
    A table for storing FAQ information.
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(150), nullable=False)
    answer = db.Column(db.String(500), nullable=False)
    subject = db.Column(db.String(150), nullable=False)

    @classmethod
    def add_faq(cls, f):
        """
        Adds and commits a list of FAQs to the table.
        
        Args:
            f (list[dict]): A list of dictionaries with keys question, answer, and subject

        Returns:
            None
        """
        faqs = []
        for question, answer, subject in f:
            faq = cls(question=question, answer=answer, subject=subject)
            faqs.append(faq)
        db.session.add_all(faqs)
        db.session.commit()