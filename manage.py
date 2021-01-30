# 数据库配置，flask-sqlalchemy
from flask_sqlalchemy import SQLAlchemy
# 脚本管理器，flask-script
from flask_script import Manager
# 数据库迁移，flask-migrate
from flask_migrate import Migrate,MigrateCommand

# 导入工厂函数
from applet_app import create_applet_app
# 导入配置信息的字典
from config import config_dict
# 从models中导入db
from models import db

app = create_applet_app(config_dict['pro_config'])


# 实例化脚本管理器对象
manager = Manager(app)
# 使用迁移框架
Migrate(app,db)
# 添加迁移命令
manager.add_command('db',MigrateCommand)

@app.route("/")
def index():
    return 'index info'


if __name__ == '__main__':
    # app.run()
    # 查看路由映射
    print(app.url_map)
    manager.run()
