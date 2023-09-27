# flask-test-project-bootstrap

flask-test-project, вместо ручной отрисовки используется bootstrap
```
 pybabel extract -F babel.cfg -k _ -o messages.pot .
 pybabel init -i messages.pot -d app/translations -l ru
 pybabel init -i messages.pot -d app/translations -l en


 pybabel compile -d app/translations
 pybabel updatate -i messages.pot -d app/translations
```
