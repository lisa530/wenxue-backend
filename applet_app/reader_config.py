# 导入蓝图
from flask import Blueprint, g, current_app
# 导入flask-restful扩展
from flask_restful import Api,Resource,reqparse,inputs

# 导入用户模型类
from models import User,db
# 导入登录验证装饰器
from lib.decoraters import login_required
# 创建蓝图对象
config_bp = Blueprint('config',__name__)

api = Api(config_bp)


class PreferenceResource(Resource):
    """
    用户阅读偏好设置
    """
    method_decorators = [login_required]
    def post(self):
        # 1.获取参数，post请求体中json数据
        req = reqparse.RequestParser()
        req.add_argument('gender',type=inputs.int_range(0,1),location='json',required=True,help='gender params error')
        args = req.parse_args()
        gender = args.get('gender')
        # 3.查询数据库，用户表，获取用户信息
        try:
            user = User.query.filter_by(id=g.user_id).first()
            user.gender = gender
            # 4.保存数据、提交数据
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库错误'},500

        # 5.返回结果
        return {'msg':'设置成功'}


class ReaderConfigResource(Resource):
    """
    用户阅读器设置
    """
    method_decorators = [login_required]

    def post(self):
        # 1.获取参数、亮度、字号、背景、翻页效果
        req = reqparse.RequestParser()
        req.add_argument('brightness',required=False,location='json',help='brightness params error')
        req.add_argument('font_size',required=False,location='json',help='font_size params error')
        req.add_argument('background',required=False,location='json',help='background params error')
        req.add_argument('turn',required=False,location='json',help='turn params error')
        args = req.parse_args()
        brightness = args.get('brightness')
        font_size = args.get('font_size')
        background = args.get('background')
        turn = args.get('turn')
        # 2.查询数据库，用户表，根据用户id查询用户信息
        try:
            user = User.query.get(g.user_id)
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500
        # 3.保存设置信息，提交数据
        if brightness:
            user.brightness = brightness
        if font_size:
            user.fontSize = font_size
        if background:
            user.background = background
        if turn:
            user.turn = turn
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库错误'},500

        # 4.返回结果
        return {'msg':'设置成功'}

# 给类视图添加路由
api.add_resource(PreferenceResource,'/config/preference')
api.add_resource(ReaderConfigResource,'/config/reader')
