from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image

from itens.models import Comentario, HistoricoStatus, Item, Reivindicacao

SENHA = 'SenhaTeste123!'

ITENS = [
    ('encontrado', 'Pendrive Kingston 32GB', 'Pendrive preto encontrado sobre a bancada.', 'eletronicos', 'Laboratório de Informática', 'verificacao', (60, 60, 60)),
    ('perdido', 'Carteira de couro marrom', 'Carteira com documentos pessoais dentro.', 'documentos', 'Biblioteca', 'perdido', (139, 90, 43)),
    ('encontrado', 'Casaco azul marinho', 'Casaco de moletom tamanho M, esquecido na sala.', 'vestuario', 'Bloco A, sala 102', 'verificacao', (30, 50, 110)),
    ('perdido', 'Calculadora científica', 'Calculadora Casio fx-82 com nome gravado atrás.', 'eletronicos', 'Bloco B', 'perdido', (90, 90, 100)),
    ('encontrado', 'Carteirinha de estudante', 'Carteirinha da UTFPR encontrada no corredor.', 'documentos', 'Corredor do Bloco C', 'devolvido', (200, 200, 200)),
    ('encontrado', 'Garrafa térmica preta', 'Garrafa térmica de 500 ml com adesivos.', 'outros', 'Cantina', 'verificacao', (20, 20, 20)),
    ('perdido', 'Fone de ouvido sem fio', 'Fone branco com estojo de carregamento.', 'eletronicos', 'Estacionamento', 'arquivado', (230, 230, 230)),
    ('encontrado', 'Chaveiro com três chaves', 'Chaveiro com um pingente de ursinho.', 'outros', 'Ginásio', 'encontrado', (180, 150, 40)),
]


def criar_usuario(email, nome, admin):
    usuario, criado = User.objects.get_or_create(
        username=email,
        defaults={'email': email, 'first_name': nome, 'is_staff': admin, 'is_superuser': admin},
    )
    if criado:
        usuario.set_password(SENHA)
        usuario.save()
    return usuario


def criar_imagem(cor, nome):
    imagem = Image.new('RGB', (400, 300), cor)
    buffer = BytesIO()
    imagem.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=nome)


def criar_item(dados, autor):
    tipo, titulo, descricao, categoria, local, status, cor = dados
    item = Item(
        tipo=tipo, titulo=titulo, descricao=descricao,
        categoria=categoria, local=local, status=status, autor=autor,
    )
    item.foto = criar_imagem(cor, f'{titulo[:15]}.png')
    item.save()

    status_inicial = 'perdido' if tipo == 'perdido' else 'verificacao'
    HistoricoStatus.objects.create(
        item=item, status_anterior='', status_novo=status_inicial,
        alterado_por=autor, observacao='Item cadastrado',
    )

    if status != status_inicial:
        HistoricoStatus.objects.create(
            item=item, status_anterior=status_inicial, status_novo=status,
            alterado_por=autor, observacao='Status alterado (dados de exemplo)',
        )
    return item


class Command(BaseCommand):
    help = 'Cria usuários e itens de exemplo'

    def handle(self, *args, **options):
        if Item.objects.exists():
            self.stdout.write('Seed já executado. Nada a fazer.')
            return

        admin = criar_usuario('admin@utfpr.br', 'Administrador', True)
        usuario = criar_usuario('usuario@utfpr.br', 'Usuário', False)

        itens = []
        for numero, dados in enumerate(ITENS):
            autor = usuario if numero % 2 == 0 else admin
            itens.append(criar_item(dados, autor))

        Comentario.objects.create(item=itens[0], autor=admin, texto='Qual a cor da capa do pendrive?')
        Comentario.objects.create(item=itens[0], autor=usuario, texto='É preto, com uma etiqueta no lado.')
        Comentario.objects.create(item=itens[1], autor=usuario, texto='Vou procurar na biblioteca amanhã.')

        Reivindicacao.objects.create(
            item=itens[0], autor=admin,
            prova='O pendrive tem uma pasta chamada TCC com meu nome.',
        )

        self.stdout.write(self.style.SUCCESS('Seed concluído: 2 usuários e 8 itens criados.'))