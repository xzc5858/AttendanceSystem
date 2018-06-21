from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateTimeField, IntegerField, SelectField, \
    SelectMultipleField, RadioField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError


class changePassword(FlaskForm):
    old_password = PasswordField('password', validators=[DataRequired(), Length(6, 64)])
    password = PasswordField('newpass', validators=[DataRequired(), Length(6, 64),
                                                    EqualTo('repass', message='Passwords must match')])
    password2 = PasswordField('repass', validators=[DataRequired()])
    submit = SubmitField('Update Password')


class application(FlaskForm):
    leaveuser = SelectField('leaveuser', validators=[DataRequired(), Length(1, 64)])
    StartTime = DateTimeField('StartTime', validators=[])
    EndTime = DateTimeField('EndTime', validators=[])
    SubUser = SelectField('SubUser', validators=[])
    other = SelectField('other', validators=[])
    Category = SelectField('Category', validators=[])
