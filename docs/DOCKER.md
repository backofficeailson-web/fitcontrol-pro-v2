# 🐳 FitControl Pro 2.0 — Docker

## Build local

```bash
docker build -t fitcontrol-pro:2.0 .
```

## Stack completa (web + PostgreSQL + Redis)

```bash
cp .env.production.example .env.production
docker compose up --build
```

Acesse `http://localhost:5000`.

## Serviços do `docker-compose.yml`

| Serviço | Porta | Função |
|---|---|---|
| `db` | 5432 | PostgreSQL 16 |
| `redis` | 6379 | Rate limit / cache |
| `web` | 5000 | Gunicorn + Flask |

Volumes persistentes:
- `fitcontrol_pgdata` — dados do banco
- `fitcontrol_uploads` — uploads de usuário
- `fitcontrol_logs` — logs do app

## Comandos úteis

```bash
docker compose logs -f web              # acompanhar logs
docker compose exec web flask db upgrade
docker compose exec db psql -U fitcontrol -d fitcontrol
docker compose down                      # parar
docker compose down -v                   # parar + apagar dados
```

## Variáveis no compose

Sobrescreva no `.env.production` ou direto no `docker-compose.yml`.
Em produção real, **nunca** use o `SECRET_KEY` de exemplo.

## Healthcheck

A própria imagem expõe `HEALTHCHECK` em `/healthz` — orquestradores
(Kubernetes, Swarm, ECS) detectam falhas e reiniciam o container.
