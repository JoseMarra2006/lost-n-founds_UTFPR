from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (ComentarioForm, EditarItemForm, ItemForm, ReivindicacaoForm, StatusForm)
from .models import (CATEGORIAS, STATUS, Comentario, HistoricoStatus, Item, Reivindicacao)

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
    pode_reivindicar = item.tipo == 'encontrado' and item.status in ('encontrado', 'verificacao')
    contexto = {
        'item': item,
        'form_status': StatusForm(initial={'status': item.status}),
        'historico': item.historico.all(),
        'comentarios': item.comentarios.all(),
        'pode_reivindicar': pode_reivindicar,
        'form_comentario': ComentarioForm(),
        'form_reivindicacao': ReivindicacaoForm(),
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

@login_required
def comentar(request, id):
    item = get_object_or_404(Item, id=id)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.item = item
            comentario.autor = request.user
            comentario.save()
            messages.success(request, 'Comentário adicionado.')
        else:
            messages.error(request, 'Não foi possível salvar o comentário. Escreva um texto de até 500 caracteres.')
    return redirect('detalhe_item', id=item.id)


@login_required
def excluir_comentario(request, id):
    comentario = get_object_or_404(Comentario, id=id)
    if not request.user.is_staff:
        raise PermissionDenied
    item_id = comentario.item.id
    if request.method == 'POST':
        comentario.delete()
        messages.success(request, 'Comentário removido.')
    return redirect('detalhe_item', id=item_id)


@login_required
def reivindicar(request, id):
    item = get_object_or_404(Item, id=id)
    if item.tipo != 'encontrado' or item.status not in ('encontrado', 'verificacao'):
        messages.error(request, 'Este item não pode ser reivindicado.')
        return redirect('detalhe_item', id=item.id)
    if request.method == 'POST':
        ja_pendente = Reivindicacao.objects.filter(
            item=item, autor=request.user, situacao='pendente'
        ).exists()
        if ja_pendente:
            messages.warning(request, 'Você já tem uma reivindicação pendente para este item.')
            return redirect('detalhe_item', id=item.id)
        form = ReivindicacaoForm(request.POST, request.FILES)
        if form.is_valid():
            reivindicacao = form.save(commit=False)
            reivindicacao.item = item
            reivindicacao.autor = request.user
            reivindicacao.save()
            messages.success(request, 'Reivindicação enviada. Aguarde a análise do administrador.')
        else:
            messages.error(request, 'Não foi possível enviar a reivindicação. Descreva a prova e use uma imagem JPG ou PNG de até 5 MB.')
    return redirect('detalhe_item', id=item.id)


@login_required
def lista_reivindicacoes(request):
    if not request.user.is_staff:
        raise PermissionDenied
    pendentes = Reivindicacao.objects.filter(situacao='pendente').select_related('item', 'autor')
    return render(request, 'reivindicacoes.html', {'pendentes': pendentes})


@login_required
def decidir_reivindicacao(request, id):
    reivindicacao = get_object_or_404(Reivindicacao, id=id)
    if not request.user.is_staff:
        raise PermissionDenied
    if request.method == 'POST' and reivindicacao.situacao == 'pendente':
        item = reivindicacao.item
        acao = request.POST.get('acao')
        if acao == 'aprovar':
            HistoricoStatus.objects.create(
                item=item,
                status_anterior=item.status,
                status_novo='devolvido',
                alterado_por=request.user,
                observacao='Reivindicação aprovada',
            )
            item.status = 'devolvido'
            item.save()
            reivindicacao.situacao = 'aprovada'
            reivindicacao.save()
            messages.success(request, 'Reivindicação aprovada. Item marcado como devolvido.')
        elif acao == 'recusar':
            HistoricoStatus.objects.create(
                item=item,
                status_anterior=item.status,
                status_novo=item.status,
                alterado_por=request.user,
                observacao='Reivindicação recusada',
            )
            reivindicacao.situacao = 'recusada'
            reivindicacao.save()
            messages.success(request, 'Reivindicação recusada.')
    return redirect('lista_reivindicacoes')