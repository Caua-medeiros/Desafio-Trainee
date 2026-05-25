from django.contrib import admin
from django.urls import path
from loja.views import clientes

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', clientes)
]
