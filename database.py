import psycopg2
import os
from argon2 import PasswordHasher
from functions import gerar_url
from user import cria_usuario


class Database:
    def __init__(self):
        comando = os.environ['DATABASE_URL']

        self.conn = psycopg2.connect(comando, sslmode='require')
        self.cur = self.conn.cursor()


class Database_access:
    '''
    Classe para acesso ao banco de dados PostgreSQL
    '''

    def __init__(self):
        self.db = Database()

    def select_ads(self):
        '''
        Retorna a tabela de anúncios
        '''
        self.db.cur.execute("SELECT * FROM ads;")
        return self.db.cur.fetchall()

    def select_users(self, nome=None, sobrenome=None, email=None,
                     max_results=0):
        '''
        Método para realizar buscas de usuários
        Parâmetros:
        nome: busca por um nome específico
        nome: busca por um sobrenome específico
        email: busca por um email eespecífico
        max_results: limita os resultados
        '''

        # query de busca
        q = "SELECT * FROM usuarios {}ORDER BY nome;"
        # adiciona possíveis condições na busca
        if(email):
            q = q.format("WHERE email='{}' ".format(email))
        elif(nome and sobrenome):
            c = "WHERE nome='{}' AND sobrenome='{}' ".format(nome, sobrenome)
            q = q.format(c)
        elif(nome):
            q = q.format("WHERE nome='{}' ".format(nome))
        else:
            q = q.format('')
        # executa a busca
        self.db.cur.execute(q)
        # limita os resultados e retorna
        if(max_results == 1):
            return cria_usuario(self.db.cur.fetchall()[0])
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
        autor = self.select_users(nome=autor[0], sobrenome=autor[1])[0][0]
        # query para inserir o post
        q = "INSERT INTO posts (titulo, autor, data, imagem, texto, ativo, " \
            "url) VALUES ('{}', {}, '{}', '{}', '{}', {}, '{}');"
        q = q.format(titulo, autor, data, img, texto, ativo, url)
        # executa a query
        self.db.cur.execute(q)
        self.db.conn.commit()

    def insert_visita(self, url):
        '''
        Incrementa o contador de visitas de um post
        '''
        q = "UPDATE posts SET visitas = visitas + 1 WHERE url='{}';"
        q = q.format(url)
        self.db.cur.execute(q)
        self.db.conn.commit()

    def update_post(self, id_post, titulo, autor, texto, ativo):
        '''
        Método para alterar um post do banco de dados
        Cada parâmetro é um campo da tabela
        '''
        # busca o id do autor do post
        autor = autor.split()
        autor = self.select_users(nome=autor[0], sobrenome=autor[1])[0][0]
        # query para editar o post
        q = "UPDATE posts SET titulo='{}', autor={}, texto='{}', ativo={} " \
            "WHERE id={};".format(titulo, autor, texto, ativo, id_post)
        # executa a query
        self.db.cur.execute(q)
        self.db.conn.commit()

    def update_users(self, nome, sobrenome, fb, insta, github, linkedin,
                     pesquisa, descricao, email):
        '''
        Método para alterar um usuário do banco de dados
        Cada parâmetro é um campo da tabela
        '''
        # query para editar o usuário
        q = "UPDATE usuarios SET nome='{}', sobrenome='{}', facebook='{}'," \
            " instagram='{}', github='{}', linkedin='{}', pesquisa='{}', " \
            " descricao='{}' WHERE email='{}';"
        q = q.format(nome, sobrenome, fb, insta, github, linkedin, pesquisa,
                     descricao, email)
        # executa a query
        self.db.cur.execute(q)
        self.db.conn.commit()

    def auth_user(self, email, senha):
        user = self.select_users(email=email, max_results=1)
        ph = PasswordHasher()
        try:
            ph.verify(user.senha, senha)
            return True
        except Exception:
            return False

    def delete_post(self, email, senha, url):
        r = self.auth_user(email, senha)
        if(r):
            q = "DELETE FROM posts WHERE url='{}';".format(url)
            self.db.cur.execute(q)
            self.db.conn.commit()
            return 1
        else:
            return 0
