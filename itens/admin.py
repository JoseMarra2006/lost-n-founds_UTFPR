from django.contrib import admin

from .models import Comentario, HistoricoStatus, Item, Reivindicacao

admin.site.register(Item)
admin.site.register(Comentario)
admin.site.register(Reivindicacao)
admin.site.register(HistoricoStatus)
