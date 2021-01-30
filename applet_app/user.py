# Flask基本程序实现
import random
from flask import Blueprint,current_app
# 导入日期模块
from datetime import datetime,timedelta
# 导入flask-restful扩展
from flask_restful import Api,Resource,reqparse

# 导入微信工具
from lib.wxauth import get_wxapp_session_key,get_user_info
# 导入模型类
from models.user import User
# 导入数据库sqlalchemy对象
from models import db, Book, BookShelf
# 导入jwt工具
from lib.jwt_utils import generate_jwt



# 创建蓝图对象
user_bp = Blueprint('user_bp',__name__)
# 定义蓝图路由
# @user_bp.route('/')
# def user_info():
#     return 'user info'

# app.register_blueprint(user_bp)

api = Api(user_bp)


# @user_bp.route("/login",methods=['POST'])
class UserLoginResource(Resource):

    def _generate_jwt_token(user_id):
        # 参数：user_id表示生成token的载荷中存储用户信息
        # 步骤：
        # 1、生成当前时间
        now = datetime.utcnow()
        # 2、根据时间差，指定token的过期时间,
        # expire = now + timedelta(hours=24)
        expiry = now + timedelta(hours=current_app.config.get("JWT_EXPIRE_TIME"))
        # 3、调用jwt工具，传入过期时间
        token = generate_jwt({'user_id': user_id}, expire=expiry)
        # 4、返回token
        return token

    def _add_book_shelf(user_id, sex):
        """书架增加默认书籍"""
        books = Book.query.filter(Book.showed == 1).all()
        choice_books = random.sample(books, 5)
        for book in choice_books:
            db.session.add(BookShelf(book_id=book.book_id,
                                     user_id=user_id,
                                     book_name=book.book_name,
                                     cover=book.cover))
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)

    def post(self):
        #- 1、获取参数code,用户登录凭证，有效期五分钟
        # code = request.json.get('code','')
        # #- 2、获取参数iv、envryptedData
        # iv = request.json.get('iv','')
        # envryptedData = request.json.get('envryptedData','')
        # # 判断参数是否存在
        # if not iv or not envryptedData or not code:
        #     return jsonify(msg='参数错误'),403
        req = reqparse.RequestParser()
        req.add_argument('code',type=str,required=True,help='code params error')
        req.add_argument('iv',type=str,required=True,help='iv params error')
        req.add_argument('envryptedData',type=str,required=True,help='envryptedData params error')
        args = req.parse_args()
        code = args.get('code')
        iv = args.get('iv')
        envryptedData = args.get('envryptedData')

        #- 3、调用微信工具，获取session_key
        data = get_wxapp_session_key(code)
        if 'session_key' not in data:
            return {'msg':'获取session_key信息失败','data':data},500
        #- 4、根据session_key，调用微信工具，获取用户信息
        session_key = data['session_key']
        user_info = get_user_info(envryptedData,iv,session_key)
        #- 5、判断是否获取到openID
        if 'openId' not in user_info:
            return {'msg':'获取用户信息失败','user_info':user_info},403
        #- 6、保存用户数据
        #- 查询mysql数据库，判断openID是否存在
        openid = user_info['openId']
        # User.query.filter(User.openId==openid).first()
        try:
            user = User.query.filter_by(openId=openid).first()
        except Exception as e:
            current_app.logger.error(e)
            user = None
        if not user:
            user = User(user_info)
            db.session.add(user)
            # flush表示把当前的模型类对象，刷到数据库中
            try:
                db.session.flush()
            except Exception as e:
                current_app.logger.error(e)
            # ----在书架和书籍模块完成后，补充代码用户登录后，默认添加书籍
            UserLoginResource._add_book_shelf(user.id,sex=user.gender)
        #- 如果用户存在，更新用户信息
        else:
            try:
                user.update_info(user_info)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
        # - 7、调用jwt工具，生成token
        token = UserLoginResource._generate_jwt_token(user.id)
        # - 8、返回数据
        ret_data = {
            'token':token,
            'user_info':{
                'uid':user.id,
                'gender':user.gender,
                'avatarUrl':user.avatarUrl
            },
            "config": {
                "preference": user.preference,
                "brightness": user.brightness,
                "fontSize": user.fontSize,
                "background": user.background,
                "turn": user.turn
            }
        }
        return ret_data


# 添加测试用户，只是用来测试功能展示所用
# @user_bp.route("/temp_add_user",methods=['POST'])

class AddTempUserResource(Resource):

    def post(self):

        # 默认添加用户，用来测试数据
        # 构造用户数据
        data = dict(
            openId = '1'*32,
            nickName = '测试用户001',
            gender = 1,
            city = '广州市',
            province = '广东省',
            country = '中国',
            avatarUrl = 'default'
        )
        # 把模拟的用户数据，通过模型类添加到数据库中
        user = User(data)
        db.session.add(user)
        db.session.commit()
        # 返回结果
        ret_data = {
            'msg':'添加成功',
            'user_id':user.id
        }
        return ret_data


# 使用测试用户，用来模拟登录
# @user_bp.route("/temp_login")

class LoginTempResource(Resource):

    def get(self):
        # 模拟用户登录测试，默认是get请求
        # 以用户id进行测试，查询字符串
        # 生成token，返回token
        # 返回基本信息
        # user_id = request.args.get('user_id')
        # user = User.query.get(user_id)
        # if not user:
        #     return jsonify(msg='用户不存在')
        req = reqparse.RequestParser()
        req.add_argument('user_id', type=int, required=True, help='user_id params error')
        args = req.parse_args()
        user_id = args.get('user_id')
        user = User.query.get(user_id)
        token = UserLoginResource._generate_jwt_token(user.id)
        ret_data = {
            'token': token,
            'user_info': {
                'uid': user.id,
                'gender': user.gender,
                'avatarUrl': user.avatarUrl
            },
            "config": {
                "preference": user.preference,
                "brightness": user.brightness,
                "fontSize": user.fontSize,
                "background": user.background,
                "turn": user.turn
            }
        }
        return ret_data

api.add_resource(UserLoginResource,'/users/login')
api.add_resource(AddTempUserResource,'/users/temp_add_user')
api.add_resource(LoginTempResource,'/users/temp_login')



