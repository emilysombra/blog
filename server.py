from flask import Flask, render_template

app = Flask(__name__)


# paginas user


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sobre/')
def sobre():
    return render_template('sobre.html')


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


@app.route('/admin/login/')
def adm_login():
    return render_template('admin/login.html')


if __name__ == '__main__':
    app.run()
