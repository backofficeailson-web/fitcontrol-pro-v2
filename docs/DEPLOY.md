# 🚀 FitControl Pro 2.0 — Guia de Deploy em Nuvem

> Objetivo: colocar o FitControl Pro com **URL pública HTTPS**, acessível por **smartphone, tablet e PC em qualquer rede Wi-Fi/4G/5G**, **sem depender do seu computador ligado**.

---

## 📋 Pré-requisitos

- Conta em uma plataforma de nuvem (escolha 1): **Render**, **Railway**, **Fly.io** ou **Heroku**.
- Repositório Git (GitHub, GitLab ou Bitbucket).
- Banco **PostgreSQL** (oferecido pelas plataformas acima).
- (Opcional) Redis para rate limit distribuído.

---

## 🎯 Opção 1 — Render (recomendado, mais simples)

1. **Faça push do projeto** para um repositório GitHub.
2. No Render: **New + → Blueprint**.
3. Selecione seu repo. O Render lê automaticamente `render.yaml`.
4. Render irá:
   - Provisionar o PostgreSQL `fitcontrol-postgres`.
   - Injetar `DATABASE_URL` (no formato `postgres://...` — o app converte sozinho).
   - Gerar `SECRET_KEY` e `WTF_CSRF_SECRET_KEY` automaticamente.
   - Rodar `pip install -r requirements.txt && flask db upgrade`.
   - Iniciar com `gunicorn wsgi:app`.
5. Após o deploy, acesse `https://fitcontrol-pro.onrender.com` (URL exibida no painel).

✅ Healthcheck: `/healthz` · Readiness: `/readyz`

---

## 🎯 Opção 2 — Railway

```bash
railway login
railway init
railway add --plugin postgresql
railway up
```

Em **Variables** defina:

| Variável | Valor |
|---|---|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | (48 caracteres aleatórios) |
| `WTF_CSRF_SECRET_KEY` | (outro segredo) |
| `SESSION_COOKIE_SECURE` | `True` |
| `BEHIND_PROXY` | `True` |
| `LOG_TO_STDOUT` | `True` |
| `DATABASE_URL` | (auto-injetado pelo plugin) |

O `railway.json` define o start command e `/healthz`.

---

## 🎯 Opção 3 — Fly.io

```bash
fly auth login
fly launch --no-deploy           # detecta o Dockerfile
fly postgres create --name fitcontrol-db
fly postgres attach fitcontrol-db
fly secrets set \
  SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))") \
  WTF_CSRF_SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))")
fly deploy
```

Sua URL: `https://fitcontrol-pro.fly.dev`.

---

## 🎯 Opção 4 — Heroku

```bash
heroku create fitcontrol-pro
heroku addons:create heroku-postgresql:essential-0
heroku config:set FLASK_ENV=production SESSION_COOKIE_SECURE=True BEHIND_PROXY=True \
                  SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))") \
                  WTF_CSRF_SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))")
git push heroku main
```

O `Procfile` cuida do release (migrations) e do `web` (gunicorn).

---

## 🐳 Opção 5 — Docker / VPS

```bash
cp .env.production.example .env.production
# edite SECRET_KEY, WTF_CSRF_SECRET_KEY, DATABASE_URL
docker compose up --build -d
```

Para HTTPS público em VPS, coloque **Nginx + Let's Encrypt** ou **Caddy** na frente:

```caddy
fitcontrol.seudominio.com {
    reverse_proxy localhost:5000
}
```

Caddy obtém o certificado SSL automaticamente.

---

## 🔐 Variáveis de ambiente OBRIGATÓRIAS em produção

| Variável | Obrigatória | Notas |
|---|---|---|
| `SECRET_KEY` | ✅ | mínimo 24 caracteres aleatórios |
| `WTF_CSRF_SECRET_KEY` | ✅ | idem |
| `DATABASE_URL` | ✅ | PostgreSQL recomendado |
| `FLASK_ENV` | ✅ | `production` |
| `SESSION_COOKIE_SECURE` | ✅ | `True` (HTTPS) |
| `BEHIND_PROXY` | ✅ | `True` |
| `RATELIMIT_STORAGE_URI` | recomendado | `redis://...` |
| `LOG_TO_STDOUT` | recomendado | `True` |

Geração de segredos:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

---

## ✅ Pós-deploy — checklist

- [ ] `https://SUA_URL/healthz` retorna `{"status":"ok"}`
- [ ] `https://SUA_URL/readyz` retorna `{"status":"ready"}`
- [ ] `https://SUA_URL/auth/login` abre
- [ ] É possível registrar usuário e logar
- [ ] Dashboard carrega
- [ ] PDFs continuam sendo gerados
- [ ] `https://SUA_URL/manifest.json` responde JSON
- [ ] `https://SUA_URL/service-worker.js` responde JS
- [ ] No celular, é oferecido "Adicionar à tela inicial" / "Instalar"

Veja também [`ACESSO_MOBILE.md`](ACESSO_MOBILE.md) e [`POSTGRES.md`](POSTGRES.md).
