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


def get_posts(db, active_only=True):
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


def inserir_post(db, titulo, autor, data, img, texto, ativo):
    q = "SELECT id from usuarios WHERE nome='{}' AND sobrenome='{}';"
    q = q.format(autor.split()[0], autor.split()[1])
    db.cur.execute(q)
    autor = db.cur.fetchall()[0][0]

    q = "INSERT INTO posts (titulo, autor, data, imagem, texto, ativo) " \
        "VALUES ('{}', {}, '{}', '{}', '{}', {});"
    q = q.format(titulo, autor, data, img, texto, ativo)
    db.cur.execute(q)
    db.conn.commit()