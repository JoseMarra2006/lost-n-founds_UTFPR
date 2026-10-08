from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Item


def item_para_dict(item, request):
    return {
        'id': item.id,
        'titulo': item.titulo,
        'descricao': item.descricao,
        'tipo': item.tipo,
        'categoria': item.categoria,
        'status': item.status,
        'local': item.local,
        'foto': request.build_absolute_uri(item.foto.url),
        'autor': item.autor.first_name or item.autor.username,
        'criado_em': item.criado_em.isoformat(),
    }


@require_GET
def lista_itens(request):
    itens = Item.objects.select_related('autor').all()

    status = request.GET.get('status', '')
    categoria = request.GET.get('category', '') or request.GET.get('categoria', '')

    if status:
        itens = itens.filter(status=status)
    if categoria:
        itens = itens.filter(categoria=categoria)

    paginador = Paginator(itens, 10)
    pagina = paginador.get_page(request.GET.get('page'))

    dados = {
        'total': paginador.count,
        'pagina': pagina.number,
        'total_paginas': paginador.num_pages,
        'resultados': [item_para_dict(item, request) for item in pagina],
    }
    return JsonResponse(dados)


@require_GET
def detalhe_item(request, id):
    try:
        item = Item.objects.select_related('autor').get(id=id)
    except Item.DoesNotExist:
        return JsonResponse({'erro': 'Item não encontrado.'}, status=404)

    dados = item_para_dict(item, request)
    dados['comentarios'] = [
        {
            'id': c.id,
            'autor': c.autor.first_name or c.autor.username,
            'texto': c.texto,
            'criado_em': c.criado_em.isoformat(),
        }
        for c in item.comentarios.select_related('autor')
    ]
    return JsonResponse(dados)