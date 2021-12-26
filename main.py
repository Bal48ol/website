import sqlite3

import flask
import flask_security
from flask import Flask, render_template, url_for, request, redirect, jsonify, json, blueprints, current_app
from flask_sqlalchemy import SQLAlchemy, os
from datetime import datetime
from flask_security import UserMixin, RoleMixin
from flask_admin import Admin
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import or_
from flask_security import SQLAlchemyUserDatastore
from flask_security import Security
from flask_security import login_required
from flask_security import current_user

from flask_swagger_ui import get_swaggerui_blueprint
from marshmallow import Schema, fields
from flask_marshmallow import Marshmallow
from flask_restful import reqparse, Api, Resource, abort

from werkzeug.utils import secure_filename


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlbase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Qwerty123'
app.config['SECURITY_PASSWORD_SALT'] = 'salt'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['JSON_AS_ASCII'] = False

app.config['IMAGE_UPLOADS'] = '/img/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


db = SQLAlchemy(app)


class Article(db.Model):                                # класс для сохранения записей (база данных)
    id = db.Column(db.Integer, primary_key=True)        # поле которое получает только числа
    title = db.Column(db.String(100), nullable=False)   # Оглавление
    intro = db.Column(db.String(300), nullable=False)   # вступительный текст
    text = db.Column(db.Text, nullable=False)           # основной текст на 300+ символов
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Article %r>' % self.id




#--------------------------------------------------------------------




roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                       )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(100))


class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'), 301)


class AdminView(AdminMixin, ModelView):
    pass


class HomeAdminView(AdminMixin, AdminIndexView):
    pass


admin = Admin(app, 'Return', url='/', index_view=HomeAdminView(name='Home'))
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
admin.add_view(AdminView(Article, db.session))
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Role, db.session))





#--------------------------------------------------------------------





@app.route('/static/<path:path>')
def send_static(path):
    return flask.send_from_directory('static', path)


SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config=
    {
        'app_name': "My App"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)





#--------------------------------------------------------------------


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("sqlbase.db")
    except sqlite3.error as e:
        print(e)
    return conn


@app.route('/recept', methods=['GET'])
def all_recept():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM Article")
        receptes = [
            dict(id=row[0], Название=row[1], Описание=row[3], Дата=row[4])
            for row in cursor.fetchall()
        ]
        if receptes is not None:
            return jsonify(receptes)


@app.route("/recept/<int:id>", methods=["GET"])
def single_recept(id):
    conn = db_connection()
    cursor = conn.cursor()
    recept = None
    if request.method == "GET":
        cursor.execute("SELECT * FROM Article WHERE id=?", (id,))
        recept = [
            dict(id=row[0], Название=row[1], Описание=row[3], Дата=row[4])
            for row in cursor.fetchall()
        ]
        if recept is not None:
            return jsonify(recept)



        """rows = cursor.fetchall()
        for r in rows:
            recept = r
        if recept is not None:
            return json.dumps(recept), 200
        else:
            return "Something wrong", 404"""



#--------------------------------------------------------------------





@app.route('/')
@app.route('/feed')
def feed():
    q = request.args.get('q')
    if q:
        articles = Article.query.filter(Article.title.contains(q) | Article.intro.contains(q)).all()
    else:
        articles = Article.query.order_by(Article.date.desc()).all()

    return render_template("feed.html", articles=articles)


@app.route('/feed/<int:id>', methods=['POST', 'GET'])
def feed_detail(id):
    article = Article.query.get(id)
    return render_template("feed_detail.html", article=article)


@app.route('/feed/<int:id>/del', methods=['POST', 'GET'])
@login_required
def feed_del(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/feed')
    except:
        return "При добавлении рецепта произошла ошибка"


@app.route('/feed/<int:id>/edit', methods=['POST', 'GET'])
@login_required
def feed_edit(id):
    article = Article.query.get(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/feed')
        except:
            return "При редактировании рецепта произошла ошибка"
    else:
        return render_template("feed_edit.html", article=article)


@app.route('/create', methods=['POST', 'GET'])
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/feed')
        except:
            return "При добавлении рецепта произошла ошибка"

    else:
        return render_template("create.html")


@app.route('/about')
def about():
    return render_template("about.html")





if __name__ == "__main__":
    app.run(debug=True)
