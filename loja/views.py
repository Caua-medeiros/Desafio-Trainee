from loja.models import Cadastro_Clientes, Cadastro_Logistas, Login, Cadastro_Produtos
from loja.serializers import CadastroClientesSerializer, CadastroLogistasSerializer, LoginSerializer, CadastroProdutosSerializer
from rest_framework import viewsets

class CadastroClientesViewSet(viewsets.ModelViewSet):
    queryset = Cadastro_Clientes.objects.all()
    serializer_class = CadastroClientesSerializer

class CadastroLogistasViewSet(viewsets.ModelViewSet):
    queryset = Cadastro_Logistas.objects.all()
    serializer_class = CadastroLogistasSerializer

class LoginViewSet(viewsets.ModelViewSet):
    queryset = Login.objects.all()
    serializer_class = LoginSerializer

class CadastroProdutosViewSet(viewsets.ModelViewSet):   
    queryset = Cadastro_Produtos.objects.all()
    serializer_class = CadastroProdutosSerializer   

