from django.contrib import admin
from .models import Clientes, Logistas, Login, Produtos, Estoque

class ClientesAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep', 'email')
    list_display_links = ('id', 'nome_completo', 'email')
    list_per_page = 20
    search_fields = ('nome_completo', 'email')

admin.site.register(Clientes, ClientesAdmin)

class LogistasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep', 'email')
    list_display_links = ('id', 'nome_completo', 'email')
    list_per_page = 20
    search_fields = ('nome_completo', 'email')

admin.site.register(Logistas, LogistasAdmin)

class LoginAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'senha')
    list_display_links = ('id', 'email')
    list_per_page = 20
    search_fields = ('email',)

admin.site.register(Login, LoginAdmin)

class ProdutosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_produto', 'descricao', 'preco')
    list_display_links = ('id', 'nome_produto')
    list_per_page = 20
    search_fields = ('nome_produto',)

admin.site.register(Produtos, ProdutosAdmin)

class EstoqueAdmin(admin.ModelAdmin):
    list_display = ('id', 'produtos', 'quantidade', 'tamanho')
    list_display_links = ('id', 'produtos')
    list_per_page = 20
    search_fields = ('produtos__nome_produto',)

admin.site.register(Estoque, EstoqueAdmin)
