from django.core.paginator import Paginator
from django.shortcuts import render

from .models import CATEGORIAS, STATUS, Item


def home(request):
    categoria = request.GET.get('categoria', '')
    status = request.GET.get('status', '')

    itens = Item.objects.all()

    if categoria:
        itens = itens.filter(categoria=categoria)
    if status:
        itens = itens.filter(status=status)

    paginador = Paginator(itens, 6)
    pagina = paginador.get_page(request.GET.get('page'))

    contexto = {
        'pagina': pagina,
        'categorias': CATEGORIAS,
        'status_lista': STATUS,
        'categoria_atual': categoria,
        'status_atual': status,
    }
    return render(request, 'home.html', contexto)