import config
from app import app, db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required, login_manager
from app.email import send_password_reset_email
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordForm, ResetPasswordRequestForm
from app.models import User, Post

# from werkzeug.urls import url_parse
from urllib.parse import urlparse
from datetime import datetime



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post_tx.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Ваш пост опубликован')
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

    # posts = [
    #     {
    #         'author': {'username': 'Наташа'},
    #         'gender': 'F',
    #         'body': 'Хочется домой...'
    #     },
    #     {
    #         'author': {'username': 'Андрей'},
    #         'gender': 'M',
    #         'body': 'Да пора уже'
    #     }
    # ]
    return render_template('index.html', title='Домашняя страница', posts=posts, form=form, user=current_user,
                           next_url=next_page_url, prev_url=prev_page_url)


@app.route('/news')
@login_required
def news():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page,
                                                                per_page=config.Config.POSTS_ON_PAGE, error_out=False)
    if posts.has_next:
        next_page_url = url_for('news', page=posts.next_num)
    else:
        next_page_url = None

    if posts.has_prev:
        prev_page_url = url_for('news', page=posts.prev_num)
    else:
        prev_page_url = None
    return render_template('index.html', title='Новости', posts=posts, user=current_user,
                           next_url=next_page_url, prev_url=prev_page_url)
    # Тот же индекс, но без порождениия формы для ввода


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user_login = User.query.filter_by(username=form.username.data).first()
        if user_login is None or not user_login.check_password(form.password.data):
            flash('Неправильное имя пользователя или пароль ')
            return redirect(url_for('login'))
        login_user(user=user_login, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Вход', form=form)


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
        flash('Регистрация прошла успешно')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Изменения сохранены')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Редактирование профиля',
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
    # posts = [
    #     {'author': user_, 'body': "Пора домой!!!"},
    #     {'author': user_, 'body': "Скорее уже!!!"}
    # ]
    if posts.has_next:
        next_page_url = url_for('user', page=posts.next_num, username=user_.username)
    else:
        next_page_url = None

    if posts.has_prev:
        prev_page_url = url_for('user', page=posts.prev_num, username=user_.username)
    else:
        prev_page_url = None

    return render_template('user.html', user=user_, posts=posts, form=form,
                           next_url=next_page_url, prev_url=prev_page_url)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.commit()


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f'Пользователь {username} не найден')
            return redirect(url_for('index'))
        if user == current_user:
            flash(f'Нельзя подписаться на самого себя')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()  # Добавляем связь в БД
        flash(f'Вы подписались на {username}')
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
        flash(f'Вы отписались от {username}')
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
            flash('Проверь свою почту для восстановления пароля')
        else:
            flash('Данная почта не зарегистрирована')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Сброс пароля', form=form)


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
        flash('Вы установили новый пароль')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
