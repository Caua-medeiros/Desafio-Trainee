from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from datetime import timedelta

# ==================== VALIDATORES ====================

cpf_validator = RegexValidator(
    r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 
    'CPF deve seguir o modelo: 000.000.000-00'
)
telefone_validator = RegexValidator(
    r'^\(\d{2}\)\s\d{4,5}-\d{4}$', 
    'Telefone deve seguir o modelo: (84) 99999-1111'
)

# ==================== PERFIS DE USUÁRIO ====================

class Clientes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_cliente')
    nome_completo = models.CharField(blank=False, max_length=100, null=False)
    data_nascimento = models.DateField(blank=False, null=False)
    telefone = models.CharField(validators=[telefone_validator], max_length=15, unique=True)
    cpf = models.CharField(validators=[cpf_validator], max_length=14, unique=True)
    cep = models.CharField(blank=False, max_length=9, null=False)

    def __str__(self):
        return self.nome_completo
    
class Logistas(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_lojista')
    nome_completo = models.CharField(blank=False, max_length=100, null=False)
    data_nascimento = models.DateField(blank=False, null=False)
    telefone = models.CharField(validators=[telefone_validator], max_length=15, unique=True)
    cpf = models.CharField(validators=[cpf_validator], max_length=14, unique=True)
    cep = models.CharField(blank=False, max_length=9, null=False)

    def __str__(self):
        return self.nome_completo

# ==================== PRODUTOS E ESTOQUE ====================

class Produtos(models.Model):
    CATEGORIAS = (
        ('camisas', 'Camisas'),
        ('calcas', 'Calças'),
        ('casacos', 'Casacos'),
        ('acessorios', 'Acessórios'),
    )
    lojista = models.ForeignKey(Logistas, on_delete=models.CASCADE, null=True, blank=True)
    nome_produto = models.CharField(blank=False, max_length=100, null=False)
    descricao = models.TextField(blank=False, null=False)
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, validators=[MinValueValidator(0.01)])
    categoria = models.CharField(max_length=20, choices=CATEGORIAS, default='camisas')
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_produto
    
class Estoque(models.Model):
    TAMANHO = (
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
        ('GG', 'Extra Grande'),
    )
    produtos = models.ForeignKey(Produtos, on_delete=models.CASCADE, related_name='variacoes', blank=False, null=False)
    quantidade = models.IntegerField(blank=False, null=False, validators=[MinValueValidator(0)])
    tamanho = models.CharField(max_length=2, choices=TAMANHO, blank=False, null=False, default='M')
    cor = models.CharField(max_length=30, blank=False, null=False, default='Preto')

    class Meta:
        unique_together = ('produtos', 'tamanho', 'cor')

    def __str__(self):
        return f"{self.produtos.nome_produto} - {self.tamanho} - {self.cor}"

# ==================== RECUPERAÇÃO DE SENHA ====================

class PasswordResetToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.created_at + timedelta(minutes=10)

# ==================== UC06: CONTATO ====================

class Contato(models.Model):
    nome = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(blank=False, null=False)
    assunto = models.CharField(max_length=150, blank=False, null=False)
    mensagem = models.TextField(blank=False, null=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contato de {self.nome} - {self.assunto}"

# ==================== UC07: CARRINHO ====================

class Carrinho(models.Model):
    cliente = models.OneToOneField(Clientes, on_delete=models.CASCADE, related_name='carrinho')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrinho do Cliente: {self.cliente.nome_completo}"

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    variacao = models.ForeignKey(Estoque, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.quantidade}x {self.variacao.produtos.nome_produto} ({self.variacao.tamanho}/{self.variacao.cor})"

# ==================== UC08 & UC09: PEDIDOS ====================

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('pago', 'Pago'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    )
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='pedidos')
    lojista = models.ForeignKey(Logistas, on_delete=models.CASCADE, related_name='pedidos_loja')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    endereco_entrega = models.TextField(blank=False, null=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['criado_em']  # UC09: Mais antigos primeiro

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.nome_completo} ({self.status})"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    variacao = models.ForeignKey(Estoque, on_delete=models.SET_NULL, null=True)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Congela o preço na hora da compra

    def __str__(self):
        return f"{self.quantidade}x Itens no Pedido #{self.pedido.id}"

# ==================== UC10: MÉTODOS DE PAGAMENTO ====================

class MetodoPagamento(models.Model):
    TIPO_CHOICES = (
        ('cartao_credito', 'Cartão de Crédito'),
        ('pix', 'PIX'),
        ('boleto', 'Boleto'),
    )
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='metodos_pagamento')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    # Dados fictícios/mascarados para o mockup de cartão (ex: "vencimento", "final_4_digitos")
    identificador_metodo = models.CharField(max_length=100, help_text="Final do cartão ou chave de identificação")
    salvo_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cliente.nome_completo}"