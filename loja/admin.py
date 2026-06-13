from django.contrib import admin
from .models import Clientes, Logistas, Produtos, Estoque, PasswordResetToken

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_completo', 'telefone', 'cpf')
    search_fields = ('nome_completo', 'cpf')

@admin.register(Logistas)
class LogistasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_completo', 'telefone', 'cpf')
    search_fields = ('nome_completo', 'cpf')

@admin.register(Produtos)
class ProdutosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_produto', 'preco', 'categoria', 'ativo')
    list_filter = ('categoria', 'ativo')
    search_fields = ('nome_produto',)

@admin.register(Estoque)
class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('id', 'produtos', 'tamanho', 'cor', 'quantidade')
    list_filter = ('tamanho', 'cor')

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('email', 'token', 'created_at', 'used')
    list_filter = ('used',)