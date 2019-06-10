def cria_post(attr):
    return Post(i=attr[0], titulo=attr[1], data=attr[2], img=attr[3],
                autor=attr[4], texto=attr[5], ativo=attr[6], url=attr[7])


class Post:
    def __init__(self, i=None, titulo=None, data=None, img=None, autor=None,
                 texto=None, ativo=None, url=None):
        self.id = i
        self.titulo = titulo
        self.data = data
        self.imagem = img
        self.autor = autor
        self.texto = texto
        self.ativo = ativo
        self.url = url
