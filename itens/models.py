from django.contrib.auth.models import User
from django.db import models

CATEGORIAS = [
    ('eletronicos', 'Eletrônicos'),
    ('documentos', 'Documentos'),
    ('vestuario', 'Vestuário'),
    ('outros', 'Outros'),
]


TIPOS = [
    ('perdido', 'Perdido'),
    ('encontrado', 'Encontrado'),
]

STATUS = [
    ('perdido', 'Perdido'),
    ('encontrado', 'Encontrado'),
    ('verificacao', 'Em verificação'),
    ('devolvido', 'Devolvido'),
    ('arquivado', 'Arquivado'),
]

SITUACOES = [
    ('pendente', 'Pendente'),
    ('aprovada', 'Aprovada'),
    ('recusada', 'Recusada'),
]


class Item(models.Model):
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=100)
    descricao = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    local = models.CharField(max_length=150, blank=True)
    foto = models.ImageField(upload_to='itens/')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itens')
    status = models.CharField(max_length=20, choices=STATUS)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return self.titulo


class Comentario(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField(max_length=500)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f'Comentário de {self.autor.first_name} em {self.item.titulo}'


class Reivindicacao(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='reivindicacoes')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    prova = models.TextField(max_length=500)
    imagem = models.ImageField(upload_to='provas/', blank=True)
    situacao = models.CharField(max_length=20, choices=SITUACOES, default='pendente')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-criado_em']

    def __str__(self):
        return f'Reivindicação de {self.autor.first_name} para {self.item.titulo}'


class HistoricoStatus(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='historico')
    status_anterior = models.CharField(max_length=20, blank=True)
    status_novo = models.CharField(max_length=20)
    alterado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    observacao = models.CharField(max_length=200, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['criado_em']

    def __str__(self):
        return f'{self.item.titulo}: {self.status_anterior} -> {self.status_novo}'

