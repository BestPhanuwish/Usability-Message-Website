# init_db.py
import sqlite3

# 创建数据库链接
connection = sqlite3.connect('database/db_info.db')
# 执行db.sql中的SQL语句
with open('db_info.sql') as f:
    connection.executescript(f.read())
# 创建一个执行句柄，用来执行后面的语句
cur = connection.cursor()
# 提交前面的数据操作
connection.commit()
# 关闭链接
connection.close()