# 📱 FitControl Pro — Acesso em Smartphone, Tablet e PC

> **Pergunta-chave:** “Funciona no celular da minha esposa, fora do meu Wi-Fi, em 4G?”
> **Resposta:** SIM — desde que o FitControl esteja publicado em nuvem com **URL pública HTTPS**.

---

## 🔍 Por que `localhost` e `192.168.x.x` não servem

Quando você roda `python app.py` no seu computador:

- `http://localhost:5000` → só funciona **no próprio computador**.
- `http://127.0.0.1:5000` → idem.
- `http://192.168.0.x:5000` → só funciona em dispositivos **na mesma rede Wi-Fi**.

Para acessar de **qualquer rede** (Wi-Fi do trabalho, Wi-Fi da casa de alguém, 4G/5G):

✅ É **obrigatório** publicar o app em nuvem (Render, Railway, Fly.io, Heroku, VPS).
✅ É **obrigatório** ter uma **URL pública HTTPS** (ex.: `https://fitcontrol-pro.onrender.com`).
✅ Seu computador pessoal **não precisa estar ligado**.

> Veja o passo a passo de publicação em [`DEPLOY.md`](DEPLOY.md).

---

## 📲 Como abrir no smartphone

### Android (Chrome / Edge / Brave)

1. Abra `https://SUA_URL_PUBLICA` no Chrome.
2. Faça login normalmente.
3. Você verá um banner **“Instalar FitControl”** (ou um botão flutuante).
4. Toque em **Instalar**. O app aparece como ícone na tela inicial.
5. Pronto — abre em tela cheia, sem barra do navegador.

### iPhone / iPad (Safari)

iOS **não tem botão automático de instalação**. Faça manualmente:

1. Abra `https://SUA_URL_PUBLICA` no **Safari** (não Chrome/Firefox no iOS).
2. Toque em **Compartilhar** (ícone ↑).
3. Role e toque em **Adicionar à Tela de Início**.
4. Confirme o nome “FitControl”.
5. Pronto — ícone na home, abre em tela cheia.

O app exibe uma **dica visual** no rodapé do iPhone na primeira visita.

---

## 💻 Tablets e PCs

- **iPad / Android tablet** → mesma instrução do celular.
- **Notebook / desktop** (Windows, macOS, Linux) → abra a URL no Chrome/Edge → ícone “Instalar” na barra de endereço.

---

## 📶 Funciona em 4G / 5G?

Sim. Como o app está em nuvem com URL pública:

- Wi-Fi de casa → OK
- Wi-Fi do trabalho → OK
- Wi-Fi de cafeteria/shopping → OK
- 4G/5G da operadora → OK
- Roaming internacional → OK

O FitControl é uma **aplicação web HTTPS** — qualquer conexão à internet funciona.

---

## 🔄 PWA — recursos avançados

| Recurso | Comportamento |
|---|---|
| **Tela cheia** | Sim, sem barra do navegador |
| **Ícone na home** | Sim |
| **Splash screen** | Sim (cor `#050912`) |
| **Offline básico** | Página `/offline` exibida quando não há internet; assets em cache continuam |
| **Atualizações** | Service worker atualiza em background; recarregue para ver |
| **Notificações** | Não habilitadas nesta versão |

---

## 🧪 Como testar antes de publicar

1. Garanta que o app está rodando em produção (`gunicorn wsgi:app`).
2. Acesse `https://SUA_URL/healthz` → deve responder `{"status":"ok"}`.
3. Conecte seu celular em **4G** (desligue o Wi-Fi).
4. Abra `https://SUA_URL` no celular.
5. Faça login e use normalmente.
6. Adicione à tela inicial.

Se algum desses passos falhar, consulte [`DEPLOY.md`](DEPLOY.md#-pós-deploy--checklist).

---

## 🆘 Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| “Não consegue se conectar” no celular | Você está testando `localhost` ou IP local | Use a **URL pública HTTPS** do deploy |
| “Conexão não é segura” | Sem certificado HTTPS | Plataformas como Render/Fly fornecem HTTPS automático |
| Não aparece botão de instalar no Android | URL não é HTTPS, ou manifest com erro | Acesse `/manifest.json` no navegador — deve ser JSON válido |
| iPhone não instala | iOS exige Safari + “Adicionar à Tela de Início” manual | Siga a seção iPhone acima |
| App fica em branco no 4G | Service worker ainda não cacheou; abra primeiro com internet | Recarregue uma vez online |
