def formato_permitido(nome):
    EXTENSOES = set(['png', 'jpg', 'jpeg'])
    return '.' in nome and nome.rsplit('.', 1)[1].lower() in EXTENSOES


def get_usuarios(db):
    query = 'SELECT * FROM usuarios ORDER BY nome;'
    db.cur.execute(query)
    return db.cur.fetchall()


def usuario_pelo_email(db, email):
    q = "SELECT * FROM usuarios WHERE email='{}';".format(email)
    db.cur.execute(q)
    return db.cur.fetchall()[0]


def usuario_pelo_nome(db, nome):
    q = "SELECT facebook, instagram, github, linkedin, descricao, pesquisa, " \
        "dir_foto FROM usuarios WHERE nome='{}';".format(nome)
    db.cur.execute(q)
    return db.cur.fetchall()[0]


def get_posts(db, active_only=True, ultimos=0):
    q = "SELECT p.id, titulo, TO_CHAR(data, 'DD/MM/YYYY'), imagem, " \
        "CONCAT(nome, ' ', sobrenome), texto, ativo, url FROM posts as p " \
        "INNER JOIN usuarios as u ON p.autor=u.id {}" \
        "ORDER BY p.id desc"
    if(active_only):
        q = q.format('WHERE ativo=1 ')
    else:
        q = q.format('')

    if(ultimos > 0):
        q += " LIMIT {};".format(ultimos)
    else:
        q += ';'
    db.cur.execute(q)
    return db.cur.fetchall()


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


def get_posts_por_page(posts, page=1, per_page=10):
    init = per_page * (page - 1)
    fim = init + per_page
    return posts[init:fim]


def buscar_posts(db, src, active_only=True):
    src = '%' + src.lower() + '%'
    q = "SELECT p.id, titulo, TO_CHAR(data, 'DD/MM/YYYY'), imagem, " \
        "CONCAT(nome, ' ', sobrenome), texto, ativo, url FROM posts AS p " \
        "INNER JOIN usuarios AS u ON p.autor=u.id WHERE (LOWER(texto) " \
        "LIKE '{}' OR LOWER(titulo) LIKE '{}'){} ORDER BY p.id desc;"
    if(active_only):
        q = q.format(src, src, ' AND ativo=1')
    else:
        q = q.format(src, src, '')

    db.cur.execute(q)
    return db.cur.fetchall()


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
