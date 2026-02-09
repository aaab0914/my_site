import subprocess, time, sys

print("设置PostgreSQL Docker容器...")

# 清理旧容器
subprocess.run("docker stop blog-db 2>nul", shell=True)
subprocess.run("docker rm blog-db 2>nul", shell=True)

# 创建容器（使用5550端口）
cmd = 'docker run --name blog-db -e POSTGRES_DB=blogdb '
cmd += '-e POSTGRES_USER=bloguser -e POSTGRES_PASSWORD=blogpass '
cmd += '-p 5550:5432 -d postgres:latest'

print("创建容器...")
if subprocess.run(cmd, shell=True).returncode != 0:
    print("容器创建失败")
    sys.exit(1)

print("等待启动...")
time.sleep(8)

# 检查状态
subprocess.run('docker ps --filter name=blog-db', shell=True)

# 测试连接（移除特殊字符）
test = '''
import psycopg2
try:
    conn = psycopg2.connect(
        dbname="blogdb", user="bloguser",
        password="blogpass", host="localhost",
        port=5550, connect_timeout=10
    )
    print("PostgreSQL连接成功！")
    conn.close()
except Exception as e:
    print(f"错误: {e}")
'''

# 指定UTF-8编码写入文件
with open('_test.py', 'w', encoding='utf-8') as f:
    f.write(test)

subprocess.run([sys.executable, '_test.py'])
subprocess.run('del _test.py 2>nul', shell=True)

# 显示配置
print("\\n完成！请在settings.py中使用:")
print('''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'blogdb',
        'USER': 'bloguser',
        'PASSWORD': 'blogpass',
        'HOST': 'localhost',
        'PORT': '5550',
    }
}
''')

print("运行: python manage.py migrate")