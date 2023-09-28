import os
from flask import Flask, current_app, request
from flask_babel import Babel, _, lazy_gettext as _l

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from config import Config

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'python flask'
# app.config['SECRET_KEY'] = Config.SECRET_KEY  # Явное присвоение не нужно, если название SECRET_KEY
app.config.from_object(Config)  # Можно использовать следующий вариант
db = SQLAlchemy(app)
"""База данных"""
migrate = Migrate(app, db)
"""Отвечает за миграцию"""
login = LoginManager(app)
"""Отвечает за логины"""
login.login_view = 'login'
"""Ищет маршрут login, будет подставлять имя пользователя в строку браузера"""
login.login_message = _l('Для просмотра необходима авторизация')
"""Замена английского сообщения на русское"""
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
"""Переводит отображение времени в другой вид. Moment - библиотека JS"""


def get_local():
    """Перевод на местный язык. Смотрит язык браузера"""
    return request.accept_languages.best_match(app.config['LANGUAGES'])


babel = Babel(app)
babel.init_app(app, locale_selector=get_local)
"""Инициализирует начальный язык"""

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='example@' + app.config['MAIL_SERVER'],  # От кого
            toaddrs=app.config['ADMINS'],  # Для кого
            subject='Your app crashes',  # Тема сообщения
            credentials=auth,  # Имя пользователя и пароль от почтового сервера
            secure=secure
        )  # ЭТИ НАСТРОЙКИ ПРОИЗВОДЯТСЯ СО ЗНАНИЕМ ПОЧТОВОГО СЕРВЕРА
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/mylogs.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    file_handler.setLevel(logging.INFO)
    app.logger.info('My app start')

from app import routes, models, errors
