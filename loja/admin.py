from django.contrib import admin
from .models import Cadastro_Clientes, Cadastro_Logistas, Login, Cadastro_Produtos

class CadastroClientesAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep', 'email')
    list_display_links = ('id', 'nome_completo', 'email')
    list_per_page = 20
    search_fields = ('nome_completo', 'email')

admin.site.register(Cadastro_Clientes, CadastroClientesAdmin)

class CadastroLogistasAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_completo', 'data_nascimento', 'telefone', 'cpf', 'cep', 'email')
    list_display_links = ('id', 'nome_completo', 'email')
    list_per_page = 20
    search_fields = ('nome_completo', 'email')

admin.site.register(Cadastro_Logistas, CadastroLogistasAdmin)

class LoginAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'senha')
    list_display_links = ('id', 'email')
    list_per_page = 20
    search_fields = ('email',)

admin.site.register(Login, LoginAdmin)

class CadastroProdutosAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_produto', 'descricao', 'preco', 'tamanho', 'estoque')
    list_display_links = ('id', 'nome_produto')
    list_per_page = 20
    search_fields = ('nome_produto',)

admin.site.register(Cadastro_Produtos, CadastroProdutosAdmin)

