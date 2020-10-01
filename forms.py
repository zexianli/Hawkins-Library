from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators, SubmitField
from wtforms.validators import DataRequired, Length


class memberLookUpForm(FlaskForm):
    memberID = StringField('memberID')
    fName = StringField('fName')
    lName = StringField('lName')
    submit = SubmitField('Submit')





class authorAddForm(FlaskForm):
    fName = StringField('First Name')
    lName = StringField('Last Name')
    submit = SubmitField('Submit')