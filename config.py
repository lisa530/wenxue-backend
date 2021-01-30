# # 数据库的连接信息
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql@localhost/wenxue'
# # 动态追踪修改，如果未配置，只会提示警告信息，不影响代码的业务逻辑
# # 如果True，会跟踪数据库信号的变化，对计算机的性能有一定的影响，如果False，不会跟踪数据库信号变化。
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 封装配置的基类
class BaseConfig(object):
    SECRET_KEY = 'FA-LEUOAZDUFK34Lsfdzf-q340=34q234'
    JWT_EXPIRE_TIME = 24

    DEBUG = None
    # 数据库的连接信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@localhost/wxbak'
    # 动态追踪修改，如果未配置，只会提示警告信息，不影响代码的业务逻辑
    # 如果True，会跟踪数据库信号的变化，对计算机的性能有一定的影响，如果False，不会跟踪数据库信号变化。
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 七牛云配置信息
    QINIU_SETTINGS = {
        'access_key': '51DGWfSzbBws6szT3GVoZ8nMuqVVFAFV2P_StMbr',
        'secret_key': 'pAo3kBotA7PQLCuIF9Y2wCc7AfRs0MEss2-qdTbb',
        'bucket_name': 'hmwx01',
        'host': 'pu3lpnbqt.bkt.clouddn.com',
    }

# 开发配置
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    pass

# 生产配置
class ProductionConfig(BaseConfig):
    DEBUG = False
    pass


# 定义字典，实现不同配置类的映射
config_dict = {
    'base_config':BaseConfig,
    'dev_config':DevelopmentConfig,
    'pro_config':ProductionConfig
}