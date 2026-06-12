from loja.models import Clientes, Logistas, Login, Produtos, Estoque
from loja.serializers import ClientesSerializer, LogistasSerializer, LoginSerializer, ProdutosSerializer, EstoqueSerializer
from rest_framework import viewsets, generics, filters
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend

class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Clientes.objects.all().order_by('id')
    serializer_class = ClientesSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_completo']
    search_fields = ['nome_completo', 'email']

class LogistasViewSet(viewsets.ModelViewSet):
    queryset = Logistas.objects.all().order_by('id')
    serializer_class = LogistasSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_completo']
    search_fields = ['nome_completo', 'email']

class LoginViewSet(viewsets.ModelViewSet):
    queryset = Login.objects.all().order_by('id')
    serializer_class = LoginSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

class ProdutosViewSet(viewsets.ModelViewSet):
    queryset = Produtos.objects.all().order_by('id')
    serializer_class = ProdutosSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_produto', 'preco']
    search_fields = ['nome_produto']


class EstoqueViewSet(viewsets.ModelViewSet):
    queryset = Estoque.objects.all().order_by('id')
    serializer_class = EstoqueSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id']
    search_fields = ['produtos__nome_produto', 'tamanho']