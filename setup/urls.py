from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from loja.views import (
    ClientesViewSet, LogistasViewSet, ProdutosViewSet, EstoqueViewSet,
    GerenciamentoEstoqueView, AuthRegisterView, ForgotPasswordView, ResetPasswordView
)


schema_view = get_schema_view(
    openapi.Info(
        title="API Desafio Trainee EJECT",
        default_version='v1',
        description="Documentação da API da Loja",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = DefaultRouter()
router.register(r'clientes', ClientesViewSet, basename='clientes')
router.register(r'lojistas', LogistasViewSet, basename='lojistas')
router.register(r'produtos', ProdutosViewSet, basename='produtos')
router.register(r'estoque', EstoqueViewSet, basename='estoque')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    
    path('api/', include(router.urls)),
    
    
    path('api/register/', AuthRegisterView.as_view(), name='auth_register'),
    path('api/produtos/<int:product_id>/estoque/', GerenciamentoEstoqueView.as_view(), name='gerenciamento_estoque'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
   
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]