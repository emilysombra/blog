import os
import requests
from datetime import datetime
from werkzeug.utils import secure_filename as secure


def formato_permitido(nome):
    EXTENSOES = set(['png', 'jpg', 'jpeg'])
    return '.' in nome and nome.rsplit('.', 1)[1].lower() in EXTENSOES


def str_data():
    agr = str(datetime.now())
    data = (agr.split(' ')[0]).split('-')[1]
    data += ('/' + (agr.split(' ')[0]).split('-')[2])
    data += ('/' + (agr.split(' ')[0]).split('-')[0])
    return data


def novo_post(dba, requisicao):
    img = requisicao.files['img']
    nome_img = secure(img.filename)
    if(not formato_permitido(nome_img)):
        return -1
    app_root = os.path.dirname(os.path.abspath(__file__))
    alvo = os.path.join(app_root, 'static/img/posts/')
    titulo = requisicao.form['titulo']
    autor = requisicao.form['autor']
    data = str_data()
    destino = '/'.join([alvo, nome_img])
    img.save(destino)
    img = 'img/posts/' + nome_img
    texto = requisicao.form['texto']
    ativo = len(requisicao.form.getlist('ativo'))
    dba.insert_post(titulo, autor, data, img, texto, ativo)
    return 1


def edit_post(dba, requisicao, post):
    if(len(post) == 0):
        return -1
    titulo = requisicao.form['titulo']
    autor = requisicao.form['autor']
    texto = requisicao.form['texto']
    ativo = len(requisicao.form.getlist('ativo'))
    dba.update_post(post[0][0], titulo, autor, texto, ativo)
    return 1


def get_posts_por_page(posts, page=1, per_page=10):
    init = per_page * (page - 1)
    fim = init + per_page
    return posts[init:fim]


def gerar_url(dba, titulo, autor):
    url = titulo.lower().replace(' ', '-')[:45]

    posts = dba.select_posts(url=url)
    if(len(posts) == 0):
        return url
    else:
        url = url[:30] + '-' + autor.lower().replace(' ', '-')
        posts = dba.select_posts(url=url)

    i = 1
    while(len(posts) > 0):
        url = url[:-1] + str(i)
        i += 1
        posts = dba.select_posts(url=url)

    return url


def edit_user(dba, requisicao, email):
    nome = requisicao.form['nome']
    sobrenome = requisicao.form['sobrenome']
    fb = requisicao.form['facebook']
    insta = requisicao.form['instagram']
    github = requisicao.form['github']
    linkedin = requisicao.form['linkedin']
    pesquisa = requisicao.form['pesquisa']
    descricao = requisicao.form['descricao']
    dba.update_users(nome, sobrenome, fb, insta, github, linkedin, pesquisa,
                     descricao, email)


def mail(requisicao):
    MAILGUN_DOMAIN = os.environ['MAILGUN_DOMAIN']
    MAILGUN_API_KEY = os.environ['MAILGUN_API_KEY']

    nome = requisicao.form['nome'] if requisicao.form['nome'] else 'Anônimo'
    email = requisicao.form['email'] if requisicao.form['email'] else 'Anônimo'
    msg = requisicao.form['msg']

    corpo = "Mensagem enviada por {}.\n".format(nome)
    corpo += "E-mail: {}\n\n".format(email)
    corpo += "Mensagem:\n{}\n".format(msg)

    assunto = "Contato - The Science's on the Table ({})".format(nome)

    url = 'https://api.mailgun.net/v3/{}/messages'
    url = url.format(MAILGUN_DOMAIN)
    auth = ('api', MAILGUN_API_KEY)
    dados = {
        'from': 'Mailgun User <postmaster@{}>'.format(MAILGUN_DOMAIN),
        'to': ['marcos.sombraaa@gmail.com'],
        'subject': assunto,
        'text': corpo
    }

    response = requests.post(url, auth=auth, data=dados)
    response.raise_for_status()
