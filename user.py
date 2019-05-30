def cria_usuario(attr):
    return Usuario(id=attr[0], nome=attr[1], snome=attr[2], fb=attr[3],
                   insta=attr[4], git=attr[5], linkedin=attr[6], bio=attr[7],
                   pesq=attr[8], foto=attr[9], email=attr[10], senha=attr[11])


class Usuario:
    def __init__(self, id=None, nome=None, snome=None, fb=None, insta=None,
                 git=None, linkedin=None, bio=None, pesq=None, foto=None,
                 email=None, senha=None):
        self.id = id
        self.nome = nome
        self.sobrenome = snome
        self.facebook = fb
        self.instagram = insta
        self.github = git
        self.linkedin = linkedin
        self.descricao = bio
        self.pesquisa = pesq
        self.diretorio_foto = foto
        self.email = email
        self.senha = senha

    @property
    def nome_completo(self):
        return self.nome + ' ' + self.sobrenome
