# 🦴🤖 Módulos Postura & IA Lab — FitControl Pro V2

## 1. Avaliação Postural

Módulo profissional para análise biomecânica completa do aluno.

### Funcionalidades
- Registro de **9 segmentos corporais**: cabeça, cervical, ombros, escápulas, coluna torácica, lombar, quadril, joelhos, pés
- **Alinhamentos** frontal e lateral (texto livre técnico)
- **Indicadores clínicos**: grau de desvio (leve/moderado/acentuado), dor relatada, limitação funcional
- **Upload de até 4 imagens**: frontal, lateral direita, lateral esquerda, posterior
- **Comparação antes/depois** entre avaliações
- **Observações técnicas e do profissional**
- **Isolamento total** entre usuários (cada coach só vê seus próprios dados)

### Rotas
| Rota | Descrição |
|---|---|
| `/postura/` | Lista geral (todas avaliações do usuário) |
| `/postura/aluno/<id>` | Lista por aluno |
| `/postura/novo/<aluno_id>` | Nova avaliação |
| `/postura/<id>` | Detalhe completo |
| `/postura/<id>/editar` | Editar |
| `/postura/<id>/excluir` | Excluir (POST) |
| `/postura/<id>/comparar/<anterior_id>` | Comparativo de evolução |

### Validações
- Imagens: PNG, JPG, JPEG, WebP (MIME + extensão validados)
- Tamanho máximo: 16 MB por arquivo
- Nomes randomizados (`u<user>_<timestamp>_<token>_<nome>.png`)
- Hash SHA-256 calculado em cada upload

---

## 2. IA Lab — Análise de Arquivos

Área de IA para upload e análise técnica de arquivos.

### Tipos suportados
| Tipo | Extensões | Análise realizada |
|---|---|---|
| **ZIP** | `.zip` | Estrutura, dependências, segurança (eval/exec, SECRET_KEY hardcoded), performance (.all() sem limit), arquitetura (Dockerfile, requirements, tests, migrations) |
| **PDF** | `.pdf` | Validação de assinatura, tamanho, integridade |
| **Imagem** | `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif` | Dimensões, peso, formato, recomendações |
| **Código** | `.py`, `.html`, `.css`, `.js`, `.json`, `.sql`, `.yml`, `.yaml`, `.toml`, `.ini`, `.cfg` | Linting heurístico, padrões de risco, sugestão de correção |
| **Documento** | `.txt`, `.md` | Métricas básicas |

### Scores gerados (0-100)
- **Segurança** (eval/exec, hardcoded secrets, DEBUG=True)
- **Performance** (queries sem limit, N+1)
- **Arquitetura** (Dockerfile, requirements, tests, migrations)
- **Responsividade** (viewport, mobile-first)
- **Banco** (SQLite em produção, indexes)

### Rotas
| Rota | Descrição |
|---|---|
| `/ai/` | Dashboard com histórico |
| `/ai/upload` | POST — upload de arquivo |
| `/ai/<id>` | Detalhe da análise |
| `/ai/<id>/status` | JSON com status/progresso (polling) |
| `/ai/<id>/reprocessar` | POST — reprocessar |
| `/ai/<id>/excluir` | POST — excluir |

### Fila de processamento
- Status: `pending` → `processing` → `done` / `failed`
- Progresso: 0 → 5 → 20 → 80 → 100
- Histórico permanente em `ai_analyses`
- Relatório técnico completo em Markdown
- Métricas em JSON serializado

### Rate limit
- Upload: 20 análises/minuto por usuário
- Reprocessar: 10/minuto

### Substituição por LLM externo
O `services/ai_engine_analysis.py` faz análise **determinística local** (heurística). Para integrar com OpenAI/Anthropic/Gemini, basta substituir os métodos `_analyze_*` por chamadas API. O contrato de retorno é estável:

```python
{
    "resumo": str,
    "erros": list[str],
    "sugestoes": list[str],
    "relatorio": str (markdown),
    "metricas": dict,
    "scores": {"seguranca","performance","arquitetura","responsividade","banco"},
    "codigo_corrigido": str | None,
}
```

---

## 3. Sistema de Uploads (compartilhado)

Service: `services/upload_service.py`

### Categorias
```
static/uploads/
├── images/        # imagens gerais
├── reports/       # PDFs de relatórios
├── posture/       # imagens de avaliação postural
├── ai_analysis/   # arquivos enviados ao IA Lab
└── temp/          # arquivos temporários
```

### Segurança aplicada
- Validação de **tamanho** (`MAX_CONTENT_LENGTH`)
- Validação de **extensão** (allowlist por categoria)
- Validação de **MIME type** (declarado + adivinhado)
- Sanitização de nome via `secure_filename`
- Nome final randomizado: `u<owner_id>_<timestamp>_<token>_<original>`
- Hash **SHA-256** para integridade
- Path traversal bloqueado em `delete()`

---

## 4. Testes

```bash
pytest tests/test_postura.py -v    # 5 testes
pytest tests/test_ai_lab.py -v     # 6 testes
pytest -q                          # 54 testes total
```

Todos passam contra SQLite (dev) e PostgreSQL (produção).
