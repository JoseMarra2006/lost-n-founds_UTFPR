from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('novo/', views.novo_item, name='novo_item'),
    path('item/<int:id>/', views.detalhe_item, name='detalhe_item'),
    path('item/<int:id>/editar/', views.editar_item, name='editar_item'),
    path('item/<int:id>/excluir/', views.excluir_item, name='excluir_item'),
    path('item/<int:id>/status/', views.alterar_status, name='alterar_status'),
    path('item/<int:id>/comentar/', views.comentar, name='comentar'),
    path('comentario/<int:id>/excluir/', views.excluir_comentario, name='excluir_comentario'),
    path('item/<int:id>/reivindicar/', views.reivindicar, name='reivindicar'),
    path('reivindicacoes/', views.lista_reivindicacoes, name='lista_reivindicacoes'),
    path('reivindicacao/<int:id>/decidir/', views.decidir_reivindicacao, name='decidir_reivindicacao'),
]