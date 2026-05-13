# 🐘 FitControl Pro 2.0 — PostgreSQL em Produção

> SQLite só é usado em desenvolvimento local. Em produção, **use sempre PostgreSQL**.

---

## Por quê PostgreSQL

- **Concorrência real** (múltiplos workers do gunicorn escrevendo ao mesmo tempo).
- **Backup gerenciado** nas plataformas cloud (Render, Railway, Fly, Heroku).
- **Resistência a perda de dados** (SQLite num container efêmero é desastre garantido).
- **Performance** para listagens grandes (`COUNT`, `JOIN`, `GROUP BY`).

---

## Formato da URL

O FitControl aceita **qualquer um** dos formatos abaixo (são normalizados internamente):

```
postgres://USER:PASS@HOST:5432/DB
postgresql://USER:PASS@HOST:5432/DB
postgresql+psycopg://USER:PASS@HOST:5432/DB    # recomendado
```

A normalização ocorre em `config.py::_normalize_database_url()`.

---

## Pool de conexões

Configurado em `config.py`:

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_pre_ping": True,   # reconecta automaticamente após drop
    "pool_recycle": 280,     # recicla conexões antes do timeout do PG (300s)
}
```

Recomendamos `pool_pre_ping=True` SEMPRE em produção atrás de proxy/PG gerenciado.

---

## Migrations

```bash
# criar nova migration
flask db migrate -m "describe change"

# aplicar
flask db upgrade

# voltar uma versão
flask db downgrade
```

O `scripts/release.sh` roda `flask db upgrade` automaticamente em cada deploy.

---

## Provisionando um banco

### Render
```bash
# já incluso no render.yaml: bloco `databases:`
```

### Railway
```bash
railway add --plugin postgresql
```

### Fly.io
```bash
fly postgres create --name fitcontrol-db
fly postgres attach fitcontrol-db
```

### Heroku
```bash
heroku addons:create heroku-postgresql:essential-0
```

### Docker (local)
Já incluído em `docker-compose.yml` como serviço `db`. URL gerada:
```
postgresql+psycopg://fitcontrol:fitcontrol_secret@db:5432/fitcontrol
```

---

## Backup manual

```bash
# Render/Heroku/Railway oferecem snapshots automáticos no painel.
# Backup manual via pg_dump:
pg_dump "$DATABASE_URL" > backup_$(date +%F).sql

# Restore
psql "$DATABASE_URL" < backup_2025-01-15.sql
```

---

## Migrar dados de SQLite → PostgreSQL

```bash
# 1. exportar do SQLite
sqlite3 instance/fitcontrol.db .dump > sqlite_dump.sql

# 2. converter syntax (substituições básicas)
sed -i 's/AUTOINCREMENT/SERIAL/g' sqlite_dump.sql
sed -i 's/PRAGMA.*;//g' sqlite_dump.sql

# 3. importar no Postgres
psql "$DATABASE_URL" < sqlite_dump.sql
```

Para projetos com dados sensíveis, recomendamos `pgloader` (ferramenta dedicada).

---

## Healthcheck

`GET /readyz` executa `SELECT 1` no banco — retorna `503` se a conexão falhar.
Use esse endpoint em load balancers / probes do Kubernetes / Render.
