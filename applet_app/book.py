# 导入蓝图
from flask import Blueprint,request,jsonify,g,current_app
# 导入flask-restful扩展
from flask_restful import Api,Resource,reqparse,inputs
# 导入日期模块
from datetime import datetime

# 导入模型类
from models import Book,BookChapters,BookChapterContent,ReadRate,BrowseHistory,db
# 创建蓝图对象
book_bp = Blueprint('book',__name__,url_prefix='/book')

api = Api(book_bp)

class ChapterListResource(Resource):
    """
    小说目录列表
    """
    def get(self,book_id):
        # 1.获取查询字符串参数，page/pagesize/order
        req = reqparse.RequestParser() # 创建RequestParser
        # 向对象中添加需要校验的参数或转换参数声明
        req.add_argument('page', required=True, type=int, default=1, location='args', help='page paras error')
        req.add_argument('pagesize', required=True, type=int, default=10, location='args', help='pagesize paras error')
        req.add_argument('order', required=True, type=int, defatul=0, location='args', help='order paras error')
        # 校验参数
        args = req.parse_args()
        page = args.get('page')
        pagesize = args.get('pagesize')
        order = args.get('order')

        # 2.根据书籍id参数，查询书籍表
        try:
            book = Book.query.get(book_id)
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500

        if not book:
            return {'msg':'书籍不存在'},404
        # 3.查询书籍章节目录表，按照书籍id进行过滤查询
        try:
            query = BookChapters.query.filter(BookChapters.book_id==book_id)
            # 4.根据order参数的排序条件，如果1倒序排序，如果0升序排序
            if order == 1:
                query = query.order_by(BookChapters.chapter_id.desc())
            else:
                query = query.order_by(BookChapters.chapter_id.asc())
        except Exception as e:
            current_app.logger.error(e) # 输出错误信息到日志中
            return {'msg':'数据库查询错误'},500
        # 5.对排序的结果，进行分页处理
        try:
            paginate = query.paginate(page,pagesize,False)
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500

        data_list = paginate.items
        # 6.遍历分页的数据，获取章节信息
        items = []
        for data in data_list:
            items.append({
                'id':data.chapter_id,
                'title':data.chapter_name
            })
        # 构造响应数据
        chapter_data = {
            'counts':paginate.total,
            'pages':paginate.pages,
            'page':paginate.page,
            'items':items
        }
        # 7.返回数据
        return chapter_data


class ReadBookResource(Resource):
    """
    小说阅读
    """
    def get(self,book_id):
        # 1.根据书籍id查询书籍表
        try:
            book = Book.query.get(book_id)
        # 查询的书籍不存在输出错误信息
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500

        if not book:
            return {'msg':'书籍不存在'},404
        # 2.获取查询字符串参数章节id，校验参数
        req = reqparse.RequestParser()
        # 添加校验参数到req对象中
        req.add_argument('chapter_id', required=True, type=int, default=-1, location='args', help='page paras error')
        # 使用parset_args方法启动校验参数处理
        args = req.parse_args()
        chapter_id = args.get('chapter_id')
        if chapter_id < 1:
            return {'msg':'章节id不能小于1'},400
        # 3.根据章节id，查询书籍章节表
        try:
            chapter = BookChapters.query.get(chapter_id)
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500

        # 4.判断章节id是否有效
        if not chapter:
            return jsonify(msg='章节不存在'),404
        # 5.如果章节数据存在，则查询书籍内容表
        try: # 根据书籍id和章节id过滤查询
            content = BookChapterContent.query.filter_by(book_id=book_id,chapter_id=chapter_id).first()
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500
        # 6.如果用户登录，查询用户阅读进度表；
        progress = None
        if g.user_id:
            try:
                # 根据用户id book_id chapter_id过滤查询
                progress = ReadRate.query.filter_by(book_id=book_id,chapter_id=chapter_id,user_id=g.user_id).first()
            except Exception as e:
                current_app.logger.error(e)
                return {'msg':'数据库查询错误'},500
        # 构造响应数据
        data = {
            'id':book_id, # 书籍id
            'title':book.book_name,
            'chapter_id':chapter.chapter_id,
            'chapter_name':chapter.chapter_name,
            'progress':progress.rate if progress else 0,  # 阅读进度
            'article_content':content.content if content else '' # 章节内容
        }
        # 7.返回
        return data


class BookDetailResource(Resource):
    """小说详情"""
    def get(self,book_id):
        # 1.根据书籍id，查询数据书籍表
        try:
            book = Book.query.get(book_id)
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500

        if not book:
            return {'msg':'书籍不存在'},404
        # 2.判断，如果用户登录，查询用户的浏览记录
        # 查询过滤条件，必须加上书籍id，一个用户可以阅读多本书
        if g.user_id:
            try:
                bs_data = BrowseHistory.query.filter_by(user_id=g.user_id,book_id=book_id).first()
            except Exception as e:
                current_app.logger.error(e)
                return {'msg':'数据库查询错误'},500
            # 3.判断查询结果，保存数据，浏览记录的时间
            if not bs_data:
                bs_data = BrowseHistory(user_id=g.user_id,book_id=book_id)
            bs_data.updated = datetime.now()
            db.session.add(bs_data)
            try:
                db.session.commit()
            except Exception as e:
                current_app.logger.error(e)
                return {'msg':'数据库错误'},500

        # 4.如果用户未登录，根据书籍id查询书籍章节表，默认倒序排序。
        try:
            chapter = BookChapters.query.filter_by(book_id=book_id).order_by(BookChapters.chapter_id.desc()).first()
        except Exception as e:
            current_app.logger.error(e)
            return {'msg':'数据库查询错误'},500
        # 5.返回结果
        data = {
            'id':book.book_id,
            'title':book.book_name,
            'intro':book.intro,
            'author':book.author_name,
            'status':book.status,
            'category_id':book.cate_id,
            'category_name':book.cate_name,
            'words':book.word_count,
            'imgURL':'http://{}/{}'.format(current_app.config['QINIU_SETTINGS']['host'],book.cover),
            'lastChapter':chapter.chapter_name if chapter else None
        }
        return data

# 给视图类添加路由
api.add_resource(ChapterListResource,'/book/chapters/<int:book_id>')
api.add_resource(ReadBookResource,'/book/reader/<int:book_id>')
api.add_resource(BookDetailResource,'/book/<int:book_id>')