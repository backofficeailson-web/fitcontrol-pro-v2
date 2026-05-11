# FitControl Pro V2 Enterprise

Sistema SaaS fitness premium em Flask/Python com autenticação, alunos, avaliações físicas, treinos, motor de treino por regras, relatórios em PDF, UI dark/glassmorphism, PWA e deploy real.

Branding preservado: **since 2018 Ailson Soares**.

## Rodar localmente

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
flask db upgrade
python app.py
```

Acesse: `http://127.0.0.1:5000/auth/login`.

## Rodar com Gunicorn

```bash
gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 4 --timeout 120 wsgi:app
```

## Rodar com Docker

```bash
docker compose up --build
```

## Produção

Use PostgreSQL e Redis. Consulte `docs/DEPLOY.md`.

## Validação rápida

```bash
pytest -q
flask db upgrade
flask --app wsgi:app routes
```

## Estrutura principal

```text
app/                  arquitetura-alvo modular
models/               modelos SQLAlchemy atuais
repositories/         queries isoladas por domínio
services/             regras de negócio
routes/               blueprints Flask
schemas/              WTForms
static/               CSS, JS, PWA, uploads
templates/            Jinja2 + PDFs
migrations/           Alembic/Flask-Migrate
tests/                suíte automatizada
docker/ scripts/ docs/
```
