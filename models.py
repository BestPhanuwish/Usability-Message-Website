'''
models
defines sql alchemy data models
also contains the definition for the room class used to keep track of socket.io rooms

Just a sidenote, using SQLAlchemy is a pain. If you want to go above and beyond, 
do this whole project in Node.js + Express and use Prisma instead, 
Prisma docs also looks so much better in comparison

or use SQLite, if you're not into fancy ORMs (but be mindful of Injection attacks :) )
'''

from sqlalchemy import String, Integer, Boolean, PickleType, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.mutable import MutableList
from typing import Dict

# data models
class Base(DeclarativeBase):
    pass

# model to store user information
class User(Base):
    __tablename__ = "user"
    
    # looks complicated but basically means
    # I want a username column of type string,
    # and I want this column to be my primary key
    # then accessing john.username -> will give me some data of type string
    # in other words we've mapped the username Python object property to an SQL column of type String 
    username: Mapped[str] = mapped_column(String, primary_key=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[int] = mapped_column(String)
    mute: Mapped[bool] = mapped_column(Boolean)
    
    # New attribute to store a list of friends and friend request
    friends = Column(MutableList.as_mutable(PickleType), default=[])
    friend_sent = Column(MutableList.as_mutable(PickleType), default=[])
    friend_request = Column(MutableList.as_mutable(PickleType), default=[])
    
    # Method to add a friend to the user's friend list (your friend tab)
    def add_friend(self, friend_username: str):
        self.friends.append(friend_username)
    
    # Method to remove a friend to the user's friend list (your friend tab)
    def remove_friend(self, friend_username: str):
        self.friends.remove(friend_username)

    # Method to add a friend that you've sent a request to (friend request tab)
    def add_friend_sent(self, friend_username: str):
        self.friend_sent.append(friend_username)
        
    # Method to remove a friend that you've sent a request to (friend request tab)
    def remove_friend_sent(self, friend_username: str):
        self.friend_sent.remove(friend_username)

    # Method to add a friend that sent a request from (notification tab)
    def add_friend_request(self, friend_username: str):
        self.friend_request.append(friend_username)

    # Method to remove a friend that sent a request from (notification tab)
    def remove_friend_request(self, friend_username: str):
        self.friend_request.remove(friend_username)
        
    def get_role(self):
        return self.role
    
    def is_mute(self):
        return self.mute
    

# stateful counter used to generate the room id
class Counter():
    def __init__(self):
        self.counter = 0
    
    def get(self):
        self.counter += 1
        return self.counter

# Room class, used to keep track of which username is in which room
class Room():
    def __init__(self):
        self.counter = Counter()
        # dictionary that maps the username to the room id
        # for example self.dict["John"] -> gives you the room id of 
        # the room where John is in
        self.dict: Dict[str, int] = {}

    def create_room(self, sender: str, receiver: str) -> int:
        room_id = self.counter.get()
        self.dict[sender] = room_id
        self.dict[receiver] = room_id
        return room_id
    
    def join_room(self,  sender: str, room_id: int) -> int:
        self.dict[sender] = room_id

    def leave_room(self, user):
        if user not in self.dict.keys():
            return
        del self.dict[user]

    # gets the room id from a user
    def get_room_id(self, user: str):
        if user not in self.dict.keys():
            return None
        return self.dict[user]
    
