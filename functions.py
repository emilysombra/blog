def formato_permitido(nome):
    EXTENSOES = set(['png', 'jpg', 'jpeg'])
    return '.' in nome and nome.rsplit('.', 1)[1].lower() in EXTENSOES


def inserir_post(db, titulo, autor, data, img, texto, ativo):
    url = gerar_url(db, titulo, autor)

    q = "SELECT id from usuarios WHERE nome='{}' AND sobrenome='{}';"
    q = q.format(autor.split()[0], autor.split()[1])
    db.cur.execute(q)
    autor = db.cur.fetchall()[0][0]

    q = "INSERT INTO posts (titulo, autor, data, imagem, texto, ativo, url) " \
        "VALUES ('{}', {}, '{}', '{}', '{}', {}, '{}');"
    q = q.format(titulo, autor, data, img, texto, ativo, url)
    db.cur.execute(q)
    db.conn.commit()


def editar_post(db, post, titulo, autor, texto, ativo):
    q = "SELECT id from usuarios WHERE nome='{}' AND sobrenome='{}';"
    q = q.format(autor.split()[0], autor.split()[1])
    db.cur.execute(q)
    autor = db.cur.fetchall()[0][0]

    q = "UPDATE posts SET titulo='{}', autor={}, texto='{}', ativo={} " \
        "WHERE id={};".format(titulo, autor, texto, ativo, post[0][0])

    db.cur.execute(q)
    db.conn.commit()


def get_posts_por_page(posts, page=1, per_page=10):
    init = per_page * (page - 1)
    fim = init + per_page
    return posts[init:fim]


def post_por_url(db, url):
    q = "SELECT p.id, titulo, TO_CHAR(data, 'DD/MM/YYYY'), imagem, " \
        "CONCAT(nome, ' ', sobrenome), texto, ativo, url FROM posts AS p " \
        "INNER JOIN usuarios AS u ON p.autor=u.id WHERE url='{}';"

    q = q.format(url)
    db.cur.execute(q)
    return db.cur.fetchall()


def gerar_url(db, titulo, autor):
    url = titulo.lower().replace(' ', '-')[:45]

    posts = post_por_url(db, url)
    if(len(posts) == 0):
        return url
    else:
        url = url[:30] + '-' + autor.lower().replace(' ', '-')
        posts = post_por_url(db, url)

    i = 1
    while(len(posts) > 0):
        url = url[:-1] + str(i)
        i += 1
        posts = post_por_url(db, url)

    return url


def buscar_ads(db):
    db.cur.execute("SELECT * FROM ads;")
    return db.cur.fetchall()


def get_popular_posts(db):
    q = "SELECT titulo, url, visitas FROM posts WHERE ativo=1 "\
        "ORDER BY visitas DESC LIMIT 5;"
    db.cur.execute(q)
    return db.cur.fetchall()


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
