from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

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
