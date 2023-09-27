from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User


# from email_validator import validate_email


class LoginForm(FlaskForm):
    username = StringField('Логин:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    gender = SelectField('Пол', coerce=str, choices=[('M', 'М'), ('F', 'Ж')])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль',
                              validators=[DataRequired(),
                                          EqualTo('password', message='Пароли не совпадают')])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        """
        Проверяет, не занято ли имя пользователя.

        :param username:
        :return:
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Имя пользователя занято!')

    def validate_email(self, email):
        """
        Проверяет, не зарегистрирован ли email

        :param email:
        :param username:
        :return:
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('На эту почту уже зарегистрирован аккаунт')


class EditProfileForm(FlaskForm):
    """
    Позволяет поменять имя, описание
    """
    username = StringField('Логин', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне', validators=[Length(min=0, max=140)])
    submit = SubmitField('Принять')

    def __init__(self, self_name, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.self_name = self_name

    def validate_username(self, username):
        if username.data != self.self_name:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Имя занято, используйте другое!')


class EmptyForm(FlaskForm):
    submit = SubmitField('Подписаться')


class PostForm(FlaskForm):
    post_tx = TextAreaField('Написать', validators=[DataRequired()])
    """содержит блок текста"""
    submit = SubmitField('Отправить')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Отправить')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Введите новый пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo(password)])
    submit = SubmitField('Подтвердить')
