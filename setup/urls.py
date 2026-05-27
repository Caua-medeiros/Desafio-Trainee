from django.contrib import admin
from django.urls import path,include
from loja.views import CadastroClientesViewSet, CadastroLogistasViewSet, LoginViewSet, CadastroProdutosViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('clientes', CadastroClientesViewSet, basename='clientes')
router.register('logistas', CadastroLogistasViewSet, basename='logistas')
router.register('login', LoginViewSet, basename='login')
router.register('produtos', CadastroProdutosViewSet, basename='produtos')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls))
]
