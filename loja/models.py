from django.db import models
class Cadastro_Clientes(models.Model):
    nome_completo = models.CharField(blank=False, max_length=100)
    data_nascimento = models.DateField(blank=False)
    telefone = models.CharField(blank=False, max_length=20)
    cpf = models.CharField(blank=False, max_length=11)
    cep = models.CharField(blank=False, max_length=9)
    email = models.EmailField(blank=False, max_length=100)
    senha = models.CharField(blank=False, max_length=100)

    def __str__(self):
        return self.nome_completo
    
class Cadastro_Logistas(models.Model):
    nome_completo = models.CharField(blank=False, max_length=100)
    data_nascimento = models.DateField(blank=False)
    telefone = models.CharField(blank=False, max_length=20)
    cpf = models.CharField(blank=False, max_length=11)
    cep = models.CharField(blank=False, max_length=9)
    email = models.EmailField(blank=False, max_length=100)
    senha = models.CharField(blank=False, max_length=100)

    def __str__(self):
        return self.nome_completo
    
class Login(models.Model):
    email = models.EmailField(blank=False, max_length=100)
    senha = models.CharField(blank=False, max_length=100)

    def __str__(self):
        return self.email
    

class Cadastro_Produtos(models.Model):
    nome_produto = models.CharField(blank=False, max_length=100)
    descricao = models.TextField(blank=False)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    TAMANHO = (
        ('P', 'Pequeno'),
        ('M', 'Médio'),
        ('G', 'Grande'),
        ('GG', 'Extra Grande'),
    )
    tamanho = models.CharField(max_length=2, choices=TAMANHO, blank=False, null=True, default='M')
    estoque = models.IntegerField()

    def __str__(self):
        return self.nome_produto