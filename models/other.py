from .base import db

class SearchKeyWord(db.Model):
    """
    搜索关键词
    """
    __tablename__ = 'search_key_word'
    id = db.Column(db.Integer(), primary_key=True)
    keyword = db.Column(db.String(100))
    count = db.Column(db.Integer(), default=0)
    is_hot = db.Column(db.Boolean, default=False)