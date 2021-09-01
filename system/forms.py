from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL


class SearchForm(FlaskForm):
    type = SelectField("Search by", choices=['Asset Tag', 'Serial Number'])
    identifier = StringField("Number", validators=[DataRequired()])
    search_submit = SubmitField("Search")


class EditForm(FlaskForm):
    serial = StringField("Serial", render_kw={'readonly': True})
    asset_tag = StringField("Asset Tag", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    building = SelectField("Building")
    group = SelectField("Group")
    edit_submit = SubmitField("Apply")

