import os
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


def incrementar_visita(db, url):
    q = "UPDATE posts SET visitas = visitas + 1 WHERE url='{}';".format(url)
    db.cur.execute(q)
    db.conn.commit()


def editar_usuario(db, nome, sobrenome, fb, insta, github, linkedin, pesquisa,
                   descricao, email):
    q = "UPDATE usuarios SET nome='{}', sobrenome='{}', facebook='{}'," \
        " instagram='{}', github='{}', linkedin='{}', pesquisa='{}', " \
        " descricao='{}' WHERE email='{}';"
    q = q.format(nome, sobrenome, fb, insta, github, linkedin, pesquisa,
                 descricao, email)
    db.cur.execute(q)
    db.conn.commit()
