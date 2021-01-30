from . import db
from sqlalchemy.sql import func


class BrowseHistory(db.Model):
    """
    浏览记录
    """
    __tablename__ = 'browse_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'))

    book = db.relationship('Book', uselist=False)
    created = db.Column(db.DateTime(), server_default=func.now())
    updated = db.Column(db.DateTime(), server_default=func.now())