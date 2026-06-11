from django.contrib import admin
from django.urls import path,include
from loja.views import ClientesViewSet, LogistasViewSet, LoginViewSet, ProdutosViewSet, EstoqueViewSet
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Documentação API",
      default_version='v1',
      description="Documentação da API da loja",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)

router = routers.DefaultRouter()
router.register('clientes', ClientesViewSet, basename='clientes')
router.register('logistas', LogistasViewSet, basename='logistas')
router.register('login', LoginViewSet, basename='login')
router.register('produtos', ProdutosViewSet, basename='produtos')
router.register('estoque', EstoqueViewSet, basename='estoque')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)), 
    path('swagger.<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),   
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
