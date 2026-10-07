from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import login
from .forms import CadastroForm

def cadastro(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(request, 'Conta criada com sucesso!')
            return redirect ('home')
        else: 
            form = CadastroForm()
        return render(request, 'registration/cadastro.html', {'form': form})

