from django.db import models
from django.core.validators import RegexValidator, MinValueValidator

cpf_validator = RegexValidator(r'^\d{11}$', 'CPF deve conter exatamente 11 dígitos numéricos.')
telefone_validator = RegexValidator(r'^\d{10,13}$', 'Telefone deve ter entre 10 e 13 dígitos numéricos.')

class Clientes(models.Model):
    nome_completo = models.CharField(blank=False, max_length=100,null=False)
    data_nascimento = models.DateField(blank=False,null=False)
    telefone = models.CharField(validators=[telefone_validator], max_length=20, unique=True)
    cpf = models.CharField(validators=[cpf_validator], max_length=11, unique=True)
    cep = models.CharField(blank=False, max_length=9,null=False)
    email = models.EmailField(blank=False, max_length=100,null=False,unique=True)
    senha = models.CharField(blank=False, max_length=100,null=False)

    def __str__(self):
        return self.nome_completo
    
class Logistas(models.Model):
    nome_completo = models.CharField(blank=False, max_length=100,null=False)
    data_nascimento = models.DateField(blank=False,null=False)
    telefone = models.CharField(validators=[telefone_validator], max_length=20, unique=True)
    cpf = models.CharField(validators=[cpf_validator], max_length=11, unique=True)
    cep = models.CharField(blank=False, max_length=9,null=False)
    email = models.EmailField(blank=False, max_length=100,null=False,unique=True)
    senha = models.CharField(blank=False, max_length=100,null=False)

    def __str__(self):
        return self.nome_completo
    
class Login(models.Model):
    email = models.EmailField(blank=False, max_length=100,null=False,unique=True)
    senha = models.CharField(blank=False, max_length=100,null=False)

    def __str__(self):
        return self.email
    

class Produtos(models.Model):
    lojista = models.ForeignKey(Logistas, on_delete=models.CASCADE, null=True, blank=True)
    nome_produto = models.CharField(blank=False, max_length=100,null=False)
    descricao = models.TextField(blank=False,null=False)
    preco = models.DecimalField(max_digits=10, decimal_places=2,null=False, blank=False, validators=[MinValueValidator(0.01)])
   

    def __str__(self):
        return self.nome_produto
    
class Estoque(models.Model):
    TAMANHO = (
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
        ('GG', 'Extra Grande'),
    )
    produtos = models.ForeignKey(Produtos, on_delete=models.CASCADE, blank=False, null=False)
    quantidade = models.IntegerField(blank=False, null=False, validators=[MinValueValidator(0)])
    tamanho = models.CharField(max_length=2, choices=TAMANHO, blank=False, null=False, default='M')
    
    def __str__(self):
        return f"{self.produtos.nome_produto} - {self.tamanho}"