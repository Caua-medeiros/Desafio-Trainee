import random
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from loja.models import Clientes, Logistas, Produtos, Estoque, PasswordResetToken
from loja.serializers import (
    ClientesSerializer, LogistasSerializer, ProdutosSerializer, 
    EstoqueSerializer, RegisterSerializer, ForgotPasswordSerializer, 
    ResetPasswordSerializer
)

class ClientesViewSet(viewsets.ModelViewSet):
    queryset = Clientes.objects.all().order_by('id')
    serializer_class = ClientesSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_completo']
    search_fields = ['nome_completo', 'user__email']

class LogistasViewSet(viewsets.ModelViewSet):
    queryset = Logistas.objects.all().order_by('id')
    serializer_class = LogistasSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_completo']
    search_fields = ['nome_completo', 'user__email']

class ProdutosViewSet(viewsets.ModelViewSet):
    queryset = Produtos.objects.all().order_by('id')
    serializer_class = ProdutosSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'nome_produto', 'preco']
    search_fields = ['nome_produto']
    filterset_fields = ['categoria', 'ativo']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and Logistas.objects.filter(user=user).exists():
            return Produtos.objects.all().order_by('id')
        return Produtos.objects.filter(ativo=True).order_by('id')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        lojista = Logistas.objects.filter(user=self.request.user).first()
        serializer.save(lojista=lojista)

class GerenciamentoEstoqueView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=EstoqueSerializer,
        responses={
            201: openapi.Response('Variação de estoque registrada com sucesso!'),
            400: openapi.Response('Erro de validação ou variação duplicada (Tamanho + Cor)'),
            403: openapi.Response('Permissão negada')
        }
    )
    def post(self, request, product_id):
        produto = get_object_or_404(Produtos, id=product_id)
        
        if not produto.lojista or produto.lojista.user != request.user:
            return Response(
                {"detail": "Você não tem permissão para alterar o estoque deste produto."}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = EstoqueSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(produtos=produto)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response(
                    {"detail": "Essa variação (Tamanho + Cor) já existe para este produto."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EstoqueViewSet(viewsets.ModelViewSet):
    queryset = Estoque.objects.all().order_by('id')
    serializer_class = EstoqueSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id']
    search_fields = ['produtos__nome_produto', 'tamanho']

class AuthRegisterView(APIView):
    serializer_class = RegisterSerializer

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response('Conta criada com sucesso!'),
            400: openapi.Response('Erro de validação (Campos inválidos ou duplicados)')
        }
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            perfil = serializer.save()
            serializer_perfil = ClientesSerializer(perfil) if isinstance(perfil, Clientes) else LogistasSerializer(perfil)
            return Response(serializer_perfil.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    serializer_class = ForgotPasswordSerializer

    @swagger_auto_schema(
        request_body=ForgotPasswordSerializer,
        responses={200: openapi.Response('Se o e-mail existir na base, um código foi enviado.')}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user_exists = User.objects.filter(email=email).exists()
            
            if user_exists:
                codigo = f"{random.randint(100000, 999999)}"
                PasswordResetToken.objects.create(email=email, token=codigo)
                
                print("\n" + "="*50)
                print(f"E-MAIL DE RECUPERAÇÃO ENVIADO PARA: {email}")
                print(f"Seu código de verificação é: {codigo}")
                print("Este código expira em 10 minutos.")
                print("="*50 + "\n")
                
            return Response({"detail": "Se o e-mail existir na base, um link de recuperação foi enviado."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    serializer_class = ResetPasswordSerializer

    @swagger_auto_schema(
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response('Senha atualizada com sucesso!'),
            400: openapi.Response('Código inválido, expirado ou já utilizado')
        }
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
                
                return Response({"detail": "Senha updated com sucesso!"}, status=status.HTTP_200_OK)
                
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)