import datetime as _datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import database as _database
import passlib.hash as _hash


class UserModel(_database.Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email= Column(String, unique=True, index=True)
    name = Column(String)
    phone = Column(String)
    password_hash = Column(String)
    created_at = Column(DateTime, default=_datetime.datetime.now)
    posts = relationship("PostModel", back_populates="user")

    def password_verification(self, password: str):
        return _hash.bcrypt.verify(password, self.password_hash)

class PostModel(_database.Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String)
    image = Column(String)
    created_at = Column(DateTime, default=_datetime.datetime.now)
    user = relationship("UserModel", back_populates="posts")

#_database.create_db()  # only run this if you want to create the tables