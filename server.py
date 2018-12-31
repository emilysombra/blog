from flask import Flask, render_template, request, session, redirect
from werkzeug.utils import secure_filename as secure
from argon2 import PasswordHasher
from datetime import timedelta
import psycopg2
import pickle
import os


class Database:
    def __init__(self):
        comando = pickle.load(open('loginbd.pkl', 'rb'))

        self.conn = psycopg2.connect(comando, sslmode='require')
        self.cur = self.conn.cursor()


db = Database()
app = Flask(__name__)
app.secret_key = os.urandom(24)
app_root = os.path.dirname(os.path.abspath(__file__))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)


# funções gerais


def formato_permitido(nome):
    EXTENSOES = set(['png', 'jpg', 'jpeg'])
    return '.' in nome and nome.rsplit('.', 1)[1].lower() in EXTENSOES


def inserir_post(titulo, autor, data, img, texto, ativo):
    q = "SELECT id from usuarios WHERE nome='{}' AND sobrenome='{}';"
    q = q.format(autor.split()[0], autor.split()[1])
    db.cur.execute(q)
    autor = db.cur.fetchall()[0][0]

    q = "INSERT INTO posts (titulo, autor, data, imagem, texto, ativo) " \
        "VALUES ('{}', {}, '{}', '{}', '{}', {});"
    q = q.format(titulo, autor, data, img, texto, ativo)
    db.cur.execute(q)
    db.conn.commit()


def get_usuarios():
    query = 'SELECT * FROM usuarios ORDER BY nome;'
    db.cur.execute(query)
    return db.cur.fetchall()


def usuario_pelo_email(email):
    q = "SELECT * FROM usuarios WHERE email='{}';".format(email)
    db.cur.execute(q)
    return db.cur.fetchall()[0]


def get_posts(active_only=True):
    q = "SELECT p.id, titulo, TO_CHAR(data, 'DD/MM/YYYY'), imagem, " \
        "CONCAT(nome, ' ', sobrenome), texto, ativo FROM posts as p " \
        "INNER JOIN usuarios as u ON p.autor=u.id {}" \
        "ORDER BY p.id desc;"
    if(active_only):
        q = q.format('WHERE ativo=1 ')
    else:
        q = q.format('')
    db.cur.execute(q)
    return db.cur.fetchall()


# paginas user


@app.route('/')
def index():
    posts = get_posts()
    return render_template('index.html', posts=posts)


@app.route('/sobre/')
def sobre():
    usuarios = get_usuarios()
    return render_template('sobre.html', usuarios=usuarios)


@app.route('/contato/')
def contato():
    return render_template('contato.html')


# paginas adm


@app.route('/admin/')
def adm_index():
    if('user' in session):
        posts = get_posts(False)
        return render_template('admin/index.html', posts=posts)

    return redirect('/admin/login/')


@app.route('/admin/novo-post/', methods=['POST', 'GET'])
def adm_novo_post():
    if('user' not in session):
        return redirect('/admin/login/')

    if(request.method == 'POST'):
        from datetime import datetime
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

        inserir_post(titulo, autor, data, img, texto, ativo)
        return render_template('admin/novo-post.html', msg=1)
    else:
        return render_template('admin/novo-post.html', msg=0)


@app.route('/admin/usuarios/')
def adm_usuarios():
    if('user' in session):
        return str(get_usuarios())

    return redirect('/admin/login/')


@app.route('/admin/login/', methods=['POST', 'GET'])
def adm_login():
    if(request.method == 'POST'):
        session.pop('user', None)

        try:
            user = usuario_pelo_email(request.form['email'])
        except Exception:
            return render_template('/admin/login.html', msg=1)

        ph = PasswordHasher()
        try:
            ph.verify(user[11], request.form['senha'])
            session.permanent = True
            session['user'] = user[10]
            return redirect('/admin/')
        except Exception:
            return render_template('/admin/login.html', msg=1)
    else:
        return render_template('/admin/login.html')


if __name__ == '__main__':
    app.run()
