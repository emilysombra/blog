from flask import Flask, render_template
import psycopg2
import pickle


class Database:
    def __init__(self):
        comando = pickle.load(open('loginbd.pkl', 'rb'))

        self.conn = psycopg2.connect(comando, sslmode='require')
        self.cur = self.conn.cursor()


db = Database()
app = Flask(__name__)


# funções gerais


def get_usuarios():
    query = 'SELECT * FROM usuarios ORDER BY nome;'
    db.cur.execute(query)
    return db.cur.fetchall()


# paginas user


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sobre/')
def sobre():
    usuarios = get_usuarios()
    return render_template('sobre.html', usuarios=usuarios)


@app.route('/contato/')
def contato():
    return render_template('contato.html')


# paginas adm


@app.route('/admin/')
def adm_index():
    return render_template('admin/index.html')


@app.route('/admin/novo-post/')
def adm_novo_post():
    return render_template('admin/novo-post.html')


@app.route('/admin/usuarios/')
def adm_usuarios():
    return str(get_usuarios())


@app.route('/admin/login/')
def adm_login():
    return render_template('admin/login.html')


if __name__ == '__main__':
    app.run()
