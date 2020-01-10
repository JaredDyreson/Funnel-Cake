from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class RegistrationForm(FlaskForm):
  username = StringField(
    'Username', 
    validators=[DataRequired(), Length(min=2, max=20)]
  )
  email = StringField(
    'Email',
    validators=[DataRequired(), Email()]
  )
  password = PasswordField(
    'Password',
    validators=[DataRequired()]
  )
  confirm_password = PasswordField(
    'Confirm Password',
    validators=[DataRequired(), EqualTo('password')]
  )
  submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
  email = StringField(
    'Email',
    validators=[DataRequired(), Email()]
  )
  password = PasswordField(
    'Password',
    validators=[DataRequired()]
  )
  remember = BooleanField('Remember Me')
  
  submit = SubmitField('Login')
class PlaylistMergeForm(FlaskForm):
  playlist_one = StringField(
    'Playlist One',
    validators=[DataRequired()]

  )
  playlist_two = StringField(
    'Playlist Two',
    validators=[DataRequired()]
  )
  playlist_output_name = StringField(
    'Output Name',
    validators=[DataRequired()]
  )
  submit = SubmitField('Merge')

class PlaylistCloneForm(FlaskForm):
  playlist_original = StringField(
    'Playlist One',
    validators = [DataRequired()]
  )
  submit = SubmitField('Clone')
