import re
from validate_docbr import CPF
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from loja.models import Clientes, Logistas, Produtos, Estoque

cpf_validator = CPF()

def validar_campos_comuns(dados, instancia_id=None, tipo_usuario=None):
    errors = {}
    cpf = dados.get('cpf')
    telefone = dados.get('telefone')
    nome = dados.get('nome_completo')
    email = dados.get('email')

    
    if cpf:
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
            errors['cpf'] = 'O CPF deve seguir o modelo: 000.000.000-00'
        elif not cpf_validator.validate(cpf):
            errors['cpf'] = 'Este CPF é inválido. Digite um CPF real.'
        else:
            if tipo_usuario == 'cliente':
                cpf_cliente_existe = Clientes.objects.filter(cpf=cpf).exclude(id=instancia_id).exists()
                cpf_lojista_existe = Logistas.objects.filter(cpf=cpf).exists()
            elif tipo_usuario == 'lojista':
                cpf_cliente_existe = Clientes.objects.filter(cpf=cpf).exists()
                cpf_lojista_existe = Logistas.objects.filter(cpf=cpf).exclude(id=instancia_id).exists()
            else:
                cpf_cliente_existe = Clientes.objects.filter(cpf=cpf).exists()
                cpf_lojista_existe = Logistas.objects.filter(cpf=cpf).exists()

            if cpf_cliente_existe or cpf_lojista_existe:
                errors['cpf'] = 'Este CPF já está cadastrado por outro usuário.'

    
    if telefone:
        if not re.match(r'^\(\d{2}\)\s\d{4,5}-\d{4}$', telefone):
            errors['telefone'] = 'O telefone deve seguir o modelo: (84) 99999-1111'
        else:
            if tipo_usuario == 'cliente':
                tel_cliente_existe = Clientes.objects.filter(telefone=telefone).exclude(id=instancia_id).exists()
                tel_lojista_existe = Logistas.objects.filter(telefone=telefone).exists()
            elif tipo_usuario == 'lojista':
                tel_cliente_existe = Clientes.objects.filter(telefone=telefone).exists()
                tel_lojista_existe = Logistas.objects.filter(telefone=telefone).exclude(id=instancia_id).exists()
            else:
                tel_cliente_existe = Clientes.objects.filter(telefone=telefone).exists()
                tel_lojista_existe = Logistas.objects.filter(telefone=telefone).exists()

            if tel_cliente_existe or tel_lojista_existe:
                errors['telefone'] = 'Este telefone já está cadastrado por outro usuário.'

    
    if nome and not re.match(r'^\s*[A-Za-zÀ-ÿ]+(?:\s+[A-Za-zÀ-ÿ]+)*\s*$', nome):
        errors['nome_completo'] = 'O nome deve conter apenas letras e espaços.'

    
    if email:
        user_existente = User.objects.filter(email=email).first()
        if user_existente:
            if instancia_id and tipo_usuario:
                # Recupera o usuário dono do perfil que está sofrendo o update
                model_atual = Clientes if tipo_usuario == 'cliente' else Logistas
                perfil_atual = model_atual.objects.filter(id=instancia_id).first()
                if perfil_atual and perfil_atual.user != user_existente:
                    errors['email'] = 'Não deve permitir email duplicado.'
            else:
                errors['email'] = 'Não deve permitir email duplicado.'

    if errors:
        raise serializers.ValidationError(errors)
    return dados


class ClientesSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Clientes
        fields = ['id', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep', 'email']

    def validate(self, dados):
        instancia_id = self.instance.id if self.instance else None
        return validar_campos_comuns(dados, instancia_id=instancia_id, tipo_usuario='cliente')


class LogistasSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Logistas
        fields = ['id', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep', 'email']

    def validate(self, dados):
        instancia_id = self.instance.id if self.instance else None
        return validar_campos_comuns(dados, instancia_id=instancia_id, tipo_usuario='lojista')


class EstoqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estoque
        fields = ['id', 'quantidade', 'tamanho', 'cor']


class ProdutosSerializer(serializers.ModelSerializer):
    variacoes = EstoqueSerializer(many=True, read_only=True)

    class Meta:
        model = Produtos
        fields = ['id', 'nome_produto', 'descricao', 'preco', 'categoria', 'ativo', 'variacoes']


class RegisterSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['cliente', 'lojista'])
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True)
    nome_completo = serializers.CharField()
    data_nascimento = serializers.DateField()
    telefone = serializers.CharField()
    cpf = serializers.CharField()
    cep = serializers.CharField()

    def validate(self, dados):
        
        return validar_campos_comuns(dados, instancia_id=None, tipo_usuario=None)

    def create(self, validated_data):
        role = validated_data.pop('role')
        senha = validated_data.pop('senha')
        email = validated_data['email']

        with transaction.atomic():
            user = User.objects.create(
                username=email,
                email=email,
                password=make_password(senha)
            )

            if role == 'cliente':
                perfil = Clientes.objects.create(user=user, **validated_data)
            else:
                perfil = Logistas.objects.create(user=user, **validated_data)

        return 
    

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)
    nova_senha = serializers.CharField(min_length=8, write_only=True)