from math import ceil
from werkzeug.datastructures import CallbackDict
from redis import from_url
from flask.sessions import SessionInterface, SessionMixin
from uuid import uuid4
from datetime import timedelta
import psycopg2
import pickle
from functions import gerar_url


class Pagination(object):
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if(num <= left_edge or
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or
               num > self.pages - right_edge):
                if last + 1 != num:
                    yield None
                yield num
                last = num


class Database:
    def __init__(self):
        comando = pickle.load(open('loginbd.pkl', 'rb'))

        self.conn = psycopg2.connect(comando, sslmode='require')
        self.cur = self.conn.cursor()


class Database_access:
    '''
    Classe para acesso ao banco de dados PostgreSQL
    '''

    def __init__(self):
        self.db = Database()

    def select_users(self, nome=None, email=None, max_results=0):
        '''
        Método para realizar buscas de usuários
        Parâmetros:
        nome: busca por um nome específico
        email: busca por um email eespecífico
        max_results: limita os resultados
        '''

        # query de busca
        q = "SELECT * FROM usuarios {}ORDER BY nome;"
        # adiciona possíveis condições na busca
        if(email):
            condition = "WHERE email='{}' ".format(email)
            q = q.format(condition)
        elif(nome):
            condition = "WHERE nome='{}' ".format(nome)
            q = q.format(condition)
        else:
            q = q.format('')
        # executa a busca
        self.db.cur.execute(q)
        # limita os resultados e retorna
        if(max_results == 1):
            return self.db.cur.fetchall()[0]
        elif(max_results > 1):
            return self.db.cur.fetchall()[:max_results]
        else:
            return self.db.cur.fetchall()

    def select_posts(self, active_only=True, ultimos=0, busca=None, url=None,
                     populares=False):
        '''
        Método para realizar buscas de posts
        Parâmetros:
        active_only: apenas posts ativos
        ultimos: quantos posts devem ser exibidos (0 busca todos)
        busca: posts com algum conteudo especifico
        url: post com uma certa url
        populares: busca os posts mais visitados
        '''

        # query de busca
        q = "SELECT p.id, titulo, TO_CHAR(data, 'DD/MM/YYYY'), imagem, " \
            "CONCAT(nome, ' ', sobrenome), texto, ativo, url FROM posts as p" \
            " INNER JOIN usuarios as u ON p.autor=u.id {}ORDER BY {} desc"

        # caso populares seja true, seta variaveis e ordena por visitas
        if(populares):
            active_only = True
            ultimos = 5
            q = q.format('{}', 'visitas')
        # caso populares seja false, ordena por id
        else:
            q = q.format('{}', 'p.id')

        # configura a seleção de posts ativos ou não
        if(active_only):
            q = q.format('WHERE ativo=1 {}')
        else:
            q = q.format('WHERE ativo=0 {}')

        # caso haja uma busca, configura para buscar pelo titulo ou texto
        if(busca):
            busca = '%' + busca.lower() + '%'
            ultimos = 0
            s = "AND (LOWER(texto) LIKE '{}' OR LOWER(titulo) LIKE '{}') "
            s = s.format(busca, busca)
            q = q.format(s)
        # caso haja uma url, busca por url
        elif(url):
            q = q.format("AND url='{}' ".format(url))
        # busca todos os posts
        else:
            q = q.format('')

        # limita os resultados ou não
        if(ultimos > 0):
            q += " LIMIT {};".format(ultimos)
        else:
            q += ';'

        # realiza a busca e retorna
        self.db.cur.execute(q)
        return self.db.cur.fetchall()

    def insert_post(self, titulo, autor, data, img, texto, ativo):
        '''
        Método para inserir post no banco de dados
        Cada parâmetro é um campo da tabela
        '''

        # gera uma url para o post
        url = gerar_url(self, titulo, autor)
        # busca o id do autor do post
        autor = autor.split()
        q = "SELECT id from usuarios WHERE nome='{}' AND sobrenome='{}';"
        q = q.format(autor[0], autor[1])
        self.db.cur.execute(q)
        autor = self.db.cur.fetchall()[0][0]
        # query para inserir o post
        q = "INSERT INTO posts (titulo, autor, data, imagem, texto, ativo, " \
            "url) VALUES ('{}', {}, '{}', '{}', '{}', {}, '{}');"
        q = q.format(titulo, autor, data, img, texto, ativo, url)
        # executa a query
        self.db.cur.execute(q)
        self.db.conn.commit()


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
