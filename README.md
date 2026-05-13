# 🏋️ FitControl Pro 2.0

> **Premium SaaS Fitness Platform** — Cloud, Mobile & Network Production Ready
> *since 2018 Ailson Soares*

Sistema profissional para personal trainers gerenciarem alunos, avaliações físicas, treinos com IA, protocolos (Pollock, etc.) e relatórios PDF. Acessível por **smartphone, tablet e PC em qualquer rede Wi-Fi/4G/5G** através de URL pública HTTPS.

---

## 🎯 Por que esta versão é diferente

| Aspecto | Antes | Agora |
|---|---|---|
| Banco em produção | SQLite local | **PostgreSQL** com auto-normalização de URL |
| Servidor | Flask dev | **Gunicorn** WSGI |
| Acesso | só localhost / Wi-Fi local | **URL pública HTTPS**, 4G/5G, qualquer rede |
| Deploy | manual no PC | **Render / Railway / Fly.io / Heroku / Docker** |
| Mobile | tabela quebrava | **PWA instalável** + responsive mobile-first |
| Segurança | básica | CSP, HSTS, X-Frame, rate limit, SECRET_KEY obrigatório |
| Performance | counts em Python | aggregates em SQL, GROUP BY, paginação |
| Observabilidade | logs em arquivo | logs stdout + `/healthz` + `/readyz` |

---

## 🚀 Quick start (local dev)

### 🐧 Linux / Mac
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask db upgrade
python app.py
# abre em http://localhost:5000
```

### 🪟 Windows (setup automático)
```cmd
setup_windows.bat
run_windows.bat
```
Detalhes: [`docs/WINDOWS.md`](docs/WINDOWS.md)

### 📄 PDFs (WeasyPrint) — opcional
```bash
pip install -r requirements-pdf.txt
```
No Windows requer GTK3 runtime. Em Docker/Cloud já funciona automaticamente.

## ☁️ Deploy em nuvem (URL pública)

Escolha sua plataforma:

- 🟢 **[Render](docs/DEPLOY.md#-opção-1--render-recomendado-mais-simples)** — blueprint `render.yaml` (1 clique)
- 🔵 **[Railway](docs/DEPLOY.md#-opção-2--railway)** — `railway up`
- 🟣 **[Fly.io](docs/DEPLOY.md#-opção-3--flyio)** — `fly deploy`
- 🟡 **[Heroku](docs/DEPLOY.md#-opção-4--heroku)** — `git push heroku main`
- 🐳 **[Docker / VPS](docs/DOCKER.md)** — `docker compose up`

Guia completo: [`docs/DEPLOY.md`](docs/DEPLOY.md).

## 📱 Acesso multi-dispositivo

Após o deploy, abra `https://SUA_URL` em:

- Android Chrome → banner "Instalar" automático
- iPhone Safari → Compartilhar → "Adicionar à Tela de Início"
- iPad, tablet, PC → mesmo fluxo

Detalhes: [`docs/ACESSO_MOBILE.md`](docs/ACESSO_MOBILE.md).

---

## 🗂️ Estrutura

```
fitcontrol-pro-v2/
├── app.py                    # Application factory + security headers + ProxyFix
├── wsgi.py                   # Gunicorn entrypoint
├── config.py                 # Dev / Testing / Production configs
├── extensions.py             # Flask-Login, CSRF, Migrate, Limiter (Redis-ready)
├── Dockerfile                # Multi-stage image (WeasyPrint + psycopg)
├── docker-compose.yml        # web + Postgres + Redis
├── Procfile                  # Heroku release + web
├── runtime.txt               # python-3.12.5
├── render.yaml               # Render blueprint
├── railway.json              # Railway start config
├── fly.toml                  # Fly.io machine config
├── scripts/
│   ├── start.sh              # flask db upgrade && gunicorn
│   └── release.sh            # flask db upgrade
├── routes/
│   ├── auth.py / dashboard.py / alunos.py / avaliacoes.py
│   ├── treinos.py / protocolos.py / relatorios.py / api.py
│   ├── health.py             # /healthz /readyz
│   └── pwa.py                # /manifest.json /service-worker.js /offline
├── models/ services/ repositories/ schemas/ utils/
├── templates/
│   ├── base.html             # PWA meta tags + mobile hamburger
│   ├── components/  pdf/  auth/  alunos/  avaliacoes/
│   ├── treinos/  protocolos/  dashboard/  relatorios/
│   └── errors/ {404,403,500,offline}.html
├── static/
│   ├── css/ {tokens,base,components,layout,dashboard,print,mobile}.css
│   ├── js/  {app,auth,pwa,service-worker}.js
│   └── img/ {favicon.ico, icons/icon-192.png, icon-512.png, apple-touch-icon.png}
├── migrations/               # Alembic
├── tests/                    # 43 testes pytest, todos passando
├── docs/
│   ├── DEPLOY.md  ACESSO_MOBILE.md  POSTGRES.md  DOCKER.md  CHECKLIST.md
└── requirements.txt
```

---

## 🧪 Validação

```bash
pytest -q                                  # 43 passed ✅
gunicorn wsgi:app --bind 0.0.0.0:5000     # produção local
curl localhost:5000/healthz                # liveness probe
curl localhost:5000/readyz                 # readiness probe (DB)
curl localhost:5000/manifest.json          # PWA manifest
docker compose up --build                  # stack completa local
```

Lista detalhada de validação: [`docs/CHECKLIST.md`](docs/CHECKLIST.md).

---

## 🔒 Segurança

- `SECRET_KEY` obrigatório em produção (rejeita default/curto)
- `SESSION_COOKIE_SECURE`, `HTTPONLY`, `SAMESITE=Lax`
- CSRF em todos POSTs (Flask-WTF)
- Headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- Rate limit (10/min em login, 5/min em registro) — Redis ready
- Lockout de conta após tentativas de brute-force

---

## 📜 Licença

Proprietário — © 2018-2026 Ailson Soares. Todos os direitos reservados.
