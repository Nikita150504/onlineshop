import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Payment(SqlAlchemyBase):
    __tablename__ = 'payments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    sum_cost = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    quantity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    status = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')

    def __repr__(self):
        return f'<Payment> {self.id}'
