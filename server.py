from flask import (Flask, render_template, request, session, redirect,
                   url_for, g, abort)
from datetime import timedelta
from pagination import Pagination
from database import Database_access, Database
from functions import edit_post, novo_post, edit_user, get_posts_por_page, mail
from sessions import RedisSessionInterface
import os
import json
# import boto3 as b3
# from botocore.client import Config

PER_PAGE = 10
db = Database()
dba = Database_access()
app = Flask(__name__)
app.session_interface = RedisSessionInterface()
app.secret_key = os.urandom(24)
app_root = os.path.dirname(os.path.abspath(__file__))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

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
        return abort(404)

    url_post = url_post.lower()
    post = dba.select_posts(url=url_post)
    populares = dba.select_posts(populares=True)
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    dba.insert_visita(ip, url_post)
    tags = dba.select_tags(post=url_post)

    if(len(post) > 0):
        post = post[0]
        autor = dba.select_users(nome=post.autor.split()[0], max_results=1)
        return render_template('ver-post.html', post=post, autor=autor,
                               populares=populares, tags=tags)
    else:
        return redirect(url_for('posts'))


@app.route('/sobre/')
def sobre():
    autores = dba.select_users()
    return render_template('sobre.html', autores=autores)


@app.route('/contato/', methods=['GET', 'POST'])
def contato():
    if(request.method == 'POST'):
        mail(request)

        return render_template('contato.html', msg=1)
    else:
        return render_template('contato.html')


# paginas adm


@app.route('/admin/')
def adm_index():
    if(g.user):
        posts = dba.select_posts(active_only=False)
        return render_template('admin/index.html', posts=posts)

    return redirect(url_for('adm_login'))


@app.route('/posts/excluir-post/', defaults={'url_post': None})
@app.route('/posts/excluir-post/<url_post>/', methods=['POST', 'GET'])
def adm_excluir_post(url_post):
    if((not g.user) or (not url_post)):
        return abort(404)

    if(request.method == 'POST'):
        r = dba.delete_post(g.user, request.form['senha'], url_post)
        if(r):
            return redirect(url_for('index'))

        return redirect('/posts/ver-post/{}/'.format(url_post))
    else:
        return abort(404)


@app.route('/admin/novo-post/', methods=['POST', 'GET'])
def adm_novo_post():
    if(not g.user):
        return abort(404)

    autor = dba.select_users(email=g.user, max_results=1)

    if(request.method == 'POST'):
        r = novo_post(dba, request)
        if(r == -1):
            return render_template('admin/novo-post.html', msg=2)

        return render_template('admin/novo-post.html', msg=1, autor=autor)
    else:
        return render_template('admin/novo-post.html', msg=0, autor=autor)


@app.route('/usuarios/editar/', methods=['POST', 'GET'])
def adm_editar_usuario():
    if(not g.user):
        return abort(404)

    user = dba.select_users(email=g.user, max_results=1)

    if(request.method == 'POST'):
        edit_user(dba, request, g.user)
        return redirect(url_for('adm_usuarios'))
    else:
        return render_template('admin/editar-usuario.html', user=user)


@app.route('/posts/add-tags/', methods=['POST', 'GET'])
def admin_add_tags():
    if((not g.user) or (request.method == 'GET')):
        return abort(404)

    url = request.form['url_post']
    dba.insert_tag_post(request.form['tag'], url)
    return redirect('/posts/controle-tags/{}/'.format(url))


@app.route('/posts/remove-tags/', methods=['POST', 'GET'])
def admin_remove_tags():
    if((not g.user) or (request.method == 'GET')):
        return abort(404)

    url = request.form['url_post']
    dba.delete_tag_post(url, tag=request.form['tag'])
    return redirect('/posts/controle-tags/{}/'.format(url))


@app.route('/posts/controle-tags/', defaults={'url_post': None})
@app.route('/posts/controle-tags/<url_post>/')
def adm_controle_tags(url_post):
    if((not g.user) or (not url_post)):
        return abort(404)

    url_post = url_post.lower()
    post = dba.select_posts(url=url_post)
    tags_inc = dba.select_tags(post=url_post)
    tags_exc = dba.select_tags(post=url_post, inc=False)
    if(len(post) > 0):
        return render_template('admin/gerenciar-tags.html', post=post[0],
                               tags_inc=tags_inc, tags_exc=tags_exc)

    return abort(404)


@app.route('/posts/editar-post/', defaults={'url_post': None})
@app.route('/posts/editar-post/<url_post>/', methods=['POST', 'GET'])
def adm_editar_post(url_post):
    if((not g.user) or (not url_post)):
        return abort(404)

    post = dba.select_posts(url=url_post.lower())
    if(request.method == 'POST'):
        r = edit_post(dba, request, post)
        if(r == -1):
            return redirect(url_for('posts'))

        post = dba.select_posts(url=url_post.lower())
        return render_template('admin/editar-post.html', post=post[0],
                               autor=post[0].autor, msg=1)

    else:
        if(len(post) > 0):
            return render_template('admin/editar-post.html', post=post[0],
                                   autor=post[0].autor)
        else:
            return redirect(url_for('posts'))


@app.route('/admin/usuarios/')
def adm_usuarios():
    if(g.user):
        return render_template('admin/ver-usuarios.html',
                               autores=dba.select_users())

    return abort(404)


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
        if(dba.auth_user(request.form['email'], request.form['senha'])):
            session.permanent = True
            session['user'] = request.form['email']
            return redirect(url_for('adm_index'))
        else:
            return render_template('/admin/login.html', msg=1, logged=0)
    else:
        return render_template('/admin/login.html')


@app.route('/admin/ads/')
def adm_ads():
    if(not g.user):
        return abort(404)
    return render_template('/admin/ads.html')


@app.route('/admin/novo-ad/', methods=['POST', 'GET'])
def adm_novo_ad():
    if(not g.user):
        return abort(404)

    if(request.method == 'POST'):
        r = 1
        if(r == -1):
            return render_template('admin/novo-ad.html', msg=2)

        return render_template('admin/novo-ad.html', msg=1)
    else:
        return render_template('/admin/novo-ad.html')


@app.route('/sign_s3/')
def sign_s3():
    return abort(404)
    bucket = os.environ.get('SCIENCE_BUCKET')

    file_name = request.args.get('file_name')
    file_type = request.args.get('file_type')

    # s3 = b3.client('s3', config=Config(signature_version='s3v4'))
    s3 = ''
    post = s3.generate_presigned_post(Bucket=bucket, Key=file_name,
                                      Fields={"acl": "public-read",
                                              "Content-Type": file_type},
                                      Conditions=[{"acl": "public-read"},
                                                  {"Content-Type": file_type}],
                                      ExpiresIn=3600)

    url = 'https://{{}}.s3.amazonaws.com/{{}}'.format(bucket, file_name)
    return json.dumps({'data': post, 'url': url})


@app.before_request
def before_request():
    g.ads = dba.select_ads()
    g.brand = 'Science on the Table'
    g.user = None
    if('user' in session):
        g.user = session['user']


# erros
@app.errorhandler(404)
def handle_not_found(e):
    return render_template('error/404.html'), 404


if __name__ == '__main__':
    app.run()
