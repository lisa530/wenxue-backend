from models import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(UserMixin, db.Model):
    """ 用户表 """
    __tablename__ = 'user'
    id = db.Column(db.Integer(), primary_key=True)
    # 小程序 user_info
    openId = db.Column(db.String(128), unique=True)
    nickName = db.Column(db.String(50))
    gender = db.Column(db.Integer(), server_default='0')  # 1 男 0 女
    city = db.Column(db.String(120))
    province = db.Column(db.String(120))
    country = db.Column(db.String(120))
    avatarUrl = db.Column(db.String(200))

    # 阅读器配置
    preference = db.Column(db.Integer(), server_default='0')  # 0 女 1 男
    brightness = db.Column(db.Integer(), server_default='30')  # 10~100 亮度
    fontSize = db.Column(db.Integer(), server_default='14')  # 字号
    background = db.Column(db.String(10), default='B1')  # B1 ~ B6 内置背景
    turn = db.Column(db.String(10), default='T1')  # T1 仿真 T2 平滑 T3 无 翻页模式

    last_read = db.Column(db.Integer())  # 最后阅读一本书
    last_read_chapter_id = db.Column(db.Integer())  # 最后阅读一本书的章节id

    modified = db.Column(db.DateTime(), server_default=func.now())
    created = db.Column(db.DateTime(), server_default=func.now())

    def __init__(self, data):
        self.openId = data['openId']
        self.update_info(data)

    def update_info(self, data):
        self.nickName = data['nickName']
        self.gender = data['gender']
        self.city = data['city']
        self.province = data['province']
        self.country = data['country']
        self.avatarUrl = data['avatarUrl']
