# ✅ FitControl Pro 2.0 — Checklist de Validação

> Execute esta lista antes de declarar a entrega completa.

## 1. Local (Python)

- [ ] `python -m venv .venv && source .venv/bin/activate`
- [ ] `pip install -r requirements.txt`
- [ ] `cp .env.example .env`
- [ ] `flask db upgrade` cria/atualiza o SQLite local
- [ ] `python app.py` inicia em `http://localhost:5000`
- [ ] `pytest -q` — todos os testes passam

## 2. Gunicorn (produção local)

- [ ] `FLASK_ENV=production SECRET_KEY=$(python -c "import secrets;print(secrets.token_urlsafe(48))") gunicorn wsgi:app --bind 0.0.0.0:5000`
- [ ] `curl http://localhost:5000/healthz` → `{"status":"ok"}`
- [ ] `curl http://localhost:5000/readyz` → `{"status":"ready"}`

## 3. PostgreSQL

- [ ] `docker compose up db` sobe Postgres
- [ ] `DATABASE_URL=postgresql+psycopg://fitcontrol:fitcontrol_secret@localhost:5432/fitcontrol flask db upgrade`
- [ ] Tabelas criadas com sucesso

## 4. Docker stack completo

- [ ] `docker compose up --build` sobe sem erros
- [ ] `http://localhost:5000` abre o login
- [ ] Registro de usuário funciona
- [ ] Dashboard carrega
- [ ] Logs aparecem em `docker compose logs -f web`

## 5. Funcionalidades de produto (não pode haver regressão)

- [ ] Login premium dark/glassmorphism abre
- [ ] “since 2018 Ailson Soares” presente
- [ ] Registro de novo coach funciona
- [ ] Dashboard com métricas, feed e gráficos
- [ ] CRUD de alunos completo
- [ ] Avaliações funcionam (Pollock, etc.)
- [ ] Treinos funcionam
- [ ] Protocolos (Pollock 3, Hipertrofia, etc.) listados
- [ ] Relatórios abrem
- [ ] **PDFs continuam sendo gerados** (`WeasyPrint`)
- [ ] Páginas 404 / 403 / 500 / `/offline` premium

## 6. PWA

- [ ] `GET /manifest.json` retorna JSON válido
- [ ] `GET /service-worker.js` retorna JS
- [ ] No Chrome desktop, ícone “Instalar” aparece na barra
- [ ] No Android Chrome, banner de instalação aparece
- [ ] No iPhone Safari, banner com dica de “Adicionar à Tela de Início” aparece
- [ ] App abre em tela cheia após instalação
- [ ] Recarregar a página sem internet exibe `/offline`

## 7. Responsividade

- [ ] No celular (≤ 600px) layout em coluna única
- [ ] Hamburger menu funciona
- [ ] Tabelas têm scroll horizontal sem quebrar layout
- [ ] Botões/inputs com altura ≥ 44px (touch friendly)
- [ ] Sem zoom forçado em inputs no iOS

## 8. Segurança

- [ ] `Content-Security-Policy` presente nos headers
- [ ] `X-Frame-Options: DENY`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `Strict-Transport-Security` em produção HTTPS
- [ ] `SESSION_COOKIE_SECURE=True` em produção
- [ ] App **se recusa a iniciar** em produção sem `SECRET_KEY` forte
- [ ] Rate limit no `/auth/login` (10/min)

## 9. Deploy externo (escolher 1)

- [ ] Render: blueprint deploy, URL HTTPS pública responde
- [ ] Railway: build + start funciona, PG conectado
- [ ] Fly.io: `fly deploy` ok, `/healthz` passa
- [ ] Heroku: `release` migrations rodam antes do web

## 10. Acesso multi-dispositivo

- [ ] Smartphone Android no 4G abre a URL pública
- [ ] iPhone no Wi-Fi diferente abre a URL pública
- [ ] Tablet abre normalmente
- [ ] PC em outra rede abre normalmente
- [ ] Computador pessoal de desenvolvimento DESLIGADO — app continua online
