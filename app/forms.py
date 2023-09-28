from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l
#from email_validator import validate_email

class LoginForm(FlaskForm):
    username = StringField(_l('Логин'), validators=[DataRequired()])
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Запомнить меня'))
    submit = SubmitField(_l('Войти'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Логин'), validators=[DataRequired()])
    email = StringField(_l('Эл. почта'), validators=[DataRequired(), Email()])
    gender = SelectField(_l('Пол'), coerce=str, choices=[('M', 'М'), ('F', 'Ж')])
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Повторите пароль'), validators=[DataRequired(), EqualTo('password', message=_('Пароли не совпадают'))])
    submit = SubmitField(_l('Регистрация'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Пожалуйста, используйте другой логин'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Пожалуйста, используйте другую почту'))

class EditProfileForm(FlaskForm):
    username = StringField(_l('Логин'), validators=[DataRequired()])
    about_me = TextAreaField(_l('Обо мне'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Принять'))

    def __init__(self, self_name, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.self_name = self_name

    def validate_username(self, username):
        if username.data != self.self_name:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Имя занято, используйте другое'))


class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Подписаться'))


class PostForm(FlaskForm):
    post_tx = TextAreaField(_l('Написать'), validators=[DataRequired()])
    submit = SubmitField(_l('Отправить'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Эл. почта'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Отправить'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Введите новый пароль'), validators=[DataRequired()])
    password2 = PasswordField(_l('Повторите пароль'),
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Подтвердить'))

class MessageForm(FlaskForm):
    message = TextAreaField(_l('Сообщение'), validators=[
        DataRequired()
    ])
    submit = SubmitField(_l('Отправить'))
