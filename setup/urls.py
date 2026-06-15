from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter

from loja.views import (
    RegistroUsuarioView, SolicitacaoRecuperacaoSenhaView, ConfirmacaoRecuperacaoSenhaView,
    ProdutoViewSet, VariacaoEstoqueViewSet, DetalheVariacaoView, MensagemContatoView, 
    CarrinhoCompraView, ItemCarrinhoViewSet, CheckoutView, PedidoViewSet, MetodoPagamentoViewSet
)

# Roteador mapeado exatamente conforme as especificações exigidas de endpoints
router = DefaultRouter(trailing_slash=False)
router.register(r'products', ProdutoViewSet, basename='products')
router.register(r'cart/items', ItemCarrinhoViewSet, basename='cart-items')
router.register(r'orders', PedidoViewSet, basename='orders')
router.register(r'payments', MetodoPagamentoViewSet, basename='payments')

schema_view = get_schema_view(
    openapi.Info(title="API New Style E-Commerce - EJECT", default_version='v1'),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # UC01 & UC02 - Autenticação e Recuperação de Senha (Exigência exata do edital)
    path('auth/register', RegistroUsuarioView.as_view(), name='auth_register'),
    path('auth/login', TokenObtainPairView.as_view(), name='auth_login'),
    path('auth/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/forgot-password', SolicitacaoRecuperacaoSenhaView.as_view(), name='forgot_password'),
    path('auth/reset-password', ConfirmacaoRecuperacaoSenhaView.as_view(), name='reset_password'),
    
    # UC04 - Variações de Produto
    path('products/<int:id_produto>/variacoes', VariacaoEstoqueViewSet.as_view({'post': 'create', 'get': 'list'}), name='product_variations'),
    path('variations/<int:pk>', DetalheVariacaoView.as_view(), name='variation_detail'),
    
    # UC06 - Envio de Email de Contato
    path('contact/email', MensagemContatoView.as_view(), name='contact_email'),
    
    # UC07 - Detalhe do Carrinho Geral
    path('cart', CarrinhoCompraView.as_view(), name='cart_detail'),
    
    # UC08 - Realização de Pedido (Checkout)
    path('orders/checkout', CheckoutView.as_view(), name='orders_checkout'),
    
    # Inclusão dos endpoints via Router do DRF (/products, /cart/items, /orders, /payments)
    path('', include(router.urls)),
]