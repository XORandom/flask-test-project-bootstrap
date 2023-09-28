# flask-test-project-bootstrap

flask-test-project, вместо ручной отрисовки используется bootstrap
# Создание файла для перевода текста
```
 pybabel extract -F babel.cfg -k _ -o messages.pot .
 pybabel init -i messages.pot -d app/translations -l ru
 pybabel init -i messages.pot -d app/translations -l en


 pybabel compile -d app/translations
 pybabel updatate -i messages.pot -d app/translations
```
# flask-test-project

# Создание базы данных
```cmd
flask db init 
flask db migrate -m 'user and post'
flask db upgrade
```
# Удаление пользователя из БД
```cmd
flask shell
>>> user = User.query.get(1)
>>> db.session.delete(user)
>>> db.session.commit()


flask db migrate -m 'new columns in user'
flask db upgrade
```

# Для работы с почтой
```
pip install flask_mail
```
# Генерация ключа восстановления пароля
```
pip install pyjwt 
```
