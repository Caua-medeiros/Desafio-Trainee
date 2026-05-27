from rest_framework import serializers
from loja.models import Cadastro_Clientes, Cadastro_Logistas, Login, Cadastro_Produtos

class CadastroClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cadastro_Clientes
        fields = '__all__'

class CadastroLogistasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cadastro_Logistas
        fields = '__all__'

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = '__all__'

class CadastroProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cadastro_Produtos
        fields = '__all__'