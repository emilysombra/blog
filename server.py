from flask import (Flask, render_template, request, session, redirect,
                   url_for, g)
from flask.sessions import SessionInterface, SessionMixin

from redis import from_url

from werkzeug.utils import secure_filename as secure
from werkzeug.datastructures import CallbackDict

from argon2 import PasswordHasher

from datetime import timedelta, datetime

from functions import (formato_permitido, get_usuarios, inserir_post,
                       usuario_pelo_email, get_posts)

from uuid import uuid4
import os

import psycopg2

import pickle


class RedisSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False


class RedisSessionInterface(SessionInterface):
    serializer = pickle
    session_class = RedisSession

    def __init__(self, redis=None, prefix='session:'):
        if redis is None:
            redis_url = pickle.load(open('redis_url.pkl', 'rb'))
            redis = from_url(redis_url)
        self.redis = redis
        self.prefix = prefix

    def generate_sid(self):
        return str(uuid4())

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        val = self.redis.get(self.prefix + sid)
        if val is not None:
            data = self.serializer.loads(val)
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            self.redis.delete(self.prefix + session.sid)
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = self.serializer.dumps(dict(session))
        self.redis.setex(self.prefix + session.sid,
                         int(redis_exp.total_seconds()),
                         val)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=cookie_exp, httponly=True,
                            domain=domain)


class Database:
    def __init__(self):
        comando = pickle.load(open('loginbd.pkl', 'rb'))

        self.conn = psycopg2.connect(comando, sslmode='require')
        self.cur = self.conn.cursor()


db = Database()
app = Flask(__name__)
app.session_interface = RedisSessionInterface()
app.secret_key = os.urandom(24)
app_root = os.path.dirname(os.path.abspath(__file__))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)


# paginas user


@app.route('/')
def index():
    posts = get_posts(db)
    return render_template('index.html', posts=posts)


@app.route('/sobre/')
def sobre():
    usuarios = get_usuarios(db)
    return render_template('sobre.html', usuarios=usuarios)


@app.route('/contato/')
def contato():
    return render_template('contato.html')


# paginas adm


@app.route('/admin/')
def adm_index():
    if(g.user):
        posts = get_posts(db, False)
        return render_template('admin/index.html', posts=posts)

    return redirect(url_for('adm_login'))


@app.route('/admin/novo-post/', methods=['POST', 'GET'])
def adm_novo_post():
    if(not g.user):
        return redirect(url_for('adm_login'))

    if(request.method == 'POST'):
        alvo = os.path.join(app_root, 'static/img/posts/')

        titulo = request.form['titulo']

        autor = request.form['autor']

        agr = str(datetime.now())
        data = (agr.split(' ')[0]).split('-')[1]
        data += ('/' + (agr.split(' ')[0]).split('-')[2])
        data += ('/' + (agr.split(' ')[0]).split('-')[0])

        img = request.files['img']
        nome_img = secure(img.filename)
        if(not formato_permitido(nome_img)):
            return render_template('admin/novo-post.html', msg=2)
        destino = '/'.join([alvo, nome_img])
        img.save(destino)
        img = 'img/posts/' + nome_img

        texto = request.form['texto']

        ativo = len(request.form.getlist('ativo'))

        inserir_post(db, titulo, autor, data, img, texto, ativo)
        return render_template('admin/novo-post.html', msg=1)
    else:
        autor = usuario_pelo_email(db, g.user)
        nome = autor[1] + ' ' + autor[2]
        return render_template('admin/novo-post.html', msg=0, autor=nome)


@app.route('/admin/usuarios/')
def adm_usuarios():
    if(g.user):
        return str(get_usuarios(db))

    return redirect(url_for('adm_login'))


@app.route('/admin/logout/')
def adm_logout():
    session.pop('user', None)
    return redirect(url_for('adm_login'))


@app.route('/admin/login/', methods=['POST', 'GET'])
def adm_login():
    if(g.user):
        return redirect(url_for('adm_index'))

    if(request.method == 'POST'):
        session.pop('user', None)

        try:
            user = usuario_pelo_email(db, request.form['email'])
        except Exception:
            return render_template('/admin/login.html', msg=1, logged=0)

        ph = PasswordHasher()
        try:
            ph.verify(user[11], request.form['senha'])
            session.permanent = True
            session['user'] = user[10]
            return redirect('/admin/')
        except Exception:
            return render_template('/admin/login.html', msg=1, logged=0)
    else:
        return render_template('/admin/login.html')


@app.before_request
def before_request():
    g.user = None
    if('user' in session):
        g.user = session['user']


if __name__ == '__main__':
    app.run()
