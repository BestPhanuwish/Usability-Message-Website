'''
db
database file, containing all the logic to interface with the sql database
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import *

import sqlite3

from pathlib import Path

# creates the database directory
Path("database") \
    .mkdir(exist_ok=True)
    
# init_db.py
# 创建数据库链接
connection = sqlite3.connect('database/db_info.db')
# 执行db.sql中的SQL语句
with open('db_info.sql') as f:
    connection.executescript(f.read())
# 创建一个执行句柄，用来执行后面的语句
cur = connection.cursor()
# 插入两条文章
cur.execute("INSERT INTO posts (title, content, author, role) VALUES (?, ?, ?, ?)",
            ('Hello Night', 'Try db', '111', 'Student')
            )
# 提交前面的数据操作
connection.commit()
# 关闭链接
connection.close()


# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine = create_engine("sqlite:///database/main.db", echo=True)

# initializes the database
Base.metadata.create_all(engine)


# "database/main.db" specifies the database file
# change it if you wish
# turn echo = True to display the sql output
engine2 = create_engine("sqlite:///database/chat_database.db", echo=True)
# initializes the database
Base.metadata.create_all(engine2)


# inserts a user to the database
def insert_user(username: str, password: str, role: str):
    with Session(engine) as session:
        user = User(username=username, password=password, role=role, mute=False)
        session.add(user)
        session.commit()

# gets a user from the database
def get_user(username: str):
    with Session(engine) as session:
        return session.query(User).filter_by(username=username).first()

# gets a role from user database
def get_role(username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        return user.get_role()

# check if user got muted
def is_mute(username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        return user.is_mute()

### Below is what I've implemented ###

# add friend to the database
def add_friend(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.add_friend(friend_username)
        session.commit()
        
# remove friend on the database
def remove_friend(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.remove_friend(friend_username)
        session.commit()

# add friend sent to the database
def add_friend_sent(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.add_friend_sent(friend_username)
        session.commit()

# remove friend sent on the database
def remove_friend_sent(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.remove_friend_sent(friend_username)
        session.commit()

# add friend request to the database
def add_friend_request(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.add_friend_request(friend_username)
        session.commit()
        
# remove friend request on the database
def remove_friend_request(username: str, friend_username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.remove_friend_request(friend_username)
        session.commit()

# mute user
def mute_user(username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.mute = True
        session.commit()

# unmute user
def unmute_user(username: str):
    with Session(engine) as session:
        user = session.query(User).filter_by(username=username).first()
        user.mute = False
        session.commit()