from flask_mail import Message
from werkzeug.exceptions import InternalServerError

from app import mail, app
from flask import render_template
from threading import Thread


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    # sender = отправитель, recipients = получатели
    msg.body = text_body
    print(msg.body)
    msg.html = html_body
    # msg = Message("Feedback", recipients=[app.config['MAIL_USERNAME']])
    #
    # msg.body = "You have received a new feedback from"
    # print(msg.body)
    # print(msg.html)
    # Thread(target=send_async_email, args=(app, msg)).start()
    try:
        mail.send(msg)
    except Exception:
        raise InternalServerError("[MAIL SERVER] not working")


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except ConnectionRefusedError:
            raise InternalServerError("[MAIL SERVER] not working")


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('test',
               sender=app.config['ADMINS'][0],  # Отправитель
               recipients=[user.email],  # Получатели
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
