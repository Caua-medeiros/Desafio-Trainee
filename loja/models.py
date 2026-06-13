from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from datetime import timedelta

cpf_validator = RegexValidator(
    r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', 
    'CPF deve seguir o modelo: 000.000.000-00'
)
telefone_validator = RegexValidator(
    r'^\(\d{2}\)\s\d{4,5}-\d{4}$', 
    'Telefone deve seguir o modelo: (84) 99999-1111'
)

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

class PasswordResetToken(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.used and timezone.now() < self.created_at + timedelta(minutes=10)