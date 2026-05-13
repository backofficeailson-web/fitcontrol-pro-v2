# 🪟 FitControl Pro V2 — Guia Windows

> Como rodar o FitControl Pro no Windows 10/11 em **5 minutos**.

---

## ⚡ Instalação automática (recomendada)

1. **Extraia o ZIP** em `C:\FitControl Pro V2\fitcontrol-pro-v2\`
2. **Abra o terminal** dentro da pasta (CMD ou PowerShell)
3. Execute:
   ```cmd
   setup_windows.bat
   ```
4. Aguarde 2-3 minutos. O script:
   - Cria a virtualenv `.venv`
   - Atualiza o pip
   - Instala todas as dependências core
   - Pergunta se quer instalar o WeasyPrint (PDFs) — opcional
   - Copia o `.env.example` para `.env`
   - Aplica as migrations do banco

5. Para iniciar o app:
   ```cmd
   run_windows.bat
   ```
6. Acesse: **http://localhost:5000**

---

## 🛠️ Instalação manual

```cmd
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
set FLASK_APP=app.py
flask db upgrade
python app.py
```

---

## 📄 WeasyPrint (PDFs) no Windows

WeasyPrint precisa do **GTK3 runtime** para gerar PDFs no Windows.

### Opção A — Instalar GTK3 e habilitar PDFs

1. Baixe o instalador GTK3:
   https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Execute o `.exe` (Next, Next, Finish)
3. **Reinicie o terminal**
4. Ative a venv e instale:
   ```cmd
   .venv\Scripts\activate
   pip install -r requirements-pdf.txt
   ```
5. Pronto — PDFs funcionam.

### Opção B — Pular WeasyPrint (dev local sem PDFs)

Não instale nada. O app **funciona normalmente** — apenas as rotas de exportação em PDF retornarão erro tratado. Toda a outra funcionalidade (login, alunos, treinos, avaliações, dashboard, protocolos) opera 100%.

Em **produção (Render/Railway/Fly/Docker)** os PDFs funcionam automaticamente — o Dockerfile já inclui todas as bibliotecas nativas necessárias.

---

## 🚀 Produção local no Windows (Waitress)

Gunicorn **não roda no Windows**. Use o **Waitress** (já incluído no requirements.txt):

```cmd
run_windows_prod.bat
```

Ou manualmente:
```cmd
.venv\Scripts\activate
set FLASK_ENV=production
set SECRET_KEY=<48 caracteres aleatórios>
python -m waitress --listen=0.0.0.0:5000 --threads=8 wsgi:app
```

**Importante:** este modo é para **testes locais de produção**. Para acesso público real (qualquer rede / smartphone / 4G), você ainda precisa publicar em nuvem — veja [`DEPLOY.md`](DEPLOY.md).

---

## 🐛 Troubleshooting Windows

### `'flask' não é reconhecido como um comando`
A venv não está ativada. Execute:
```cmd
.venv\Scripts\activate
```

### `ModuleNotFoundError: No module named 'flask'`
As dependências não foram instaladas. Execute:
```cmd
.venv\Scripts\activate
pip install -r requirements.txt
```

### `ERROR: Could not find a version that satisfies the requirement psycopg-binary==X.X.X`
Versão antiga de `requirements.txt`. Esta versão Windows-friendly usa `>=` em vez de `==`, então não acontece mais.

### `cannot load library 'libgobject-2.0-0'` (WeasyPrint)
GTK3 não instalado ou terminal não reiniciado. Instale o GTK3 e abra um terminal novo.

### `psycopg2` falha ao compilar
Use `psycopg2-binary` (já está no requirements). Se ainda assim falhar, no Windows o `psycopg[binary]` (psycopg3) é a opção primária.

### Porta 5000 ocupada
```cmd
set FLASK_PORT=5001
python app.py
```

### `flask db upgrade` falha
```cmd
set FLASK_APP=app.py
flask db upgrade
```

---

## 📂 Caminhos típicos no Windows

```
C:\FitControl Pro V2\fitcontrol-pro-v2\
├── .venv\                       <- ambiente virtual (criado pelo setup)
├── instance\fitcontrol.db       <- banco SQLite local
├── logs\                        <- logs do app
├── static\uploads\              <- uploads de usuários
├── setup_windows.bat            <- ⭐ executar primeiro
├── run_windows.bat              <- desenvolvimento
├── run_windows_prod.bat         <- produção local (Waitress)
└── ...
```

---

## ✅ Checklist Windows

- [ ] Python 3.10+ instalado e no PATH
- [ ] `setup_windows.bat` executado sem erros
- [ ] `.venv` criada
- [ ] `requirements.txt` instalado
- [ ] `.env` existe
- [ ] `flask db upgrade` rodou
- [ ] `python app.py` ou `run_windows.bat` abre em http://localhost:5000
- [ ] Login premium dark/glassmorphism aparece
- [ ] Registro de usuário funciona
- [ ] Dashboard carrega
- [ ] (Opcional) GTK3 instalado para PDFs

---

## 🌐 Próximo passo

Rodar no Windows funciona apenas no **seu computador**. Para acessar de **smartphone, tablet, 4G/5G, qualquer rede**, você precisa publicar em nuvem. Veja:

- [`DEPLOY.md`](DEPLOY.md) — Render, Railway, Fly.io, Heroku
- [`ACESSO_MOBILE.md`](ACESSO_MOBILE.md) — instalação como app no celular
