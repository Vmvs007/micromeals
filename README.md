# MicroMeals

Aplicação didática de encomendas de comida construída com Python, FastAPI e arquitetura de microsserviços.

---

## O que são microsserviços?

Uma arquitetura de microsserviços divide uma aplicação em vários serviços pequenos e independentes, cada um responsável por uma área de negócio específica. Cada serviço:

- corre de forma autónoma num processo separado;
- tem a sua própria base de dados;
- comunica com outros serviços via HTTP/REST;
- pode ser desenvolvido, testado e colocado em produção de forma independente.

Ao contrário de uma aplicação monolítica (tudo num único projeto), os microsserviços permitem maior escalabilidade, manutenção mais fácil e equipas independentes.

---

## Arquitetura da MicroMeals

```
┌─────────────────────────────────────────────────────────────────┐
│                        Cliente HTTP / Swagger                    │
└──────────┬───────────┬──────────────┬──────────────────────────┘
           │           │              │
           ▼           ▼              ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │   customer   │ │  restaurant  │ │    order     │
  │   service    │ │   service    │ │   service    │
  │  :8001       │ │  :8002       │ │  :8003       │
  └──────────────┘ └──────────────┘ └──────┬───────┘
                                           │
                                           ▼
                                   ┌──────────────┐
                                   │   payment    │
                                   │   service    │
                                   │  :8004       │
                                   └──────┬───────┘
                                          │
                              ┌───────────┘
                              ▼
                     ┌──────────────────┐
                     │  notification    │
                     │    service       │
                     │   :8005          │
                     └──────────────────┘
```

---

## Microsserviços

### customer-service (porta 8001)

Gere os clientes da plataforma. Permite criar, listar, consultar, atualizar e eliminar clientes.

### restaurant-service (porta 8002)

Gere restaurantes e os seus menus. Permite criar restaurantes, adicionar itens ao menu, consultar e atualizar informações.

### order-service (porta 8003)

Gere as encomendas. Ao criar uma encomenda, valida o cliente, o restaurante e os itens junto dos respetivos serviços, calcula o total e guarda a encomenda. Também gere a evolução do estado da encomenda.

### payment-service (porta 8004)

Simula o processamento de pagamentos. Consulta a encomenda no order-service, decide aprovação com base no valor e, se aprovado, atualiza o estado da encomenda para PAID.

### notification-service (porta 8005)

Simula o envio de notificações (EMAIL, SMS, APP). Guarda cada notificação na base de dados e imprime no terminal. Não envia mensagens reais.

---

## Responsabilidades de cada serviço

| Serviço               | Responsabilidade                                      | Comunica com                          |
|-----------------------|-------------------------------------------------------|---------------------------------------|
| customer-service      | CRUD de clientes                                      | —                                     |
| restaurant-service    | CRUD de restaurantes e menus                          | —                                     |
| order-service         | Criação e gestão de encomendas                        | customer, restaurant, notification    |
| payment-service       | Simulação de pagamentos                               | order, notification                   |
| notification-service  | Registo de notificações simuladas                     | —                                     |

---

## Como correr o projeto

### Pré-requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Arrancar todos os serviços

```bash
docker compose up --build
```

Para correr em background:

```bash
docker compose up --build -d
```

Para parar:

```bash
docker compose down
```

---

## Documentação Swagger

Após arrancar o projeto, a documentação interativa de cada serviço fica disponível em:

| Serviço              | URL                          |
|----------------------|------------------------------|
| customer-service     | http://localhost:8001/docs   |
| restaurant-service   | http://localhost:8002/docs   |
| order-service        | http://localhost:8003/docs   |
| payment-service      | http://localhost:8004/docs   |
| notification-service | http://localhost:8005/docs   |

---

## Fluxo completo de exemplo

O fluxo principal da aplicação segue esta sequência:

```
1. Criar cliente
        │
        ▼
2. Criar restaurante
        │
        ▼
3. Criar itens de menu
        │
        ▼
4. Criar encomenda  ──► order-service valida cliente, restaurante e itens
        │                order-service calcula o total
        │                encomenda fica com estado: CREATED
        ▼
5. Pagar encomenda  ──► payment-service consulta a encomenda
        │                se valor ≤ 50€ → APPROVED, encomenda passa a PAID
        │                se valor > 50€ → REJECTED
        │                notificação enviada ao cliente
        ▼
6. Atualizar estado ──► PAID → PREPARING → DELIVERED
        │                notificação enviada a cada mudança de estado
        ▼
7. Consultar notificações do cliente
```

---

## Exemplos de pedidos HTTP

### Criar um cliente

```http
POST http://localhost:8001/customers
Content-Type: application/json

{
  "name": "Ana Silva",
  "email": "ana.silva@email.com",
  "address": "Rua das Flores, 10, Lisboa",
  "phone": "912345678"
}
```

### Criar um restaurante

```http
POST http://localhost:8002/restaurants
Content-Type: application/json

{
  "name": "Pizza Byte",
  "cuisine_type": "Italiana",
  "address": "Avenida da República, 50, Lisboa",
  "active": true
}
```

### Adicionar item ao menu

```http
POST http://localhost:8002/restaurants/1/menu-items
Content-Type: application/json

{
  "name": "Pizza Margherita",
  "description": "Tomate, mozzarella e manjericão",
  "price": 8.50,
  "available": true
}
```

### Criar uma encomenda

```http
POST http://localhost:8003/orders
Content-Type: application/json

{
  "customer_id": 1,
  "restaurant_id": 1,
  "items": [
    { "menu_item_id": 1, "quantity": 2 },
    { "menu_item_id": 2, "quantity": 1 }
  ]
}
```

### Pagar uma encomenda

```http
POST http://localhost:8004/payments
Content-Type: application/json

{
  "order_id": 1,
  "payment_method": "MBWAY"
}
```

### Atualizar estado da encomenda

```http
PATCH http://localhost:8003/orders/1/status
Content-Type: application/json

{
  "status": "PREPARING"
}
```

### Consultar notificações de um cliente

```http
GET http://localhost:8005/customers/1/notifications
```

---

## Limitações intencionais

Esta aplicação é um exemplo pedagógico. Por isso, algumas funcionalidades foram propositadamente omitidas para manter o código simples e fácil de compreender:

- **Sem autenticação** — qualquer pessoa pode chamar qualquer endpoint;
- **Sem autorização** — não há controlo de permissões;
- **Sem frontend** — a interface é feita via Swagger ou cliente HTTP;
- **Pagamentos simulados** — a aprovação é baseada apenas no valor (≤ 50€);
- **Notificações simuladas** — as notificações são guardadas em base de dados e impressas no terminal, mas não são enviadas de facto;
- **SQLite** — base de dados simples, sem suporte a múltiplas instâncias do mesmo serviço;
- **Sem API Gateway** — os serviços são acedidos diretamente nas suas portas;
- **Sem mensageria assíncrona** — toda a comunicação é síncrona via HTTP;
- **Sem stock** — não há controlo de inventário;
- **Sem gestão de entregadores** — o estado OUT_FOR_DELIVERY não foi implementado;
- **Sem Kubernetes** — a orquestração é feita com Docker Compose.

---

## Possíveis evoluções futuras

Para quem quiser explorar mais, algumas ideias de evolução:

- Adicionar autenticação com JWT;
- Substituir SQLite por PostgreSQL;
- Adicionar um API Gateway (ex: Traefik, Kong);
- Introduzir mensageria assíncrona com RabbitMQ ou Kafka;
- Criar um frontend simples em React ou Vue;
- Implementar observabilidade com Prometheus e Grafana;
- Adicionar testes automatizados com pytest;
- Containerizar com Kubernetes;
- Adicionar um serviço de entregadores;
- Implementar um carrinho de compras.

---

## Estrutura do projeto

```
micromeals/
│
├── customer-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── crud.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── restaurant-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── crud.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── order-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── service_clients.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── payment-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── crud.py
│   │   └── service_clients.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── notification-service/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── crud.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── examples/
    └── requests.http
```
