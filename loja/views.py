from loja.models import Clientes, Logistas, Login, Produtos, Estoque
from loja.serializers import ClientesSerializer, LogistasSerializer, LoginSerializer, ProdutosSerializer, EstoqueSerializer
from rest_framework import viewsets, generics
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Clientes.objects.all().order_by('id')
    serializer_class = ClientesSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

class LogistasViewSet(viewsets.ModelViewSet):
    queryset = Logistas.objects.all().order_by('id')
    serializer_class = LogistasSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

class LoginViewSet(viewsets.ModelViewSet):
    queryset = Login.objects.all().order_by('id')
    serializer_class = LoginSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

class ProdutosViewSet(viewsets.ModelViewSet):
    queryset = Produtos.objects.all().order_by('id')
    serializer_class = ProdutosSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


class EstoqueViewSet(viewsets.ModelViewSet):
    queryset = Estoque.objects.all().order_by('id')
    serializer_class = EstoqueSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]