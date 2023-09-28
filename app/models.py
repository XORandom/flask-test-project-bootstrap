"""
Организация баз данных
"""

from datetime import datetime
from time import time

import jwt
from flask_login import UserMixin
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, app

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('following_id', db.Integer, db.ForeignKey('user.id')))
"""Создаем таблицу подписчиков, в ней будут данные из юзера"""


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    email = db.Column(db.String(120), index=True, unique=True)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)

    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    """Связываем пост с его автором"""
    gender = db.Column(db.String(1))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    following = db.relationship('User', secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.following_id == id),
                                backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    """Ассоциация между пользователями и подписчиками"""
    messages_send = db.relationship('Message', foreign_keys='Message.sender_id',
                                    backref='author', lazy='dynamic')
    """Ассоциация между сообщением и отправителем"""
    messages_received = db.relationship('Message', foreign_keys='Message.sender_id',
                                        backref='recipient', lazy='dynamic')
    """Ассоциация между сообщением и отправителем"""
    last_massage_read_time = db.Column(db.DateTime)


    def new_messages(self):
        last_read_time = self.last_massage_read_time or datetime(0, 1, 1)
        return Message.query.filter_by(recipient=self).filter(
            Message.timestamp > last_read_time).count()

    def set_username(self, username):
        self.username = username

    def set_gender(self, gender):
        self.gender = gender

    def set_email(self, email):
        self.email = email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_following(self, user) -> bool:
        """

        :return True, если подписан, False, если нет:
        """
        return self.following.filter(followers.c.following_id == user.id).count() > 0

    def follow(self, user):
        """
        Подписаться
        :return:
        """
        if not self.is_following(user):  # Если нет подписки
            self.following.append(user)

    def unfollow(self, user):
        """

        :param user:
        :return:
        """
        if self.is_following(user):
            self.following.remove(user)

    def followed_posts(self):
        """
        Отображение собственных постов и тех, на которые ты подписан. id подписки = посту.
        :return:
        """
        following = Post.query.join(
            followers, (followers.c.following_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        """Все посты наших подписок"""
        my_posts = Post.query.filter_by(user_id=self.id)
        """Выбираем свои посты"""
        return following.union(my_posts).order_by(Post.timestamp.desc())  # Объединяем и сортируем по времени

    def get_reset_password_token(self, expires_in=600):
        print(jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256'))
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    """
    Посты в соцсети
    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language_ = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)
