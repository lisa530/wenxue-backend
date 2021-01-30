# 导入蓝图
from flask import Blueprint,request,g,current_app,jsonify
# 导入flask-restful扩展
from flask_restful import Api,Resource,reqparse,inputs

# 导入登录验证装饰器
from lib.decoraters import login_required
# 导入模型类
from models import BrowseHistory,db

# 创建蓝图对象
my_bp = Blueprint('my',__name__)

api = Api(my_bp)

class MyHistoryResource(Resource):
    """
    我的浏览记录
    查询记录、删除记录
    """
    method_decorators = [login_required]

    def get(self):
        # 获取参数，page和pagesize
        req = reqparse.RequestParser()
        req.add_argument('page',required=True,default=1,type=int,help='page params error')
        req.add_argument('pagesize',required=True,default=10,type=int,help='pagesize params error')
        args = req.parse_args()
        page = args.get("page")
        pagesize = args.get('pagesize')
        # 查询数据库浏览记录表，根据用户id查询，分页处理
        try:
            paginate = BrowseHistory.query.filter_by(user_id=g.user_id).paginate(page,pagesize,False)
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500
        # 获取分页后的数据
        history_data = paginate.items
        items = []
        for item in history_data:
            # 使用关系引用book，从浏览记录表中，获取书籍表里的数据。
            items.append({
                'id':item.book.book_id,
                'title':item.book.book_name,
                'author':item.book.author_name,
                'status':item.book.status,
                'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],item.book.cover),
                'lastTime':item.updated.strftime('%Y-%m-%d %H:%M:%S')
            })
        # 7.转成json，返回数据
        data = {
            'counts':paginate.total,
            'pagesize':pagesize,
            'pages':paginate.pages,
            'page':paginate.page,
            'items':items
        }
        return {'data':data}

    def delete(self):
        # 1.根据用户id、查询浏览记录表
        try:
            history_data = BrowseHistory.query.filter_by(user_id=g.user_id).all()
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500
        # 2.遍历查询结果
        for data in history_data:
            db.session.delete(data)
        # 3.清除数据
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库错误'},500
        # 4.返回结果
        return {'msg':'OK'}

api.add_resource(MyHistoryResource,'/my/histories')
