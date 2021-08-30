from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL


class SearchForm(FlaskForm):
    type = SelectField("Search by", choices=['Asset Tag', 'Serial Number'])
    identifier = StringField("Number", validators=[DataRequired()])
    submit = SubmitField("Search")


