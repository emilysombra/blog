def cria_ad(attr):
    return Ad(i=attr[0], titulo=attr[1], img=attr[2], url=attr[3])


class Ad:
    def __init__(self, i=None, titulo=None, img=None, url=None):
        self.id = i
        self.titulo = titulo
        self.diretorio_foto = img
        self.link = url

    def __str__(self):
        return self.titulo + ': ' + self.link
