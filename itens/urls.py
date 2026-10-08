from django.http import HttpResponse
from django.urls import path

from . import views


def provisoria(request, id=None):
    return HttpResponse('Página em construção.')


urlpatterns = [
    path('', views.home, name='home'),
    path('novo/', views.novo_item, name='novo_item'),
    path('item/<int:id>/', provisoria, name='detalhe_item'),
]