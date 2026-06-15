import os
import random
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from rest_framework import viewsets, status, filters, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from loja.models import (
    Cliente, Lojista, Produto, VariacaoEstoque, TokenRedefinicaoSenha, 
    MensagemContato, CarrinhoCompra, ItemCarrinho, Pedido, ItemPedido, MetodoPagamento
)

# IMPORT CORRIGIDO: Inclui os serializers de Auth/Recuperação de senha
from loja.serializers import (
    RegistroUsuarioSerializer, SolicitacaoRecuperacaoSenhaSerializer, ConfirmacaoRecuperacaoSenhaSerializer,
    ProdutoSerializer, VariacaoEstoqueSerializer, PaginacaoProdutosCustomizada, 
    MensagemContatoSerializer, ItemCarrinhoSerializer, CarrinhoCompraSerializer,
    PedidoSerializer, CheckoutSerializer, MetodoPagamentoSerializer
)

class RegistroUsuarioView(APIView):
    serializer_class = RegistroUsuarioSerializer
    permission_classes = []

    @swagger_auto_schema(request_body=RegistroUsuarioSerializer, responses={201: openapi.Response('Sucesso')})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Usuário registrado com sucesso!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SolicitacaoRecuperacaoSenhaView(APIView):
    serializer_class = SolicitacaoRecuperacaoSenhaSerializer
    permission_classes = []

    @swagger_auto_schema(request_body=SolicitacaoRecuperacaoSenhaSerializer, responses={200: openapi.Response('Processado')})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email_alvo = serializer.validated_data['email']
            if User.objects.filter(email=email_alvo).exists():
                codigo_verificacao = f"{random.randint(100000, 999999)}"
                TokenRedefinicaoSenha.objects.create(email=email_alvo, token=codigo_verificacao)

                protocolo = 'https' if request.is_secure() else 'http'
                host = request.get_host()
                link_recuperacao = f"{protocolo}://{host}/auth/reset-password?email={email_alvo}&token={codigo_verificacao}"

                send_mail(
                    subject="Recuperação de Senha - Loja EJECT",
                    message=(
                        "Você solicitou a redefinição de senha.\n\n"
                        f"Acesse o link abaixo para continuar:\n{link_recuperacao}\n\n"
                        "Se você não solicitou, ignore esta mensagem."
                    ),
                    from_email=os.getenv('EMAIL_USER', 'suporte@lojaeject.com'),
                    recipient_list=[email_alvo],
                    fail_silently=False
                )
            # UC02: Mantém blindagem de segurança para não vazar a existência do usuário
            return Response({"detail": "Se o e-mail informado constar em nossa base, um link de recuperação foi enviado."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfirmacaoRecuperacaoSenhaView(APIView):
    serializer_class = ConfirmacaoRecuperacaoSenhaSerializer
    permission_classes = []

    @swagger_auto_schema(request_body=ConfirmacaoRecuperacaoSenhaSerializer, responses={200: openapi.Response('Sucesso')})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email_alvo = serializer.validated_data['email']
            token_informado = serializer.validated_data['token']
            nova_senha = serializer.validated_data['nova_senha']
            
            registro_token = TokenRedefinicaoSenha.objects.filter(email=email_alvo, token=token_informado).last()
            entidade_usuario = User.objects.filter(email=email_alvo).first()
            
            if not registro_token or not registro_token.esta_valido() or not entidade_usuario:
                return Response({"detail": "O código informado é inválido, expirou ou já foi utilizado."}, status=status.HTTP_400_BAD_REQUEST)
            
            entidade_usuario.password = make_password(nova_senha)
            entidade_usuario.save()
            registro_token.utilizado = True
            registro_token.save()
            return Response({"detail": "Senha redefinida com sucesso!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = PaginacaoProdutosCustomizada
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_produto', 'preco']
    search_fields = ['nome_produto', 'descricao']
    filterset_fields = ['categoria']

    def get_queryset(self):
        usuario_atual = self.request.user
        if usuario_atual.is_authenticated and Lojista.objects.filter(usuario=usuario_atual).exists():
            perfil_lojista = Lojista.objects.filter(usuario=usuario_atual).first()
            return Produto.objects.filter(lojista=perfil_lojista).order_by('id')
        # UC05: Clientes e anônimos veem apenas produtos ativos
        return Produto.objects.filter(ativo=True).order_by('id')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        perfil_lojista = Lojista.objects.filter(usuario=self.request.user).first()
        if not perfil_lojista:
            raise PermissionDenied("Apenas contas do tipo lojista podem catalogar produtos.")
        serializer.save(lojista=perfil_lojista)

    def perform_update(self, serializer):
        registro = self.get_object()
        if registro.lojista and registro.lojista.usuario != self.request.user:
            raise PermissionDenied("Este produto não pertence ao seu estabelecimento.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.lojista and instance.lojista.usuario != self.request.user:
            raise PermissionDenied("Este produto não pertence ao seu estabelecimento.")
        instance.delete()

class VariacaoEstoqueViewSet(viewsets.ModelViewSet):
    serializer_class = VariacaoEstoqueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario_atual = self.request.user
        perfil_lojista = get_object_or_404(Lojista, usuario=usuario_atual)
        id_produto_url = self.kwargs.get('id_produto')
        if id_produto_url:
            return VariacaoEstoque.objects.filter(produto__lojista=perfil_lojista, produto_id=id_produto_url).order_by('id')
        return VariacaoEstoque.objects.filter(produto__lojista=perfil_lojista).order_by('id')

    def perform_create(self, serializer):
        perfil_lojista = get_object_or_404(Lojista, usuario=self.request.user)
        id_produto_url = self.kwargs.get('id_produto')
        entidade_produto = get_object_or_404(Produto, id=id_produto_url, lojista=perfil_lojista)
        serializer.save(produto=entidade_produto)

class DetalheVariacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        registro_variacao = get_object_or_404(VariacaoEstoque, id=pk)
        if not registro_variacao.produto.lojista or registro_variacao.produto.lojista.usuario != request.user:
            return Response({"detail": "Permissão negada."}, status=status.HTTP_403_FORBIDDEN)
        serializer = VariacaoEstoqueSerializer(registro_variacao, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        registro_variacao = get_object_or_404(VariacaoEstoque, id=pk)
        if not registro_variacao.produto.lojista or registro_variacao.produto.lojista.usuario != request.user:
            return Response({"detail": "Permissão negada."}, status=status.HTTP_403_FORBIDDEN)
        registro_variacao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MensagemContatoView(APIView):
    serializer_class = MensagemContatoSerializer
    permission_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            entidade_contato = serializer.save()
            send_mail(
                subject=f"[Contato] {entidade_contato.assunto}",
                message=entidade_contato.mensagem,
                from_email='naoresponda@lojaeject.com',
                recipient_list=['suporte@lojaeject.com'],
                fail_silently=False
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CarrinhoCompraView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_carrinho(self, request):
        perfil_cliente = get_object_or_404(Cliente, usuario=request.user)
        carrinho, _ = CarrinhoCompra.objects.get_or_create(cliente=perfil_cliente)
        return carrinho

    def get(self, request):
        carrinho = self._get_carrinho(request)
        return Response(CarrinhoCompraSerializer(carrinho).data)

    def delete(self, request):
        carrinho = self._get_carrinho(request)
        carrinho.itens.all().delete()
        return Response({"detail": "Todos os itens foram removidos do carrinho com sucesso."}, status=status.HTTP_204_NO_CONTENT)

class ItemCarrinhoViewSet(viewsets.ModelViewSet):
    serializer_class = ItemCarrinhoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        perfil_cliente = get_object_or_404(Cliente, usuario=self.request.user)
        return ItemCarrinho.objects.filter(carrinho__cliente=perfil_cliente)

    def create(self, request, *args, **kwargs):
        perfil_cliente = get_object_or_404(Cliente, usuario=request.user)
        carrinho, _ = CarrinhoCompra.objects.get_or_create(cliente=perfil_cliente)
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        variacao = serializer.validated_data['variacao']
        quantidade = serializer.validated_data['quantidade']
        
        item_existente = ItemCarrinho.objects.filter(carrinho=carrinho, variacao=variacao).first()
        
        if item_existente:
            nova_qtd = item_existente.quantidade + quantidade
            if nova_qtd > variacao.quantidade:
                raise ValidationError({"quantidade": f"Estoque insuficiente. Desejado: {nova_qtd}, Disponível: {variacao.quantidade}"})
            
            # CORREÇÃO APLICADA: Propriedade inválida (.amount) removida
            item_existente.quantidade = nova_qtd
            item_existente.save()
            
            serializer_retorno = self.get_serializer(item_existente)
            return Response(serializer_retorno.data, status=status.HTTP_200_OK)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        perfil_cliente = get_object_or_404(Cliente, usuario=self.request.user)
        carrinho, _ = CarrinhoCompra.objects.get_or_create(cliente=perfil_cliente)
        serializer.save(carrinho=carrinho)

class PedidoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = PedidoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['criado_em']

    def get_queryset(self):
        usuario_atual = self.request.user
        if Lojista.objects.filter(usuario=usuario_atual).exists():
            perfil_lojista = Lojista.objects.get(usuario=usuario_atual)
            return Pedido.objects.filter(lojista=perfil_lojista).order_by('criado_em')
        if Cliente.objects.filter(usuario=usuario_atual).exists():
            perfil_cliente = Cliente.objects.get(usuario=usuario_atual)
            return Pedido.objects.filter(cliente=perfil_cliente).order_by('-criado_em')
        return Pedido.objects.none()

    def perform_update(self, serializer):
        # UC09: Garante que apenas lojistas atualizam o status
        if not Lojista.objects.filter(usuario=self.request.user).exists():
            raise PermissionDenied("Apenas lojistas podem modificar pedidos.")
        serializer.save()

class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic()
    def post(self, request):
        perfil_cliente = get_object_or_404(Cliente, usuario=request.user)
        carrinho = get_object_or_404(CarrinhoCompra, cliente=perfil_cliente)
        
        if not carrinho.itens.exists():
            return Response({"detail": "Seu carrinho está vazio."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        lotes = {}
        for item in carrinho.itens.all():
            variacao = VariacaoEstoque.objects.select_for_update().get(id=item.variacao.id)
            if variacao.quantidade < item.quantidade:
                return Response({"detail": f"Estoque insuficiente para {variacao}."}, status=status.HTTP_400_BAD_REQUEST)
            
            lojista = variacao.produto.lojista
            if lojista not in lotes:
                lotes[lojista] = []
            lotes[lojista].append((item, variacao))

        pedidos_criados = []
        for lojista, itens_lista in lotes.items():
            pedido = Pedido.objects.create(
                cliente=perfil_cliente,
                lojista=lojista,
                status='pendente',
                endereco_entrega=serializer.validated_data['endereco_entrega'],
                forma_pagamento=serializer.validated_data['forma_pagamento'],
                destinatario=serializer.validated_data.get('destinatario') or perfil_cliente.nome_completo
            )
            for item_carrinho, var_banco in itens_lista:
                ItemPedido.objects.create(
                    pedido=pedido,
                    variacao=var_banco,
                    quantidade=item_carrinho.quantidade,
                    preco_unitario=var_banco.produto.preco
                )
                var_banco.quantidade -= item_carrinho.quantidade
                var_banco.save()
            pedidos_criados.append(pedido)

        carrinho.itens.all().delete()
        return Response(PedidoSerializer(pedidos_criados, many=True).data, status=status.HTTP_201_CREATED)

class MetodoPagamentoViewSet(viewsets.ModelViewSet):
    serializer_class = MetodoPagamentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        perfil_cliente = get_object_or_404(Cliente, usuario=self.request.user)
        return MetodoPagamento.objects.filter(cliente=perfil_cliente).order_by('-id')

    def perform_create(self, serializer):
        perfil_cliente = get_object_or_404(Cliente, usuario=self.request.user)
        serializer.save(cliente=perfil_cliente)