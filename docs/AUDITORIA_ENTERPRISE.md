# Auditoria Enterprise aplicada

Base usada: `fitcontrol-pro-python`, porque era a base Flask coesa, testável e sem duplicações graves. O ZIP `fitcontrol-pro-final-main` foi tratado como referência histórica de regressões/Frankenstein, pois contém múltiplas versões, backups e projetos misturados.

## Correções aplicadas

- `.env.example` mantido simples, mas agora resolvido em `config.py` com caminho absoluto universal para SQLite.
- Produção bloqueia SQLite e exige `DATABASE_URL` PostgreSQL.
- Suporte a `postgres://`, `postgresql://` e `postgresql+psycopg://`.
- Adicionado `psycopg[binary]`, `gunicorn` e `redis`.
- Engine tuning com `pool_pre_ping`, `pool_recycle`, `pool_size` e `max_overflow` para PostgreSQL.
- Migration inicial validada contra PostgreSQL real; corrigido `BOOLEAN DEFAULT 1` para `server_default=sa.true()`.
- Rate limit preparado para Redis via `REDIS_URL`/`RATELIMIT_STORAGE_URI`.
- Headers de segurança aplicados globalmente.
- Endpoints `/healthz` e `/readyz` adicionados.
- PWA instalável com `manifest.json`, service worker e ícones SVG.
- Safe-area iOS e reforço mobile-first.
- Dashboard semanal otimizado com aggregate queries, evitando carregar todo o histórico em memória.
- Treinos com `selectinload` para reduzir N+1 em exercícios.
- Dockerfile, Compose, Procfile, Render, Railway e Fly.io adicionados.
- Dockerfile ajustado para executar `flask db upgrade` no startup script antes do Gunicorn.
- Estrutura `app/` criada como camada-alvo para evolução modular sem quebrar imports atuais.

## Validação adicional executada

- PostgreSQL local real: OK.
- Migration PostgreSQL: OK.
- Testes com `DATABASE_URL` PostgreSQL: 34 passed.
- Gunicorn conectado ao PostgreSQL: OK.
- Docker Compose syntax/config: OK.
- Docker daemon: instalado e iniciado com flags compatíveis ao ambiente restrito.

## Limite externo restante

O `docker compose up` não concluiu porque o ambiente não conseguiu resolver/acessar Docker Hub (`registry-1.docker.io`). Isso impede puxar imagens base e imagens PostgreSQL/Redis. Não é falha do projeto; é bloqueio de rede/DNS do ambiente de execução.
