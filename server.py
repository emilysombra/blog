from flask import (Flask, render_template, request, session, redirect,
                   url_for, g)

from werkzeug.utils import secure_filename as secure

from argon2 import PasswordHasher

from datetime import timedelta, datetime

from functions import (formato_permitido, get_usuarios, inserir_post,
                       usuario_pelo_email, get_posts, get_posts_por_page,
                       buscar_posts, post_por_url)
from classes import (Database, Pagination, RedisSessionInterface)

import os


PER_PAGE = 10
db = Database()
app = Flask(__name__)
app.session_interface = RedisSessionInterface()
app.secret_key = os.urandom(24)
app_root = os.path.dirname(os.path.abspath(__file__))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)


# paginas user


@app.route('/')
def index():
    posts = get_posts(db, ultimos=10)
    return render_template('index.html', posts=posts)


@app.route('/busca')
def busca():
    if('q' not in request.args):
        return redirect(url_for('posts'))

    posts = buscar_posts(db, request.args['q'])
    return render_template('busca.html', q=request.args['q'], posts=posts)


@app.route('/posts/', defaults={'pag': 1})
@app.route('/posts/<pag>', methods=['GET'])
def posts(pag):
    try:
        pag = int(pag)
    except ValueError:
        return redirect('/posts/1')

    listposts = get_posts(db)
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

    if(len(post) > 0):
        return render_template('ver-post.html', post=post[0])
    else:
        return redirect(url_for('posts'))


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
