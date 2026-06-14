import random
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from loja.models import Clientes, Logistas, Produtos, Estoque, PasswordResetToken
from loja.serializers import (
    RegisterSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ClientesSerializer,
    LogistasSerializer,
    ProdutosSerializer,
    EstoqueSerializer,
    ProdutosPagination
)

# ==================== AUTENTICAÇÃO / REGISTRO ====================

class AuthRegisterView(APIView):
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: openapi.Response('Usuário registrado com sucesso!')}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            perfil = serializer.save()
            if isinstance(perfil, Clientes):
                serializer_perfil = ClientesSerializer(perfil)
            else:
                serializer_perfil = LogistasSerializer(perfil)
            return Response(serializer_perfil.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer

    @swagger_auto_schema(
        request_body=ForgotPasswordSerializer,
        responses={200: openapi.Response('E-mail de recuperação processado.')}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user_exists = User.objects.filter(email=email).exists()
            
            if user_exists:
                codigo = f"{random.randint(100000, 999999)}"
                PasswordResetToken.objects.create(email=email, token=codigo)
                print(f"\n[EMAIL] Código de recuperação para {email}: {codigo}\n")
                
            return Response({"detail": "Se o e-mail existir na base, um link de recuperação foi enviado."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer

    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        responses={200: openapi.Response('Senha atualizada com sucesso!')}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            token_informado = serializer.validated_data['token']
            nova_senha = serializer.validated_data['nova_senha']
            
            reset_token = PasswordResetToken.objects.filter(email=email, token=token_informado).last()
            if not reset_token or not reset_token.is_valid():
                return Response({"detail": "Código inválido, expirado ou já utilizado."}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.filter(email=email).first()
            if user:
                user.password = make_password(nova_senha)
                user.save()
                reset_token.used = True
                reset_token.save()
                return Response({"detail": "Senha atualizada com sucesso!"}, status=status.HTTP_200_OK)
                
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== PERFIS DE USUÁRIOS ====================

class ClientesViewSet(viewsets.ModelViewSet):
    serializer_class = ClientesSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_completo']
    search_fields = ['nome_completo', 'user__email']

    def get_queryset(self):
        if not self.request.user or self.request.user.is_anonymous:
            return Clientes.objects.none()
        return Clientes.objects.filter(user=self.request.user).order_by('id')


class LogistasViewSet(viewsets.ModelViewSet):
    serializer_class = LogistasSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_completo']
    search_fields = ['nome_completo', 'user__email']

    def get_queryset(self):
        if not self.request.user or self.request.user.is_anonymous:
            return Logistas.objects.none()
        return Logistas.objects.filter(user=self.request.user).order_by('id')


# ==================== PRODUTOS ====================

class ProdutosViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutosSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = ProdutosPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_produto', 'preco']
    search_fields = ['nome_produto', 'descricao']
    filterset_fields = ['categoria', 'ativo']

    def get_queryset(self):
        user = self.request.user
        # Se for um Lojista Autenticado, vê os seus próprios produtos (Ativos e Inativos)
        if user.is_authenticated and Logistas.objects.filter(user=user).exists():
            lojista = Logistas.objects.filter(user=user).first()
            return Produtos.objects.filter(lojista=lojista).order_by('id')
        # UC05: Clientes e anônimos apenas podem visualizar produtos ATIVOS
        return Produtos.objects.filter(ativo=True).order_by('id')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        lojista = Logistas.objects.filter(user=self.request.user).first()
        if not lojista:
            raise PermissionDenied("Apenas lojistas podem criar produtos.")
        serializer.save(lojista=lojista)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.lojista and instance.lojista.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para editar este produto.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.lojista and instance.lojista.user != self.request.user:
            raise PermissionDenied("Você não tem permissão para deletar este produto.")
        instance.delete()


# ==================== ESTOQUE / VARIAÇÕES ====================

class EstoqueViewSet(viewsets.ModelViewSet):
    serializer_class = EstoqueSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id']
    search_fields = ['produtos__nome_produto', 'tamanho']

    def get_queryset(self):
        user = self.request.user
        if Logistas.objects.filter(user=user).exists():
            lojista = Logistas.objects.filter(user=user).first()
            
            # Se a requisição vier filtrada por um ID de produto na URL (/api/products/:id/variations)
            product_id = self.kwargs.get('product_id')
            if product_id:
                return Estoque.objects.filter(produtos__lojista=lojista, produtos_id=product_id).order_by('id')
                
            return Estoque.objects.filter(produtos__lojista=lojista).order_by('id')
        raise PermissionDenied("Acesso restrito a lojistas para gerenciamento de estoque.")

    def perform_create(self, serializer):
        user = self.request.user
        lojista = Logistas.objects.filter(user=user).first()
        
        # Garante a injeção do produto caso venha pela URL limpa (/products/:id/variations)
        product_id = self.kwargs.get('product_id')
        if product_id:
            produto = get_object_or_404(Produtos, id=product_id, lojista=lojista)
            serializer.save(produtos=produto)
        else:
            serializer.save()


class VariaçãoDetalheView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=EstoqueSerializer,
        responses={200: openapi.Response('Variação atualizada com sucesso!')}
    )
    def put(self, request, pk):
        variacao = get_object_or_404(Estoque, id=pk)
        
        if not variacao.produtos.lojista or variacao.produtos.lojista.user != request.user:
            return Response({"detail": "Permissão negada."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = EstoqueSerializer(variacao, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except IntegrityError:
                return Response({"detail": "Essa variação já existe neste produto."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        variacao = get_object_or_404(Estoque, id=pk)
        
        if not variacao.produtos.lojista or variacao.produtos.lojista.user != request.user:
            return Response({"detail": "Permissão negada."}, status=status.HTTP_403_FORBIDDEN)
            
        variacao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)