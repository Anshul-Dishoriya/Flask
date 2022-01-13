from flask_wtf import FlaskForm
from flask_wtf.file import FileField , FileAllowed
from flask_login import current_user
from wtforms import TextAreaField, StringField ,BooleanField ,SubmitField,PasswordField
from wtforms.validators import DataRequired ,Email , Length , EqualTo ,ValidationError
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        label='Username', validators=[DataRequired() , Length(min=2 , max=30)])
    
    email = StringField(
        label='Email', validators=[DataRequired() ,Email()])
    
    password = PasswordField(
        label='Password' ,  validators=[DataRequired(), Length(min=8 , max=40)])
    
    confirm_password = PasswordField(
        label='Confirm Password' , validators=[DataRequired(), EqualTo('password')])
    
    submit = SubmitField(label='Sign Up')

    def validate_username(self ,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username Already Taken!')

    def validate_email(self ,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email Already Taken! Plaese Use another email!')



class LoginForm(FlaskForm):
    email = StringField(
        label='Email',validators=[DataRequired() ,Email()])
    
    password = PasswordField(
        label='Password' , validators=[DataRequired(), Length(min=8 , max=40)])
   
    rememberme = BooleanField(label='Remember Me')
    
    submit = SubmitField(label='Login')


class UpdateAccountForm(FlaskForm):
    username = StringField(
        label='Username',validators=[DataRequired() , Length(min=2 , max=30)])
    
    email = StringField(
        label='Email', validators=[DataRequired() ,Email()])
    
    picture = FileField('Update Profile Picture' , validators=[FileAllowed(['jpg' , 'png'])] )

    submit = SubmitField(label='Update')

    def validate_username(self ,username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username Already Taken!')

    def validate_email(self ,email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email Already Taken! Plaese Use another email!')


class PostForm(FlaskForm):
    title = StringField(label='Title' , validators=[DataRequired()])
    content = TextAreaField(label='Content' ,validators=[DataRequired()] )
    submit = SubmitField('Post')


class RequestResetForm(FlaskForm):
    email = StringField(
        label='Email', validators=[DataRequired() ,Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self ,email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no Account for this Email!!')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        label='New Password' ,  validators=[DataRequired(), Length(min=8 , max=40)])
    confirm_password = PasswordField(
        label='Confirm New Password' , validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')