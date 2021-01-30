# 导入蓝图
from flask import Blueprint,current_app
# 导入flask_restful扩展
from flask_restful import Api,Resource
# 导入模型类
from models import BookBigCategory,Book

# 创建蓝图对象
recommend_bp = Blueprint('recommend',__name__)

api = Api(recommend_bp)


class RecommendsResource(Resource):
    """
    推荐--同类热门数据推荐
    """
    def get(self,category_id):
        # 1.定义路由，接收url路径参数，作为视图函数的参数
        # 2.根据参数分类id，查询数据库、获取大分类数据
        try:
            big_category = BookBigCategory.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500
        # 定义列表容器，用来存储最终要返回的书籍数据
        books= []
        # 3.判断如果有大分类数据
        if big_category:
            # 4.获取该大分类下面的二级分类数据
            # seconds_ids = []
            # for i in big_category.second_cates:
            #     seconds_ids.append(i.cate_id)
            seconds_id = [i.cate_id for i in big_category.second_cates]
            # 5.根据分类，查询书籍表，获取对应分类的书籍数据，默认查询4条
            try:
                book_list = Book.query.filter(Book.cate_id.in_(seconds_id)).limit(4)
            except Exception as e:
                current_app.logger.error(e)
                return {'msg':'数据库查询错误'},500
            # 6.保存书籍的基本信息
            for book in book_list:
                books.append({
                    'id':book.book_id,
                    'title':book.book_name,
                    'intro':book.intro,
                    'author':book.author_name,
                    'state':book.status,
                    'category_id':book.cate_id,
                    'category_name':book.cate_name,
                    'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover)
                })
        else:
            # 7.如果没有大分类数据，默认返回4条数据。
            try:
                book_list = Book.query.limit(4)
            except Exception as e:
                current_app.logger.error(e)
                return {'msg':'数据库查询错误'},500
            for book in book_list:
                books.append({
                    'id': book.book_id,
                    'title': book.book_name,
                    'intro': book.intro,
                    'author': book.author_name,
                    'state': book.status,
                    'category_id': book.cate_id,
                    'category_name': book.cate_name,
                    'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], book.cover)
                })
        # 转成json格式，返回书籍列表
        return {'data':books}

# 给类视图添加路由
api.add_resource(RecommendsResource,'/recommend/hots/<int:category_id>')
