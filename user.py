class Usuario:
    def __init__(self, id=None, nome=None, sobrenome=None, email=None,
                 senha=None, fb=None, twitter=None, git=None, linkedin=None,
                 pesquisa=None, bio=None):
        self.id = id
        self.nome = nome
        self.sobrenome = sobrenome
        self.email = email
        self.senha = senha
        self.facebook = fb
        self.twitter = twitter
        self.github = git
        self.linkedin = linkedin
        self.pesquisa = pesquisa
        self.bio = bio

    @property
    def nome_completo(self):
        return self.nome + ' ' + self.sobrenome
