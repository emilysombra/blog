from flask import (Flask, render_template, request, session, redirect,
                   url_for, g)

from werkzeug.utils import secure_filename as secure

from argon2 import PasswordHasher

from datetime import timedelta, datetime

from functions import (formato_permitido, inserir_post, post_por_url,
                       get_posts_por_page, editar_post, buscar_ads,
                       get_popular_posts, incrementar_visita, editar_usuario)
from classes import (Database, Pagination, RedisSessionInterface,
                     Database_access)

import os
import requests
import pickle

PER_PAGE = 10
db = Database()
dba = Database_access()
app = Flask(__name__)
app.session_interface = RedisSessionInterface()
app.secret_key = os.urandom(24)
app_root = os.path.dirname(os.path.abspath(__file__))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

credentials = pickle.load(open('mailgun.pkl', 'rb'))
MAILGUN_DOMAIN_NAME = credentials['nome']
MAILGUN_API_KEY = credentials['key']

# paginas user


@app.route('/')
def index():
    posts = dba.select_posts(ultimos=10)
    return render_template('index.html', posts=posts)


@app.route('/busca')
def busca():
    if('q' not in request.args):
        return redirect(url_for('posts'))

    posts = dba.select_posts(busca=request.args['q'])
    return render_template('busca.html', q=request.args['q'], posts=posts)


@app.route('/posts/', defaults={'pag': 1})
@app.route('/posts/<pag>', methods=['GET'])
def posts(pag):
    try:
        pag = int(pag)
    except ValueError:
        return redirect('/posts/1')

    listposts = dba.select_posts()
    num_posts = len(listposts)

    listposts = get_posts_por_page(listposts, page=pag, per_page=PER_PAGE)
    p = Pagination(pag, PER_PAGE, num_posts)

    if(len(listposts) == 0):
        return redirect('/posts/1')

    return render_template('posts.html', posts=listposts, pagination=p)


@app.route('/posts/ver-post/', defaults={'url_post': None})
@app.route('/posts/ver-post/<url_post>/', methods=['GET'])
def ver_post(url_post):
    if(not url_post):
        return redirect(url_for('posts'))

    post = post_por_url(db, url_post.lower())
    populares = get_popular_posts(db)
    incrementar_visita(db, url_post)

    if(len(post) > 0):
        autor = dba.select_users(nome=post[0][4].split()[0])
        return render_template('ver-post.html', post=post[0], autor=autor,
                               populares=populares)
    else:
        return redirect(url_for('posts'))


@app.route('/sobre/')
def sobre():
    usuarios = dba.select_users()
    return render_template('sobre.html', usuarios=usuarios)


@app.route('/contato/', methods=['GET', 'POST'])
def contato():
    if(request.method == 'POST'):
        nome = request.form['nome'] if request.form['nome'] else 'Anônimo'
        email = request.form['email'] if request.form['email'] else 'Anônimo'
        msg = request.form['msg']

        corpo = "Mensagem enviada por {}.\n".format(nome)
        corpo += "E-mail: {}\n\n".format(email)
        corpo += "Mensagem:\n{}\n".format(msg)

        assunto = "Contato - The Science's on the Table ({})".format(nome)

        url = 'https://api.mailgun.net/v3/{}/messages'
        url = url.format(MAILGUN_DOMAIN_NAME)
        auth = ('api', MAILGUN_API_KEY)
        dados = {
            'from': 'Mailgun User <postmaster@{}>'.format(MAILGUN_DOMAIN_NAME),
            'to': ['marcos.sombraaa@gmail.com'],
            'subject': assunto,
            'text': corpo
        }

        response = requests.post(url, auth=auth, data=dados)
        response.raise_for_status()

        return render_template('contato.html', msg=1)
    else:
        return render_template('contato.html')


# paginas adm


@app.route('/admin/')
def adm_index():
    if(g.user):
        # posts = get_posts(db, False)
        posts = dba.select_posts(active_only=False)
        return render_template('admin/index.html', posts=posts)

    return redirect(url_for('adm_login'))


@app.route('/posts/excluir-post/', defaults={'url_post': None})
@app.route('/posts/excluir-post/<url_post>/', methods=['POST'])
def adm_excluir_post(url_post):
    if((not g.user) or (not url_post)):
        return redirect(url_for('posts'))

    if(request.method == 'POST'):
        senha_user = dba.select_users(email=g.user, max_results=1)[11]
        ph = PasswordHasher()
        try:
            ph.verify(senha_user, request.form['senha'])
            q = "DELETE FROM posts WHERE url='{}';".format(url_post)
            db.cur.execute(q)
            db.conn.commit()
            return redirect(url_for('index'))
        except Exception:
            return redirect('/posts/ver-post/{}/'.format(url_post))
    else:
        return redirect(url_for('posts'))


@app.route('/admin/novo-post/', methods=['POST', 'GET'])
def adm_novo_post():
    if(not g.user):
        return redirect(url_for('adm_login'))

    autor = dba.select_users(email=g.user, max_results=1)
    nome = autor[1] + ' ' + autor[2]

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
        return render_template('admin/novo-post.html', msg=1, autor=nome)
    else:
        return render_template('admin/novo-post.html', msg=0, autor=nome)


@app.route('/usuarios/editar/', methods=['POST', 'GET'])
def adm_editar_usuario():
    if(not g.user):
        return redirect(url_for('index'))

    user = dba.select_users(email=g.user, max_results=1)

    if(request.method == 'POST'):
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        fb = request.form['facebook']
        insta = request.form['instagram']
        github = request.form['github']
        linkedin = request.form['linkedin']
        pesquisa = request.form['pesquisa']
        descricao = request.form['descricao']

        editar_usuario(db, nome, sobrenome, fb, insta, github, linkedin,
                       pesquisa, descricao, g.user)
        return redirect(url_for('adm_usuarios'))
    else:
        return render_template('admin/editar-usuario.html', user=user)


@app.route('/posts/editar-post/', defaults={'url_post': None})
@app.route('/posts/editar-post/<url_post>/', methods=['POST', 'GET'])
def adm_editar_post(url_post):
    if((not g.user) or (not url_post)):
        return redirect(url_for('posts'))

    post = post_por_url(db, url_post.lower())
    if(request.method == 'POST'):
        if(len(post) == 0):
            return redirect(url_for('posts'))
        titulo = request.form['titulo']
        autor = request.form['autor']
        texto = request.form['texto']
        ativo = len(request.form.getlist('ativo'))

        editar_post(db, post, titulo, autor, texto, ativo)

        post = post_por_url(db, url_post.lower())
        return render_template('admin/editar-post.html', post=post[0],
                               autor=post[0][4], msg=1)

    else:
        if(len(post) > 0):
            return render_template('admin/editar-post.html', post=post[0],
                                   autor=post[0][4])
        else:
            return redirect(url_for('posts'))


@app.route('/admin/usuarios/')
def adm_usuarios():
    if(g.user):
        return render_template('admin/ver-usuarios.html',
                               autores=dba.select_users())

    return redirect(url_for('adm_login'))


@app.route('/admin/logout/')
def adm_logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/admin/login/', methods=['POST', 'GET'])
def adm_login():
    if(g.user):
        return redirect(url_for('index'))

    if(request.method == 'POST'):
        session.pop('user', None)

        try:
            user = dba.select_users(email=request.form['email'], max_results=1)
        except Exception:
            return render_template('/admin/login.html', msg=1, logged=0)

        ph = PasswordHasher()
        try:
            ph.verify(user[11], request.form['senha'])
            session.permanent = True
            session['user'] = user[10]
            return redirect(url_for('adm_index'))
        except Exception:
            return render_template('/admin/login.html', msg=1, logged=0)
    else:
        return render_template('/admin/login.html')


@app.before_request
def before_request():
    g.ads = buscar_ads(db)
    g.user = None
    if('user' in session):
        g.user = session['user']


# erros
@app.errorhandler(404)
def handle_not_found(e):
    return render_template('error/404.html')


if __name__ == '__main__':
    app.run()
