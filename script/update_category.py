from models import BookCategory, Book, db
from models import BookBigCategory, BookCategoryRelation


def add_category():
    """
    添加分类
    :return:
    """
    cates = [
        {
            'cate_name': '都市',
            'channel': '男生',
            'second_cate':[
                '都市生活',
                '都市激战',
                '热血青春',
                '都市异能',
                '乡村乡土',
                '校园风云',
                '商业大亨',
                '娱乐明星',
                '职场励志',
                '都市重生',
            ]
        },
        {
            'cate_name': '玄幻',
            'channel': '男生',
            'second_cate':[
                '东方玄幻',
                '异世大陆',
                '王朝争霸',
                '高武世界',
            ]
        },
        {
            'cate_name': '奇幻',
            'channel': '男生',
            'second_cate':[
                '剑与魔法',
                '史诗奇幻',
                '黑暗幻想',
                '现代魔法',
            ]
        },
        {
            'cate_name': '武侠',
            'channel': '男生',
            'second_cate': [
                '传统武侠',
                '武侠幻想',
                '国术无双',
                '古武未来',
            ]
        },
        {
            'cate_name': '武侠',
            'channel': '男生',
            'second_cate': [
                '传统武侠',
                '武侠幻想',
                '国术无双',
                '古武未来',
            ]
        },
        {
            'cate_name': '古代言情',
            'channel': '女生',
            'second_cate': [
                '女尊王朝',
                '古典架空',
                '古代情缘',
                '穿越奇情',
            ]
        },
        {
            'cate_name': '仙侠奇缘',
            'channel': '女生',
            'second_cate': [
                '武侠情缘',
                '古典仙侠',
                '现代修真',
                '远古洪荒',
            ]
        },
        {
            'cate_name': '现代言情',
            'channel': '女生',
            'second_cate': [
                '都市生活',
                '婚恋情缘',
                '娱乐明星',
                '善战职场',
            ]
        },
    ]

    for cate in cates:
        # 一级分类
        big_cate = BookBigCategory.query.filter_by(cate_name=cate['cate_name']).first()
        if not big_cate:
            big_cate = BookBigCategory(cate_name=cate['cate_name'],
                                       channel=1 if cate['channel'] == '男生' else 2)
            db.session.add(big_cate)
            db.session.flush()
        # 二级分类
        for name in cate['second_cate']:
            second_cate = BookCategory.query.filter_by(cate_name=name).first()
            if not second_cate:
                second_cate = BookCategory(cate_name=name)
                db.session.add(second_cate)
                db.session.flush()
            # 为一级大类添加二级分类
            br = BookCategoryRelation.query.filter_by(big_cate_id=big_cate.cate_id,
                                                      cate_id=second_cate.cate_id).first()
            if not br:
                br = BookCategoryRelation(big_cate_id=big_cate.cate_id,
                                          cate_id=second_cate.cate_id)
                db.session.add(br)
                db.session.flush()

    db.session.commit()


