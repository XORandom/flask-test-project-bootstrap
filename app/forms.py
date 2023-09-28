from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User
from flask_babel import _, lazy_gettext as _l


# from email_validator import validate_email


class LoginForm(FlaskForm):
    username = StringField(_l('Логин:'), validators=[DataRequired()])
    password = PasswordField(_l('Пароль:'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Запомнить меня'))
    submit = SubmitField(_l('Войти'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Логин'), validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    gender = SelectField(_l('Пол'), coerce=str, choices=[('M', 'М'), ('F', 'Ж')])
    password = PasswordField(_l('Пароль'), validators=[DataRequired()])
    password2 = PasswordField(_l('Повторите пароль'),
                              validators=[DataRequired(),
                                          EqualTo('password', message=_('Пароли не совпадают'))
                                          ])
    submit = SubmitField(_('Регистрация'))

    def validate_username(self, username):
        """
        Проверяет, не занято ли имя пользователя.

        :param username:
        :return:
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Имя пользователя занято!'))

    def validate_email(self, email):
        """
        Проверяет, не зарегистрирован ли email

        :param email:
        :param username:
        :return:
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('На эту почту уже зарегистрирован аккаунт'))


class EditProfileForm(FlaskForm):
    """
    Позволяет поменять имя, описание
    """
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
                raise ValidationError(_('Имя занято, используйте другое!'))


class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Подписаться'))


class PostForm(FlaskForm):
    post_tx = TextAreaField(_l('Написать'), validators=[DataRequired()])
    """содержит блок текста"""
    submit = SubmitField(_l('Отправить'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Отправить'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Введите новый пароль'), validators=[DataRequired()])
    password2 = PasswordField(_l('Повторите пароль'),
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Подтвердить'))


class EditPostForm(FlaskForm):
    posts = TextAreaField(_('Редактировать'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_('Принять'))

    def __init__(self, post_tx, *args, **kwargs):
        super(EditPostForm, self).__init__(*args, **kwargs)
        self.posts_ = post_tx
    """содержит блок текста"""


class MessageForm(FlaskForm):
    message = TextAreaField(_l('Сообщение'), validators=[
        DataRequired()
    ])
    submit = SubmitField(_l('Отправить'))