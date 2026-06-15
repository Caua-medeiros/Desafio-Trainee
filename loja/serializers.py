import re
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from loja.models import (
    Cliente, Lojista, Produto, VariacaoEstoque, MensagemContato, 
    CarrinhoCompra, ItemCarrinho, Pedido, ItemPedido, MetodoPagamento
)

# Algoritmo de validação de CPF
def verificar_cpf_valido(cpf_texto):
    numeros = re.sub(r'\D', '', cpf_texto)
    if len(numeros) != 11 or numeros == numeros[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(numeros[num]) * ((i + 1) - num) for num in range(i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(numeros[i]):
            return False
    return True

# Validação estrutural de perfil (UC01 - CPF Único por Perfil)
def validar_dados_perfil(dados, instancia_id=None, perfil_tipo=None):
    erros = {}
    cpf_informado = dados.get('cpf')
    
    if cpf_informado:
        cpf_limpo = re.sub(r'\D', '', cpf_informado)
        if not verificar_cpf_valido(cpf_limpo):
            erros['cpf'] = "O CPF informado é inválido."
        
        if len(cpf_limpo) == 11:
            cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
            dados['cpf'] = cpf_formatado
        else:
            cpf_formatado = cpf_informado

        # Validações cruzadas
        if perfil_tipo == 'cliente':
            busca_cliente = Cliente.objects.filter(cpf=cpf_formatado)
            if instancia_id:
                busca_cliente = busca_cliente.exclude(id=instancia_id)
            if busca_cliente.exists():
                erros['cpf'] = "Este CPF já encontra-se cadastrado como cliente."
            if Lojista.objects.filter(cpf=cpf_formatado).exists():
                erros['cpf'] = "Este CPF já encontra-se vinculado a uma conta corporativa de lojista."

        elif perfil_tipo == 'lojista':
            busca_lojista = Lojista.objects.filter(cpf=cpf_formatado)
            if instancia_id:
                busca_lojista = busca_lojista.exclude(id=instancia_id)
            if busca_lojista.exists():
                erros['cpf'] = "Este CPF já encontra-se cadastrado como lojista."
            if Cliente.objects.filter(cpf=cpf_formatado).exists():
                erros['cpf'] = "Este CPF já encontra-se vinculado a uma conta de usuário cliente."

    if erros:
        raise serializers.ValidationError(erros)
    return dados

class RegistroUsuarioSerializer(serializers.Serializer):
    TIPO_CHOICES = (('cliente', 'Cliente'), ('lojista', 'Lojista'))
    tipo_usuario = serializers.ChoiceField(choices=TIPO_CHOICES)
    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True)
    nome_completo = serializers.CharField(max_length=100)
    data_nascimento = serializers.DateField()
    telefone = serializers.CharField(max_length=15)
    cpf = serializers.CharField(max_length=14)
    cep = serializers.CharField(max_length=9)
    endereco = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate(self, dados):
        email_informado = dados.get('email')
        if User.objects.filter(email=email_informado).exists():
            raise serializers.ValidationError({"email": "Este endereço de e-mail já está cadastrado no sistema."})
        return validar_dados_perfil(dados, perfil_tipo=dados.get('tipo_usuario'))

    def create(self, dados_validados):
        tipo_usuario = dados_validados.pop('tipo_usuario')
        senha = dados_validados.pop('senha')
        email = dados_validados.pop('email')

        usuario_autenticacao = User.objects.create(
            username=email,
            email=email,
            password=make_password(senha)
        )

        if tipo_usuario == 'cliente':
            return Cliente.objects.create(usuario=usuario_autenticacao, **dados_validados)
        return Lojista.objects.create(usuario=usuario_autenticacao, **dados_validados)

class SolicitacaoRecuperacaoSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ConfirmacaoRecuperacaoSenhaSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=6)
    nova_senha = serializers.CharField(write_only=True)

    def validate_nova_senha(self, valor):
        if len(valor) < 8:
            raise serializers.ValidationError("A nova senha deve possuir uma extensão mínima de 8 caracteres.")
        return valor

class ClienteSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='usuario.email', read_only=True)

    class Meta:
        model = Cliente
        fields = ['id', 'email', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep', 'endereco']

    def validate(self, dados):
        id_atual = self.instance.id if self.instance else None
        return validar_dados_perfil(dados, instancia_id=id_atual, perfil_tipo='cliente')

class LojistaSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='usuario.email', read_only=True)

    class Meta:
        model = Lojista
        fields = ['id', 'email', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep', 'endereco']

    def validate(self, dados):
        id_atual = self.instance.id if self.instance else None
        return validar_dados_perfil(dados, instancia_id=id_atual, perfil_tipo='lojista')

class VariacaoEstoqueSerializer(serializers.ModelSerializer):
    produto = serializers.PrimaryKeyRelatedField(queryset=Produto.objects.all(), required=False)

    class Meta:
        model = VariacaoEstoque
        fields = '__all__'

    def validate(self, dados):
        entidade_produto = dados.get('produto')

        if not entidade_produto and self.instance:
            entidade_produto = self.instance.produto

        if not entidade_produto and 'view' in self.context:
            view = self.context.get('view')
            if hasattr(view, 'kwargs'):
                id_produto = view.kwargs.get('id_produto') or view.kwargs.get('produto_pk') or view.kwargs.get('pk')
                if id_produto:
                    entidade_produto = Produto.objects.filter(id=id_produto).first()

        if not entidade_produto:
            raise serializers.ValidationError({"produto": "A associação de um produto pai é obrigatória."})

        tamanho = dados.get('tamanho', getattr(self.instance, 'tamanho', None))
        cor = dados.get('cor', getattr(self.instance, 'cor', None))

        busca_duplicados = VariacaoEstoque.objects.filter(produto=entidade_produto, tamanho=tamanho, cor=cor)
        if self.instance:
            busca_duplicados = busca_duplicados.exclude(id=self.instance.id)
            
        if busca_duplicados.exists():
            raise serializers.ValidationError("Já existe uma variação idêntica (tamanho e cor) para este produto.")
        
        dados['produto'] = entidade_produto
        return dados

class ProdutoSerializer(serializers.ModelSerializer):
    variacoes = VariacaoEstoqueSerializer(many=True, read_only=True)
    lojista = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Produto
        fields = ['id', 'lojista', 'nome_produto', 'descricao', 'preco', 'categoria', 'ativo', 'variacoes']

class PaginacaoProdutosCustomizada(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'tamanho_pagina'
    max_page_size = 50

class MensagemContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensagemContato
        fields = ['id', 'nome', 'email', 'assunto', 'mensagem', 'criado_em']

    def validate_mensagem(self, valor):
        if len(valor) < 10 or len(valor) > 1000:
            raise serializers.ValidationError("A mensagem deve ter entre 10 e 1000 caracteres.")
        return valor

class ItemCarrinhoSerializer(serializers.ModelSerializer):
    nome_produto = serializers.CharField(source='variacao.produto.nome_produto', read_only=True)
    tamanho = serializers.CharField(source='variacao.tamanho', read_only=True)
    cor = serializers.CharField(source='variacao.cor', read_only=True)
    preco_unitario = serializers.DecimalField(source='variacao.produto.preco', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ItemCarrinho
        fields = ['id', 'variacao', 'quantidade', 'nome_produto', 'tamanho', 'cor', 'preco_unitario']

    def validate(self, dados):
        variacao = dados.get('variacao', getattr(self.instance, 'variacao', None))
        quantidade = dados.get('quantidade', getattr(self.instance, 'quantidade', None))
        
        if variacao and quantidade:
            if quantidade > variacao.quantidade:
                raise serializers.ValidationError({"quantidade": f"Estoque insuficiente ({variacao.quantidade} disponíveis)."})
            
            # UC07: Impede mistura de produtos de diferentes lojistas no mesmo carrinho
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                perfil_cliente = Cliente.objects.filter(usuario=request.user).first()
                if perfil_cliente:
                    carrinho, _ = CarrinhoCompra.objects.get_or_create(cliente=perfil_cliente)
                    outro_item = carrinho.itens.exclude(id=getattr(self.instance, 'id', None)).first()
                    if outro_item and outro_item.variacao.produto.lojista != variacao.produto.lojista:
                        raise serializers.ValidationError({"variacao": "Não é permitido misturar produtos de lojistas diferentes no carrinho."})
                        
        return dados

class CarrinhoCompraSerializer(serializers.ModelSerializer):
    itens = ItemCarrinhoSerializer(many=True, read_only=True)
    total_carrinho = serializers.SerializerMethodField()

    class Meta:
        model = CarrinhoCompra
        fields = ['id', 'cliente', 'itens', 'total_carrinho', 'criado_em']

    def get_total_carrinho(self, obj):
        return sum(item.quantidade * item.variacao.produto.preco for item in obj.itens.all())

class ItemPedidoSerializer(serializers.ModelSerializer):
    nome_produto = serializers.CharField(source='variacao.produto.nome_produto', read_only=True)
    tamanho = serializers.CharField(source='variacao.tamanho', read_only=True)
    cor = serializers.CharField(source='variacao.cor', read_only=True)

    class Meta:
        model = ItemPedido
        fields = ['id', 'variacao', 'nome_produto', 'tamanho', 'cor', 'quantidade', 'preco_unitario']

class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)
    total_pedido = serializers.SerializerMethodField()
    nome_cliente = serializers.CharField(source='cliente.nome_completo', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente', 'nome_cliente', 'lojista', 'status', 'endereco_entrega', 
            'forma_pagamento', 'destinatario', 'itens', 'total_pedido', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['cliente', 'lojista', 'criado_em', 'atualizado_em']

    def get_total_pedido(self, obj):
        return sum(item.quantidade * item.preco_unitario for item in obj.itens.all())

    def validate_status(self, valor):
        # UC09: Transições válidas de status de pedido
        if self.instance:
            status_atual = self.instance.status
            transicoes_validas = {
                'pendente': ['pago', 'cancelado'],
                'pago': ['enviado'],
                'enviado': ['entregue'],
                'entregue': [],
                'cancelado': []
            }
            if valor != status_atual and valor not in transicoes_validas.get(status_atual, []):
                raise serializers.ValidationError(f"Transição de status inválida de '{status_atual}' para '{valor}'.")
        return valor

class CheckoutSerializer(serializers.Serializer):
    endereco_entrega = serializers.CharField(max_length=500, required=True)
    forma_pagamento = serializers.CharField(max_length=50, required=True)
    destinatario = serializers.CharField(max_length=100, required=False, allow_blank=True)

class MetodoPagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPagamento
        fields = ['id', 'tipo', 'identificador_metodo', 'salvo_em']
        read_only_fields = ['cliente']