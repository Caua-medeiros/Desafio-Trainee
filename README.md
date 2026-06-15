# 📚 New Style API

A **New Style API** é uma solução de backend RESTful desenvolvida com Django REST Framework (DRF). O projeto foi concebido como parte do processo seletivo para Trainee da EJECT, oferecendo uma infraestrutura robusta e escalável para e-commerces. A API engloba controle de acesso baseado em perfis (RBAC), gerenciamento de catálogo com suporte a grades de inventário (tamanho e cor), persistência e incremento atômico de itens no carrinho de compras, além de um pipeline seguro de fechamento de pedidos (checkout) governado por uma máquina de estados estável.

## 🌐 Endpoints Globais e Documentação

* **URL Base da API:** `http://127.0.0.1:8000`
* **Documentação Interativa (Swagger/OpenAPI):** `http://127.0.0.1:8000/swagger/`
* **Documentação Alternativa (Redoc):** `http://127.0.0.1:8000/redoc/`

## 🧰 Stack Tecnológica e Dependências Core

| Dependência | Versão | Descrição |
| :--- | :--- | :--- |
| **Python** | 3.13 | Linguagem de programação e ambiente de execução core do projeto. |
| **Django** | 5.2 | Framework estrutural, responsável pelo mapeamento ORM e roteamento. |
| **Django REST Framework** | 3.16 | Toolkit para serialização de dados, tratamento de requisições e ViewSets. |
| **Simple JWT** | - | Mecanismo de autenticação Stateless baseado em tokens JSON Web Tokens. |
| **drf-yasg** | - | Biblioteca para geração automatizada do esquema OpenAPI e Swagger UI. |
| **django-filter** | - | Engine para criação de queries de filtragem dinâmica via parâmetros de URL. |
| **corsheaders** | - | Middleware para gerenciamento e liberação de políticas de CORS. |

---

## 🏗️ Arquitetura de Software e Modelagem de Dados

O ecossistema do backend foi centralizado em uma arquitetura monolítica simplificada através do app `loja`, garantindo atomicidade e forte integridade referencial nas tabelas do banco de dados:

### 🔐 Gestão de Identidades e Acesso (`users`)
O sistema estende o modelo nativo de autenticação do Django para segregar o escopo de atuação na API:
* **User (Base):** Entidade abstrata/concreta que centraliza as credenciais de login e a flag identificadora do tipo de conta.
* **Cliente:** Modelo que estende o usuário comum, armazenando metadados fiscais e logísticos essenciais para a entrega (CPF, CEP, Endereço de Entrega, Telefone, Data de Nascimento).
* **Lojista:** Perfil com privilégios administrativos no backend, autorizado a gerir o catálogo e o andamento dos pedidos.

### 🛍️ Inventário e Catálogo de Produtos
* **Produto:** Armazena os dados genéricos da peça de vestuário (Nome, descrição, preço base e categoria ativa).
* **Variação:** Abstração relacional (1-N) para a grade física do produto. Controla de forma isolada a disponibilidade de stock baseada na combinação de `Tamanho` e `Cor`.

### 🛒 Camada Transacional e Fluxo Financeiro
* **Carrinho / ItemCarrinho:** Implementa lógica imperativa no método de gravação (`POST`). Se a variação enviada já constar no carrinho do cliente, o backend executa uma operação de incremento na quantidade em vez de duplicar o registo. O modelo expõe propriedades calculadas para retornar o `total_carrinho` em tempo real.
* **Pedido (Order):** Congela o estado financeiro e os itens do carrinho no momento do checkout, isolando os dados de variações futuras de preço. Possui um campo de status protegido por uma máquina de estados.

---

## 🧩 Contrato de Endpoints e Métodos HTTP

### 📋 Módulo de Autenticação e Emissão de Credenciais

| Funcionalidade Backend | Endpoint da API | Método HTTP | Payload Esperado (JSON) |
| :--- | :--- | :--- | :--- |
| **Registo de Usuario** | `/auth/register` | `POST` | `email`, `senha`, `nome_completo`, `tipo_usuario`, `data_nascimento`, `telefone`, `cpf`, `cep`, `endereco` |
| **Autenticação (Obter JWT)** | `/auth/login` | `POST` | `username`, `password` -> Retorna `access` e `refresh` |
| **Refresh de Token** | `/auth/token/refresh` | `POST` | `refresh` -> Emite um novo token de acesso `access` |

### 📋 Módulo de Catálogo e Inventário (Restrito ao Lojista)

| Funcionalidade Backend | Endpoint da API | Método HTTP | Regra de Negócio / Permissão |
| :--- | :--- | :--- | :--- |
| **Listar Catálogo** | `/products` | `GET` | Aberto ao público (`AllowAny`). |
| **Criar Produto** | `/products` | `POST` | Bloqueado para Clientes. Exige escopo de **Lojista**. |
| **Criar Grade de Stock** | `/products/{id}/variacoes` | `POST` | Vincula tamanho, cor e quantidade inicial ao ID do produto. |

### 📋 Módulo do Carrinho de Compras e Checkout (Escopo do Cliente)

| Funcionalidade Backend | Endpoint da API | Método HTTP | Regra de Negócio / Permissão |
| :--- | :--- | :--- | :--- |
| **Consultar Carrinho** | `/cart` | `GET` | Retorna as variações adicionadas e o subtotal agregado. |
| **Adicionar/Incrementar Item** | `/cart/items` | `POST` | Valida stock disponível e executa o acúmulo atómico. |
| **Processar Checkout** | `/orders/checkout` | `POST` | Converte os itens em um Pedido `pendente` e limpa o carrinho. |
| **Atualizar Status** | `/orders/{id}` | `PATCH` | **Segurança:** Apenas o **Lojista** pode mudar o status para `pago`. |

---

## 🔍 Regras de Negócio Avançadas

### 🎯 Validação Estrita de Categorias (`CHOICES`)
O campo `categoria` no modelo de `Produto` utiliza validação em nível de ORM baseada em uma tupla fechada. O payload enviado deve corresponder exatamente a um dos identificadores em minúsculo:
`calcas`, `bermudas`, `blusas`, `regatas`, `vestidos`, `shorts`, `saias`.

* **Query Parameter de Categoria:** `GET /products?categoria=calcas`
* **Busca Textual Avançada (SearchFilter):** `GET /products?search=Casaco` (Gera uma query SQL interna utilizando cláusulas `LIKE` nos campos `nome_produto` e `descricao`).
* **Ordenação de Resultados (OrderingFilter):** `GET /products?ordering=-preco` (Maior para menor) ou `?ordering=preco` (Menor para maior).

### 🛡️ Throttling (Camada de Proteção contra Sobrecarga)
Configurado diretamente no dicionário `REST_FRAMEWORK` para mitigar ataques de negação de serviço (DDoS) e varreduras automatizadas:
* **AnonRateThrottle (Utilizadores Anónimos):** Teto máximo de **100 requisições por minuto**.
* **UserRateThrottle (Utilizadores Autenticados):** Teto máximo de **600 requisições por minuto**.

---

## 🔐 Políticas de Permissão e Segurança (RBAC)

O controle de acessos do sistema baseia-se no modelo RBAC (Role-Based Access Control) através da inspeção dos claims do Bearer Token JWT injetado no Header das requisições:
1. `AllowAny`: Rotas de leitura de catálogo e fluxos de cadastro/login.
2. `IsAuthenticated` (Escopo Cliente): Exigido para manipulação e mutação do estado de carrinhos e inicialização de ordens de compra.
3. `IsAuthenticated` + Validação de Perfil (`Lojista`): Middleware interno que barra requisições de escrita em rotas de produtos ou pedidos que venham de tokens emitidos para clientes, devolvendo um código HTTP `403 Forbidden`.

---

## 🛠️ Instruções para Instalação e Execução Local

1. **Clonar o repositório do projeto:**
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd "Desafio trainee"
   ```

2. **Criar e ativar o ambiente virtual:**
   ```bash
   python -m venv venv
   venv\\Scripts\\activate
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variáveis de ambiente:**
   - Crie um arquivo `.env` na raiz do projeto com as chaves:
     ```env
     DJANGO_SECRET_KEY="sua_chave_secreta_aqui"
     EMAIL_USER="seu-email@dominio.com"
     EMAIL_PASSWORD="sua_senha_de_app"
     ```
   - Para desenvolvimento, o backend de e-mail está configurado para exibir mensagens no console.

5. **Executar migrações:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Executar o servidor:**
   ```bash
   python manage.py runserver
   ```



DESAFIO TRAINEE/
├── loja/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── Throttles.py
│   └── views.py
├── setup/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── venv/
├── .gitignore
├── db.sqlite3
├── manage.py
├── README.md
└── requirements.txt


🧑‍💻 Desenvolvedor Backend
Cauã Medeiros

Candidato a Trainee EJECT 2026 | C&T
