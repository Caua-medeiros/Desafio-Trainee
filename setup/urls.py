from django.contrib import admin
from django.urls import path,include
from loja.views import ClientesViewSet, LogistasViewSet, LoginViewSet, ProdutosViewSet, EstoqueViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('clientes', ClientesViewSet, basename='clientes')
router.register('logistas', LogistasViewSet, basename='logistas')
router.register('login', LoginViewSet, basename='login')
router.register('produtos', ProdutosViewSet, basename='produtos')
router.register('estoque', EstoqueViewSet, basename='estoque')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)), 
]
