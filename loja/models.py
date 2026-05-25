from django.db import models

'''Id
Nome_Completo
Data_Nascimento
Telefone
CPF
CEP
E-mail
Senha'''

class Cadrastro(models.Model):
    nome_completo = models.CharField(blank=False, max_length=100)
    data_nascimento = models.DateField(blank=False)
    telefone = models.CharField(blank=False, max_length=20)
    cpf = models.CharField(blank=False, max_length=11)
    cep = models.CharField(blank=False, max_length=9)
    email = models.EmailField(blank=False, max_length=100)
    senha = models.CharField(blank=False, max_length=100)

    def __str__(self):
        return self.nome_completo
    
class 