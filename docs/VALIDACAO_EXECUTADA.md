# Validação executada — FitControl Pro V2 Enterprise

Data da validação: 2026-05-11.

## Executado neste ambiente

| Validação | Resultado |
|---|---:|
| Instalação de dependências via `pip install -r requirements.txt` | OK |
| PostgreSQL 17 local instalado e iniciado | OK |
| Banco `fitcontrol_test` criado com usuário `fitcontrol` | OK |
| `flask db upgrade` com PostgreSQL real | OK |
| `pytest -q` com PostgreSQL real configurado em `DATABASE_URL` | 34 passed |
| Boot via Gunicorn usando PostgreSQL real | OK |
| `/healthz` via Gunicorn | OK |
| `docker compose config` | OK |
| Docker Engine instalado | OK |
| Docker daemon iniciado com `--iptables=false --bridge=none --ip-masq=false --ip-forward=false --storage-driver=vfs` | OK |

## Bloqueio externo encontrado

| Validação | Resultado |
|---|---|
| `docker compose up -d db redis` | Bloqueado por falha DNS/rede ao acessar Docker Hub: `lookup registry-1.docker.io ... i/o timeout`. |
| Docker build completo | Não executável neste ambiente sem acesso funcional ao Docker Hub para puxar `python:3.12-slim`, `postgres:16-alpine` e `redis:7-alpine`. |

## Correção descoberta pela validação PostgreSQL

A validação real em PostgreSQL encontrou uma incompatibilidade que o SQLite não acusa: a migration inicial usava `BOOLEAN DEFAULT 1`. PostgreSQL exige boolean literal válido. Corrigido para `server_default=sa.true()` em `migrations/versions/001_initial_schema.py`.

## Comandos principais usados

```bash
pg_ctlcluster 17 main start
runuser -u postgres -- createdb -O fitcontrol fitcontrol_test
export DATABASE_URL=postgresql+psycopg://fitcontrol:fitcontrol@127.0.0.1:5432/fitcontrol_test
flask --app wsgi db upgrade
pytest -q
gunicorn -w 1 -b 127.0.0.1:8011 wsgi:app
curl http://127.0.0.1:8011/healthz
docker compose config
```
