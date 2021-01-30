from flask_script import Manager
from sqlalchemy import not_

from manage import app
from models import *


manager = Manager(app)

@manager.command
def update_cate_icon():
    """
    从书籍中找封面图片，给所有分类加上图片
    :return:
    """
    book_ids = []
    big_cates = BookBigCategory.query.all()
    for cate in big_cates:
        if len(book_ids) >= 11:
            book_ids = []
        if cate.icon is None:
            book = Book.query.filter(not_(Book.book_id.in_(book_ids))).first()
            book_ids.append(book.book_id)
            cate.icon = book.cover
        db.session.add(cate)
    db.session.flush()
    second_cates = BookCategory.query.all()
    for cate in second_cates:
        if len(book_ids) >= 11:
            book_ids = []
        if cate.icon is None:
            book = Book.query.filter(not_(Book.book_id.in_(book_ids))).first()
            book_ids.append(book.book_id)
            cate.icon = book.cover
        db.session.add(cate)
    db.session.commit()


@manager.command
def add_test_keyword():
    """
    添加搜索关键字，用于测试
    :return:
    """
    words = [
        '斗破',
        '斗破苍穹',
        '武侠',
        '古武',
    ]
    for w in words:
        ob_w = SearchKeyWord.query.filter_by(keyword=w).first()
        if not ob_w:
            ob_w = SearchKeyWord(keyword=w, count=1)
        else:
            ob_w.count += 1
        db.session.add(ob_w)
    db.session.commit()


@manager.command
def update_cate_name():
    """
    更新所有书籍的分类名称
    :return:
    """
    cates = BookCategory.query.all()
    map_cates = {cate.cate_id:cate.cate_name for cate in cates}
    books = Book.query.all()
    for book in books:
        book.cate_name = map_cates[book.cate_id]
        if book.status == 1:
            book.status = 2
        elif book.status == 2:
            book.status = 1
        db.session.add(book)
    db.session.commit()



@manager.option('-c', '--channel', dest='channel', default='')
def update_book(channel):
    """
    拉取书籍，更新到数据库。
    :param channel:
    :return:
    """
    import datetime
    print('Start:', datetime.datetime.now())
    from script.base_book import BookUpdater
    channel = channel.lower()
    channel_class = getattr(getattr(__import__('script.%s_book' % channel), '%s_book' % channel), '%sBookSpider' % channel.capitalize())
    if not channel_class:
        print('book channel not exist!')
        return
    updater = BookUpdater(channel_class)
    updater.pull_book()
    print('End:', datetime.datetime.now())


@manager.command
def init_category():
    """
    初始化分类
    :return:
    """
    import datetime
    print('Start:', datetime.datetime.now())
    from script import update_category
    update_category.add_category()
    print('End:', datetime.datetime.now())


def calc_word_count_from_chapters(book_id):
    """
    计算书籍的总字数
    :param book_id:
    :return:
    """
    sql = 'select sum(word_count) from book_chapters where book_id=%s' %(book_id)
    return db.session.execute(sql).scalar() or 0


@manager.option('-c', '--channel', dest='channel', default='')
def count_words(channel):
    """
    更新某个渠道的书籍，文字数量
    :param channel:
    :return:
    """
    books = Book.query.filter_by(source=channel).all()
    for b in books:
        print('before', b.book_name, b.book_id, b.word_count)
        word_count = calc_word_count_from_chapters(b.book_id)
        if word_count:
            b.word_count = word_count
        print('after', b.book_name, b.book_id, b.word_count)
        db.session.add(b)
    db.session.commit()


if __name__ == "__main__":
    manager.run()
