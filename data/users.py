import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    balance = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    admin = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    img = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=True,
                            default='https://cdn.fishki.net/upload/post/2018/01/07/2477211'
                                    '/1be374bb3fccce2f44c4ddce70c59703.jpg')
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modifed_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    basket = sqlalchemy.Column(sqlalchemy.String, index=True, nullable=True)

    def __repr__(self):
        return f'<Colonist> {self.id} {self.surname} {self.name}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
