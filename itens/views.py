from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EditarItemForm, ItemForm, StatusForm
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

def detalhe_item(request, id):
    item = get_object_or_404(Item, id=id)
    form_status = StatusForm(initial={'status': item.status})
    contexto = {
        'item': item,
        'form_status': form_status,
        'historico': item.historico.all(),
    }
    return render(request, 'detalhe_item.html', contexto)


@login_required
def editar_item(request, id):
    item = get_object_or_404(Item, id=id)
    if item.autor != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        form = EditarItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item atualizado com sucesso!')
            return redirect('detalhe_item', id=item.id)
    else:
        form = EditarItemForm(instance=item)
    return render(request, 'editar_item.html', {'form': form, 'item': item})


@login_required
def excluir_item(request, id):
    item = get_object_or_404(Item, id=id)
    if item.autor != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item excluído.')
        return redirect('home')
    return render(request, 'excluir_item.html', {'item': item})


@login_required
def alterar_status(request, id):
    item = get_object_or_404(Item, id=id)
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST':
        form = StatusForm(request.POST)
        if form.is_valid():
            novo = form.cleaned_data['status']
            if novo != item.status:
                HistoricoStatus.objects.create(
                    item=item,
                    status_anterior=item.status,
                    status_novo=novo,
                    alterado_por=request.user,
                    observacao=form.cleaned_data['observacao'],
                )
                item.status = novo
                item.save()
                messages.success(request, 'Status atualizado.')
            else:
                messages.warning(request, 'O item já está com este status.')
    return redirect('detalhe_item', id=item.id)