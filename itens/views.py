from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from .forms import ItemForm
from .models import CATEGORIAS, STATUS, HistoricoStatus, Item


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

@login_required
def novo_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.autor = request.user
            if item.tipo == 'encontrado':
                item.status = 'verificacao'
            else:
                item.status = 'perdido'
            item.save()
            HistoricoStatus.objects.create(
                item=item,
                status_anterior='',
                status_novo=item.status,
                alterado_por=request.user,
                observacao='Item cadastrado',
            )
            messages.success(request, 'Item cadastrado com sucesso!')
            return redirect('home')
    else:
        form = ItemForm()
    return render(request, 'novo_item.html', {'form': form})