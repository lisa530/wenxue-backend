# 导入蓝图
from flask import Blueprint,current_app
# 导入sqlalchemy提供的逻辑运算符
from sqlalchemy import not_
# 导入flask-restful
from flask_restful import Api,Resource,reqparse

# 导入模型类
from models import SearchKeyWord,Book,db

# 创建蓝图对象
search_bp = Blueprint('search',__name__)

api = Api(search_bp)


class SearchTabListResource(Resource):
    """
    关键词热门搜索
    """
    def get(self):
        # 1.获取参数，用户搜索的关键词key_word
        # key_word = request.args.get("key_word")
        req = reqparse.RequestParser()
        req.add_argument('key_word', type=str, required=True, help='key_word params error')
        args = req.parse_args()
        key_word = args.get('key_word')

        # 2.根据参数，查询数据库，搜索关键词表进行过滤查询、过滤关键词
        # 热门搜索词，默认提供10条数据
        # -------补充关键词是否热门的条件
        # search_list = SearchKeyWord.query.filter(or_(SearchKeyWord.is_hot==True,SearchKeyWord.keyword.contains(key_word))).limit(10)
        try:
            search_list = SearchKeyWord.query.filter(SearchKeyWord.keyword.contains(key_word)).limit(10)
        except Exception as e:
            current_app.logger.error(e)
            return {'msg': '查询数据错误'},500

        # 3.返回查询结果
        data = [{
            'title':index.keyword,
            'isHot':index.is_hot,
        }for index in search_list]
        return {'data':data}

class SearchBooksResource(Resource):
    """
    搜索书本列表
    """
    def get(self):
        req = reqparse.RequestParser()
        req.add_argument('key_word', type=str, required=True, help='key_word params error')
        req.add_argument('page', type=int, required=False,default=1 ,help='page params error')
        req.add_argument('pagesize', type=int, required=False,default=10 ,help='pagesize params error')
        args = req.parse_args()
        key_word = args.get('key_word')
        page = args.get('page')
        pagesize = args.get('pagesize')

        # 3.根据关键词参数，对书籍数据库进行过滤查询，包含
        try:
            query = Book.query.filter(Book.book_name.contains(key_word))
            # 4.判断查询结果
            # 5.对查询结果进行分页处理，items/page/pages
            paginate = query.paginate(page, pagesize, False)
            # 获取分页后的书本数据
            book_list = paginate.items
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500
        # 6.遍历分页后的数据，获取每本书籍的数据
        items = []
        for book in book_list:
            items.append({
                'id':book.book_id,
                'title':book.book_name,
                'intro':book.intro,
                'author':book.author_name,
                'state':book.status,
                'category_id':book.cate_id,
                'category_name':book.cate_name,
                'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover)
            })
        # 7.返回结果
        data = {
            'counts':paginate.total,
            'pages':paginate.pages,
            'page':paginate.page,
            'items':items
        }
        return data

class RecommendsResource(Resource):
    """
    搜索--精准匹配--高匹配--人工推荐
    """
    def get(self):
        # 1.获取参数搜索关键词，key_word
        # key_word = request.args.get('key_word')
        req = reqparse.RequestParser()
        req.add_argument('key_word', type=str, required=True, help='key_word params error')
        args = req.parse_args()
        key_word = args.get('key_word')
        # 2.根据关键词，搜索SearchKeyWord表
        try:
            skw = SearchKeyWord.query.filter(SearchKeyWord.keyword==key_word).first()
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'查询数据库错误'},500
        # 3.判断查询结果，判断关键词是否存在
        # 4.如果不存在，保存关键词
        if skw is None:
            skw = SearchKeyWord(keyword=key_word,count=0)
        # 5.如果存在关键词，count计数加1，如果count大于10，标记为热门关键词
        skw.count += 1
        if skw.count >= 10:
            skw.is_hot = True
        db.session.add(skw)
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
        # 6.定义列表容器，用来存储7条书籍数据的id,进行书籍数据重复的判断
        book_list = []
        # 7.精准匹配1条：根据关键词查询书籍表，用书籍名称进行匹配，保存数据；
        try:
            accurate_data = Book.query.filter_by(book_name=key_word).first()
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据查询异常'},500

        # 定义精准匹配到的字典容器，用来存储匹配到的的书籍数据
        accurate = {}
        # 如果有数据
        if accurate_data:
            accurate = {
                'id':accurate_data.book_id,
                'title':accurate_data.book_name,
                'intro':accurate_data.intro,
                'state':accurate_data.status,
                'category_id':accurate_data.cate_id,
                'category_name':accurate_data.cate_name,
                'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],accurate_data.cover)
            }
            book_list.append(accurate_data.book_id)
        # 8.高匹配2条：根据书名包含查询关键词，并且，该书不是精确查询的数据，默认提取2条，保存数据；
        try:
            query = Book.query.filter(Book.book_name.contains(key_word),not_(Book.book_id.in_(book_list)))
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询异常'},500
        match_data = query.limit(2)
        match = []
        for book in match_data:
            match.append({
                'id':book.book_id,
                'title':book.book_name,
                'intro':book.intro,
                'state':book.status,
                'category_id':book.cate_id,
                'category_name':book.cate_name,
                'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover)
            })
            book_list.append(book.book_id)
        # 9.推荐4条：根据书籍表过滤查询，不在之前查询到数据范围内的书籍，取出4条作为推荐阅读。
        try:
            recommends_data = Book.query.filter(not_(Book.book_id.in_(book_list))).limit(4)
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500
        recommends_list = []
        # 遍历书籍数据
        for book in recommends_data:
            recommends_list.append({
                'id': book.book_id,
                'title': book.book_name,
                'intro': book.intro,
                'state': book.status,
                'category_id': book.cate_id,
                'category_name': book.cate_name,
                'imgURL': 'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'], book.cover)
            })
        # 10.返回结果，精准匹配1条、高匹配2条、推荐4条，共7条书籍数据。
        data = {
            'accurate':accurate,
            'match':match,
            'recommends_list':recommends_list
        }
        return data


# 给类视图添加路由
api.add_resource(SearchTabListResource,'/search/tags')
api.add_resource(SearchBooksResource,'/search/books')
api.add_resource(RecommendsResource,'/search/recommends')




