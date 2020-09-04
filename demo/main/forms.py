# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length


class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind", validators=[DataRequired()])
    submit = SubmitField('Submit')


class EditPostForm(FlaskForm):
    body = TextAreaField("What's on your mind", validators=[DataRequired()])
    submit = SubmitField('Edit')