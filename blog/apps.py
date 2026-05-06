# blog/apps.py
from django.apps import AppConfig
from django.db import connection

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog'

    def ready(self):
        # 数据库连接检查
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print(f"✅ {self.name} 数据库连接正常")
        except Exception as e:
            print(f"⚠️ {self.name} 数据库连接异常: {e}")

        # 自动注册信号
        try:
            from . import signals
            print(f"✅ {self.name} 信号已注册")
        except ImportError:
            print(f"ℹ️ {self.name} 没有 signals.py 文件，跳过信号注册")