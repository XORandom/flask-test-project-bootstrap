import config
from app import app, db
from flask import render_template, flash, redirect, url_for, request, g, jsonify
from flask_login import current_user, login_user, logout_user, login_required, login_manager
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordForm, \
    ResetPasswordRequestForm, MessageForm, EditPostForm
from app.models import User, Post, Message
from flask_babel import _, get_locale
from translate_ import get_language, translate

# from werkzeug.urls import url_parse
from urllib.parse import urlparse
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = get_language(form.post_tx.data)
        if len(language) > 5:
            language = ''
        post = Post(body=form.post_tx.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Ваш пост опубликован'))
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page=page,
                                                   per_page=config.Config.POSTS_ON_PAGE, error_out=False)
    # posts = current_user.followed_posts().paginate(page, app.config['POSTS_ON_PAGE'], error_out=False)  # Тоже самое
    if posts.has_next:
        next_page_url = url_for('index', page=posts.next_num)
    else:
        next_page_url = None

    if posts.has_prev:
        prev_page_url = url_for('index', page=posts.prev_num)
    else:
        prev_page_url = None

    return render_template('index.html', title=_('Домашняя страница'), posts=posts, form=form, user=current_user,
                           next_url=next_page_url, prev_url=prev_page_url)


@app.route('/news')
@login_required
def news():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page,
                                                                per_page=app.config['POSTS_ON_PAGE'], error_out=False)
    if posts.has_next:
        next_page_url = url_for('news', page=posts.next_num)
    else:
        next_page_url = None

    if posts.has_prev:
        prev_page_url = url_for('news', page=posts.prev_num)
    else:
        prev_page_url = None
    return render_template('index.html', title=_('Новости'), posts=posts, user=current_user,
                           next_url=next_page_url, prev_url=prev_page_url)
    # Тот же индекс, но без порождения формы для ввода


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Неправильное имя пользователя или пароль '))
            return redirect(url_for('login'))
        login_user(user=user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title=_('Вход'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # user = User(username=form.username.data, email=form.email.data)
        user_new = User()
        user_new.set_gender(form.gender.data)
        user_new.set_username(form.username.data)
        user_new.set_email(form.email.data)
        user_new.set_password(form.password.data)
        db.session.add(user_new)
        db.session.commit()
        flash(_('Регистрация прошла успешно'))
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Регистрация'), form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Изменения сохранены'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Редактирование профиля'),
                           form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user_ = User.query.filter_by(username=username).first_or_404()
    form = EmptyForm()
    page = request.args.get('page', 1, type=int)
    posts = user_.posts.order_by(Post.timestamp.desc()).paginate(page=page,
                                                                 per_page=config.Config.POSTS_ON_PAGE,
                                                                 error_out=False)
    if posts.has_next:
        next_page_url = url_for('user', page=posts.next_num, username=user_.username)
    else:
        next_page_url = None

    if posts.has_prev:
        prev_page_url = url_for('user', page=posts.prev_num, username=user_.username)
    else:
        prev_page_url = None

    return render_template('user.html', user=user_, posts=posts, form=form,
                           next_url=next_page_url, prev_url=prev_page_url,
                           title=_(f'Профиль {user_.username}'))


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())
    # g - глобальные переменные для Flask


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_(f'Пользователь {username} не найден'))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_(f'Нельзя подписаться на самого себя'))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()  # Добавляем связь в БД
        flash(_(f'Вы подписались на {username}'))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        # if user is None:
        #     flash(f'Пользователь {username} не найден')
        #     return redirect(url_for('index'))
        # if user == current_user:
        #     flash(f'Нельзя отписаться от самого себя')
        #     return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()  # Добавляем связь в БД
        flash(_(f'Вы отписались от {username}'))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash(_('Проверь свою почту для восстановления пароля'))
        else:
            flash(_('Данная почта не зарегистрирована'))
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title=_('Сброс пароля'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user_ = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user_.set_password(form.password.data)
        db.session.commit()
        flash(_('Вы установили новый пароль'))
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/delete_post/<id>', methods=['GET', 'POST'])
@login_required
def delete_post(id, url=None):
    """Удаление поста"""
    post = Post.query.get(int(id))
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))
    # return redirect(url_for('url'))


@app.route('/edit_post/<id>', methods=['GET', 'POST'])
@login_required
def edit_post(id, url=None):
    """Редактирование поста"""
    post = Post.query.get(int(id))
    form = EditPostForm(post)
    if form.validate_on_submit() and request.method == 'POST':
        post.body = form.posts.data
        db.session.commit()
        flash(_('Изменения сохранены'))
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.posts.data = post.body
    return render_template('edit_post.html', form=form)


# @app.route('/translate', methods=['POST'])
@app.route('/translate_', methods=['POST'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_lang'], request.form['dest_lang'])})


@app.route('/send_messages/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash(_('Сообщение отправлено'))
        return redirect(url_for('user', username=recipient))
    return render_template('send_message.html', title=_('новое сообщение'),
                           form=form, recipient=recipient)


@app.route('/messages/')
@login_required
def messages():
    return redirect(url_for('messages_page', flag='input'))


@app.route('/messages/<flag>')
@login_required
def messages_page(flag):
    current_user.last_message_read_time = datetime.utcnow()
    #current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    if flag == 'input':
        messages = current_user.messages_received.order_by(
            Message.timestamp.desc()).paginate(
                page=page, per_page=app.config['POSTS_ON_PAGE'], error_out=False)

    else:
        messages = current_user.messages_send.order_by(
            Message.timestamp.desc()).paginate(
            page=page, per_page=app.config['POSTS_ON_PAGE'], error_out=False)

    if flag == 'input':
        next_url = url_for('messages_page', page=messages.next_num, flag='input') \
            if messages.has_next else None
        prev_url = url_for('messages_page', page=messages.prev_num, flag='input') \
            if messages.has_prev else None
    else:
        next_url = url_for('messages_page', page=messages.next_num, flag='output') \
            if messages.has_next else None
        prev_url = url_for('messages_page', page=messages.prev_num, flag='output') \
            if messages.has_prev else None
    return render_template('messages.html', messages=messages,
                           next_url=next_url, prev_url=prev_url)