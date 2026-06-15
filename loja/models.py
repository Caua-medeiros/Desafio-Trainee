from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from datetime import timedelta

# Validadores para garantir a integridade dos dados inseridos
cpf_validador = RegexValidator(
    r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 
    'O CPF deve seguir o formato padrão: 000.000.000-00'
)
telefone_validador = RegexValidator(
    r'^\(\d{2}\)\s\d{4,5}-\d{4}$', 
    'O telefone deve seguir o formato padrão: (84) 99999-1111'
)

# Entidade de perfil para usuarios do tipo Cliente
class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente')
    nome_completo = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    telefone = models.CharField(validators=[telefone_validador], max_length=15, unique=True)
    cpf = models.CharField(validators=[cpf_validador], max_length=14, unique=True)
    cep = models.CharField(max_length=9)
    endereco = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nome_completo
    
# Entidade de perfil para usuarios do tipo Lojista
class Lojista(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_lojista')
    nome_completo = models.CharField(max_length=100)
    data_nascimento = models.DateField()
    telefone = models.CharField(validators=[telefone_validador], max_length=15, unique=True)
    cpf = models.CharField(validators=[cpf_validador], max_length=14, unique=True)
    cep = models.CharField(max_length=9)
    endereco = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.nome_completo

# Catálogo de produtos vinculados a um lojista especifico
class Produto(models.Model):
    CATEGORIAS_CHOICES = (
    ('calcas', 'Calças'),
    ('bermudas', 'Bermudas'),
    ('blusas', 'Blusas'),
    ('regatas', 'Regatas'),
    ('vestidos', 'Vestidos'),
    ('shorts', 'Shorts'),
    ('saias', 'Saias'),
)
    lojista = models.ForeignKey(Lojista, on_delete=models.CASCADE, null=True, blank=True)
    nome_produto = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    categoria = models.CharField(max_length=20, choices=CATEGORIAS_CHOICES, default='blusas')
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_produto
    
# Controle de estoque fisico e variacoes dos produtos
class VariacaoEstoque(models.Model):
    TAMANHOS_CHOICES = (
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
        ('GG', 'Extra Grande'),
    )
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='variacoes')
    quantidade = models.IntegerField(validators=[MinValueValidator(0)])
    tamanho = models.CharField(max_length=2, choices=TAMANHOS_CHOICES, default='M')
    cor = models.CharField(max_length=30, default='Preto')

    class Meta:
        # Impede a criacao de duplicatas para a mesma combinacao de atributos
        unique_together = ('produto', 'tamanho', 'cor')

    def __str__(self):
        return f"{self.produto.nome_produto} - {self.tamanho} - {self.cor}"

# Registro de tokens de seguranca para redefinicao de credenciais
class TokenRedefinicaoSenha(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=6)
    criado_em = models.DateTimeField(auto_now_add=True)
    utilizado = models.BooleanField(default=False)

    def esta_valido(self):
        # Valida a janela de expiracao de 10 minutos recomendada para seguranca
        return not self.utilizado and timezone.now() < self.criado_em + timedelta(minutes=10)

# Registro de mensagens de suporte e fale conosco recebidas
class MensagemContato(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    assunto = models.CharField(max_length=150)
    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensagem de {self.nome} - {self.assunto}"

# Instancia unica do carrinho vinculada ao cliente logado
class CarrinhoCompra(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='carrinho')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrinho do Cliente: {self.cliente.nome_completo}"

# Itens contidos no carrinho de compras atual do cliente
class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(CarrinhoCompra, on_delete=models.CASCADE, related_name='itens')
    variacao = models.ForeignKey(VariacaoEstoque, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.quantidade}x {self.variacao.produto.nome_produto} ({self.variacao.tamanho}/{self.variacao.cor})"

# Transacoes de vendas geradas a partir do checkout de compras
class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos')
    lojista = models.ForeignKey(Lojista, on_delete=models.CASCADE, related_name='pedidos_loja')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    endereco_entrega = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    forma_pagamento = models.CharField(max_length=50, blank=True, null=True)
    destinatario = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        # Ordenacao cronologica exigida para a fila de atendimento do lojista
        ordering = ['criado_em']

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nome_completo} ({self.status})"

# Registro imutavel dos itens faturados no ato da compra
class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    variacao = models.ForeignKey(VariacaoEstoque, on_delete=models.SET_NULL, null=True)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x Unidades no Pedido #{self.pedido.id}"

# Carteira de metodos de pagamento arquivados pelo cliente
class MetodoPagamento(models.Model):
    TIPO_CHOICES = (
        ('cartao_credito', 'Cartão de Crédito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='metodos_pagamento')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    identificador_metodo = models.CharField(max_length=100, help_text="Ex: Final do cartão ou identificador alternativo")
    salvo_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cliente.nome_completo}"