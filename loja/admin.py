from django.contrib import admin
from loja.models import (
    Cliente, Lojista, Produto, VariacaoEstoque, TokenRedefinicaoSenha, 
    MensagemContato, CarrinhoCompra, ItemCarrinho, Pedido, ItemPedido, MetodoPagamento
)

# Configuracao inline para exibir as variacoes diretamente na pagina do produto
class VariacaoEstoqueInline(admin.TabularInline):
    model = VariacaoEstoque
    extra = 1
    verbose_name = "Variação de Estoque"
    verbose_name_plural = "Variações de Estoque"

# Configuracao inline para exibir os itens do carrinho
class ItemCarrinhoInline(admin.TabularInline):
    model = ItemCarrinho
    extra = 0
    verbose_name = "Item do Carrinho"
    verbose_name_plural = "Itens do Carrinho"

# Configuracao inline para exibir os itens faturados no pedido
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ['variacao', 'quantidade', 'preco_unitario']
    verbose_name = "Item do Pedido"
    verbose_name_plural = "Itens do Pedido"

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'telefone', 'cep', 'usuario')
    search_fields = ('nome_completo', 'cpf', 'usuario__email', 'telefone')
    list_per_page = 20

@admin.register(Lojista)
class LojistaAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'cpf', 'telefone', 'cep', 'usuario')
    search_fields = ('nome_completo', 'cpf', 'usuario__email', 'telefone')
    list_per_page = 20

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome_produto', 'lojista', 'preco', 'categoria', 'ativo')
    list_filter = ('categoria', 'ativo', 'lojista')
    search_fields = ('nome_produto', 'descricao', 'lojista__nome_completo')
    inlines = [VariacaoEstoqueInline]
    list_editable = ('preco', 'ativo')
    list_per_page = 20

@admin.register(VariacaoEstoque)
class VariacaoEstoqueAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto', 'tamanho', 'cor', 'quantidade')
    list_filter = ('tamanho', 'cor')
    search_fields = ('produto__nome_produto', 'cor')
    list_per_page = 25

@admin.register(CarrinhoCompra)
class CarrinhoCompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'criado_em')
    search_fields = ('cliente__nome_completo', 'cliente__usuario__email')
    inlines = [ItemCarrinhoInline]

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'lojista', 'status', 'forma_pagamento', 'criado_em')
    list_filter = ('status', 'forma_pagamento', 'criado_em')
    search_fields = ('id', 'cliente__nome_completo', 'lojista__nome_completo', 'destinatario')
    readonly_fields = ('criado_em', 'atualizado_em')
    inlines = [ItemPedidoInline]
    list_editable = ('status',)
    list_per_page = 20

@admin.register(MetodoPagamento)
class MetodoPagamentoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'identificador_metodo', 'cliente', 'salvo_em')
    list_filter = ('tipo', 'salvo_em')
    search_fields = ('cliente__nome_completo', 'identificador_metodo')

@admin.register(TokenRedefinicaoSenha)
class TokenRedefinicaoSenhaAdmin(admin.ModelAdmin):
    exclude = ('token',)
    list_display = ('email', 'criado_em', 'utilizado')
    readonly_fields = ('email', 'criado_em', 'utilizado')
    list_filter = ('utilizado', 'criado_em')
    search_fields = ('email',)

@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ('assunto', 'nome', 'email', 'criado_em')
    list_filter = ('criado_em',)
    search_fields = ('nome', 'email', 'assunto', 'mensagem')
    readonly_fields = ('criado_em',)