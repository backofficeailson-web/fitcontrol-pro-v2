# FitControl Pro V2 — Deploy

## Local SQLite

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
flask db upgrade
python app.py
```

Acesse `http://127.0.0.1:5000/auth/login`.

## Gunicorn local

```bash
export FLASK_APP=wsgi.py
export FLASK_ENV=development
flask db upgrade
gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 4 wsgi:app
```

## Docker + PostgreSQL + Redis

```bash
docker compose up --build
# em outro terminal, se necessário:
docker compose exec web flask db upgrade
```

Acesse `http://localhost:8000`.

## PostgreSQL em produção

Configure:

```env
FLASK_ENV=production
SECRET_KEY=<segredo-forte>
WTF_CSRF_SECRET_KEY=<segredo-forte>
DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/banco
REDIS_URL=redis://host:6379/0
SESSION_COOKIE_SECURE=True
FORCE_HTTPS=True
```

## Render

Use `render.yaml` ou configure manualmente:

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 wsgi:app
```

Release command:

```bash
flask db upgrade
```

## Railway

Crie serviços PostgreSQL e Redis, configure as variáveis de ambiente e use `railway.json`.

## Fly.io

```bash
fly launch --no-deploy
fly secrets set SECRET_KEY=... WTF_CSRF_SECRET_KEY=... DATABASE_URL=... REDIS_URL=...
fly deploy
```

## Health checks

- `/healthz`: processo Flask ativo.
- `/readyz`: aplicação consegue consultar o banco.
