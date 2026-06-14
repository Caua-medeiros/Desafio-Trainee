import re
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from loja.models import Clientes, Logistas, Produtos, Estoque

# ==================== AUXILIARES DE VALIDAÇÃO ====================

def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False
    return True

def validar_campos_comuns(dados, instancia_id=None, tipo_usuario=None):
    erros = {}
    cpf = dados.get('cpf')
    telefone = dados.get('telefone')
    
    # Validação de formato e unicidade de CPF por Role
    if cpf:
        if not validar_cpf(cpf):
            erros['cpf'] = "CPF inválido."
        
        if tipo_usuario == 'cliente' or dados.get('role') == 'cliente':
            query = Clientes.objects.filter(cpf=cpf)
            if instancia_id:
                query = query.exclude(id=instancia_id)
            if query.exists():
                erros['cpf'] = "Este CPF já está cadastrado como cliente."
        elif tipo_usuario == 'lojista' or dados.get('role') == 'lojista':
            query = Logistas.objects.filter(cpf=cpf)
            if instancia_id:
                query = query.exclude(id=instancia_id)
            if query.exists():
                erros['cpf'] = "Este CPF já está cadastrado como lojista."

    if erros:
        raise serializers.ValidationError(erros)
    return dados


# ==================== SERIALIZERS DE CONTA ====================

class RegisterSerializer(serializers.Serializer):
    ROLE_CHOICES = (
        ('cliente', 'Cliente'),
        ('lojista', 'Lojista'),
    )
    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True)
    nome_completo = serializers.CharField(max_length=100)
    data_nascimento = serializers.DateField()
    telefone = serializers.CharField(max_length=15)
    cpf = serializers.CharField(max_length=14)
    cep = serializers.CharField(max_length=9)

    def validate(self, dados):
        email = dados.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Este e-mail já está cadastrado."})
            
        return validar_campos_comuns(dados)

    def create(self, validated_data):
        role = validated_data.pop('role')
        senha = validated_data.pop('senha')
        email = validated_data.pop('email')

        user = User.objects.create(
            username=email,
            email=email,
            password=make_password(senha)
        )

        if role == 'cliente':
            return Clientes.objects.create(
                user=user,
                nome_completo=validated_data.get('nome_completo'),
                data_nascimento=validated_data.get('data_nascimento'),
                telefone=validated_data.get('telefone'),
                cpf=validated_data.get('cpf'),
                cep=validated_data.get('cep')
            )
        else:
            return Logistas.objects.create(
                user=user,
                nome_completo=validated_data.get('nome_completo'),
                data_nascimento=validated_data.get('data_nascimento'),
                telefone=validated_data.get('telefone'),
                cpf=validated_data.get('cpf'),
                cep=validated_data.get('cep')
            )


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)
    nova_senha = serializers.CharField(write_only=True)


# ==================== SERIALIZERS DE PERFIL ====================

class ClientesSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Clientes
        fields = ['id', 'email', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep']

    def validate(self, dados):
        if self.instance:
            return validar_campos_comuns(dados, instancia_id=self.instance.id, tipo_usuario='cliente')
        return dados


class LogistasSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Logistas
        fields = ['id', 'email', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep']

    def validate(self, dados):
        if self.instance:
            return validar_campos_comuns(dados, instancia_id=self.instance.id, tipo_usuario='lojista')
        return dados


class EstoqueSerializer(serializers.ModelSerializer):
    produtos = serializers.PrimaryKeyRelatedField(queryset=Produtos.objects.all(), required=False)

    class Meta:
        model = Estoque
        fields = ['id', 'produtos', 'quantidade', 'tamanho', 'cor']

    def validate(self, dados):
        produto = dados.get('produtos')
        
        # Recuperação dinâmica do ID pela URL aninhada (visto na UC04)
        if not produto and self.context.get('view'):
            kwargs = self.context['view'].kwargs
            produto_id = kwargs.get('product_id')
            if produto_id:
                produto = Produtos.objects.filter(id=produto_id).first()
                if not produto:
                    raise serializers.ValidationError({"produtos": "Produto associado não encontrado."})
                dados['produtos'] = produto

        tamanho = dados.get('tamanho', getattr(self.instance, 'tamanho', None))
        cor = dados.get('cor', getattr(self.instance, 'cor', None))

        if produto:
            query = Estoque.objects.filter(produtos=produto, tamanho=tamanho, cor=cor)
            if self.instance:
                query = query.exclude(id=self.instance.id)
                
            if query.exists():
                raise serializers.ValidationError("Esta combinação de variação (Tamanho/Cor) já está registrada para este produto.")
        else:
            raise serializers.ValidationError({"produtos": "O campo produto é obrigatório."})
        
        return dados


class ProdutosSerializer(serializers.ModelSerializer):
    variacoes = EstoqueSerializer(many=True, read_only=True)

    class Meta:
        model = Produtos
        fields = ['id', 'nome_produto', 'descricao', 'preco', 'categoria', 'ativo', 'variacoes']


class ProdutosPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50