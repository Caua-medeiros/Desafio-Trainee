from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from loja.views import (
    AuthRegisterView,
    ForgotPasswordView,
    ResetPasswordView,
    ClientesViewSet,
    LogistasViewSet,
    ProdutosViewSet,
    EstoqueViewSet,
    VariaçãoDetalheView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'clientes', ClientesViewSet, basename='clientes')
router.register(r'logistas', LogistasViewSet, basename='logistas')
router.register(r'products', ProdutosViewSet, basename='products')
router.register(r'variations', EstoqueViewSet, basename='variations')

schema_view = get_schema_view(
    openapi.Info(
        title="API Desafio Trainee EJECT",
        default_version='v1',
        description="Documentação da API da Loja",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

schema_view.security_definitions = {
    'Bearer': {
        'type': 'apiKey',
        'name': 'Authorization',
        'in': 'header',
        'description': "Insira o token JWT desta forma: Bearer <seu_token>"
    }
}

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Endpoints de Autenticação Manual (UC01 / UC02)
    path('api/auth/register/', AuthRegisterView.as_view(), name='auth_register'),
    path('api/auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('api/auth/reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    
    # Endpoints do SimpleJWT (Login)
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # UC04: Rota Aninhada Obrigatória para Adicionar/Listar Variações diretamente por Produto
    path('api/products/<int:product_id>/variations/', EstoqueViewSet.as_view({'post': 'create', 'get': 'list'}), name='product_variations_list_create'),
    
    # UC04: Rotas Manuais para Edição/Exclusão de Variações de Estoque específicas
    path('api/variations/<int:pk>/', VariaçãoDetalheView.as_view(), name='variation_detail'),
    
    # ViewSets Gerais
    path('api/', include(router.urls)),
]