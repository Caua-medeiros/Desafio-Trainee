import re
from rest_framework import serializers
from loja.models import Clientes, Logistas, Login, Produtos, Estoque

class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = '__all__'

    def validate_cpf(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError('O CPF deve conter exatamente 11 dígitos numéricos.')
        return value

    def validate_telefone(self, value):
        digits = ''.join(filter(str.isdigit, value))
        if len(digits) < 10 or len(digits) > 13:
            raise serializers.ValidationError('O telefone deve ter entre 10 e 13 dígitos numéricos.')
        return value

    def validate_nome_completo(self, value):
        if not re.match(r'^[A-Za-zÀ-ÿ\s]+$', value):
            raise serializers.ValidationError('O nome deve conter apenas letras e espaços.')
        return value
    

class LogistasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logistas
        fields = '__all__'

    def validate_cpf(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError('O CPF deve conter exatamente 11 dígitos numéricos.')
        return value

    def validate_telefone(self, value):
        digits = ''.join(filter(str.isdigit, value))
        if len(digits) < 10 or len(digits) > 13:
            raise serializers.ValidationError('O telefone deve ter entre 10 e 13 dígitos numéricos.')
        return value

    def validate_nome_completo(self, value):
        if not re.match(r'^[A-Za-zÀ-ÿ\s]+$', value):
            raise serializers.ValidationError('O nome deve conter apenas letras e espaços.')
        return value


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = '__all__'


class ProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produtos
        fields = '__all__'


class EstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estoque
        fields = '__all__'