from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class AddJobForm(FlaskForm):
    id_tovar = StringField('Id tover')
    submit = SubmitField('Добавить в корзину')
