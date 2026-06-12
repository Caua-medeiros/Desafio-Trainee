import re
from validate_docbr import CPF
from rest_framework import serializers
from loja.models import Clientes, Logistas, Login, Produtos, Estoque

cpf_validator = CPF()

class ClientesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clientes
        fields = '__all__'

    def validate(self, dados):
        errors = {}
        cpf = dados.get('cpf')
        telefone = dados.get('telefone')
        nome = dados.get('nome_completo')

        if cpf is not None:
            
            if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
                errors['cpf'] = 'O CPF deve seguir o modelo: 000.000.000-00'
            
            elif not cpf_validator.validate(cpf):
                errors['cpf'] = 'Este CPF é inválido. Digite um CPF real.'

        if telefone is not None:
            if not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', telefone):
                errors['telefone'] = 'O telefone deve seguir o modelo: (84) 99999-1111'

        if nome is not None:
            if not re.match(r'^\s*[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*\s*$', nome):
                errors['nome_completo'] = 'O nome deve conter apenas letras e espaços.'

        if errors:
            raise serializers.ValidationError(errors)
        return dados


class LogistasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logistas
        fields = '__all__'

    def validate(self, dados):
        errors = {}
        cpf = dados.get('cpf')
        telefone = dados.get('telefone')
        nome = dados.get('nome_completo')

        if cpf is not None:
           
            if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
                errors['cpf'] = 'O CPF deve seguir o modelo: 000.000.000-00'

            elif not cpf_validator.validate(cpf):
                errors['cpf'] = 'Este CPF é inválido. Digite um CPF real.'

        if telefone is not None:
            if not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', telefone):
                errors['telefone'] = 'O telefone deve seguir o modelo: (84) 99999-1111'

        if nome is not None:
            if not re.match(r'^\s*[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*\s*$', nome):
                errors['nome_completo'] = 'O nome deve conter apenas letras e espaços.'

        if errors:
            raise serializers.ValidationError(errors)
        return dados


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