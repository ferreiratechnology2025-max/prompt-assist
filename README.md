# QualiPrompt

Sistema local de engenharia de prompts com validacao rigorosa e memoria adaptativa.

## Requisitos

- Windows 10/11 (64-bit)
- Python 3.10+
- Node.js 18+
- Ollama (com modelo Qwen2.5-14B)
- 12 GB VRAM (recomendado)

## Instalacao Rapida

1. **Instalar Ollama**: https://ollama.com/download/windows
2. **Configurar modelo**:
   ```
   scripts\setup_ollama.bat
   ```
3. **Inicializar banco**:
   ```
   cd backend
   pip install -r requirements.txt
   python ..\scripts\init_db.py
   ```
4. **Copiar .env** (opcional, usar defaults se pular):
   ```
   copy backend\.env.example backend\.env
   ```
   Edite `backend\.env` para ajustar `ADMIN_TOKEN` e `MODEL_VERSION`.

5. **Instalar frontend**:
   ```
   cd frontend
   npm install
   ```

## Iniciar o Sistema

### Opcao 1: Tudo de uma vez
```
scripts\start_all.bat
```

### Opcao 2: Manualmente (2 terminais)

**Terminal 1 - Backend**:
```
cd backend
python run.py
```
Acessar em http://localhost:8000/docs

**Terminal 2 - Frontend**:
```
cd frontend
npm run dev
```
Acessar em http://localhost:5173

## Seguranca

Endpoints administrativos exigem token no header:

```
X-Admin-Token: qualiprompt-admin-token-change-me-in-production
```

| Endpoint | Autenticacao |
|----------|-------------|
| `GET /api/memory/entries` | Requer token admin |
| `DELETE /api/memory/entries/{id}` | Requer token admin |
| `PUT /api/memory/epsilon/{value}` | Requer token admin |
| `GET /api/memory/stats` | Publico |
| `GET /api/validate` | Publico |
| `GET /api/templates/*` | Publico |

O token padrao esta em `backend/.env` (`ADMIN_TOKEN`). Altere para producao.

## Uso

1. Acesse http://localhost:5173
2. Selecione um template na sidebar (SWOT, Imagem, Pesquisa)
3. Preencha os campos solicitados
4. Clique em "Gerar Prompt"
5. Aguarde a validacao (30-90s, dependendo da GPU)
6. Veja o score (0-100) com circulo colorido
7. Copie ou baixe o prompt gerado

## Comercial

O QualiPrompt oferece:

- **Validador de 5 camadas**: estrutura (20%), ambiguidade (20%), semantica via LLM (25%), restricoes (15%), SMART via LLM (20%)
- **Memoria adaptativa e-greedy**: 80% explora o melhor conhecido, 20% explora novas alternativas. A memoria nunca acumula lixo — substitui apenas quando o novo prompt e estritamente melhor. Isolada por versao do modelo (via `MODEL_VERSION`)
- **Motor de refinamento**: loop de ate 3 iteracoes que corrige automaticamente o prompt com base no feedback do validador
- **100% local**: nenhum dado sai da sua maquina. Tudo roda em Ollama + SQLite (WAL mode)
- **API REST documentada**: http://localhost:8000/docs
- **Autenticacao em endpoints admin**: via token configravel
- **Templates via JSON**: crie seus proprios templates sem modificar codigo

## Roadmap do Projeto

| Fase | Descricao | Status |
|------|-----------|--------|
| 1 | Setup + estrutura de diretorios | Concluido |
| 2 | Configuracao Ollama + modelo Qwen2.5-14B | Concluido |
| 3 | Validador de 5 camadas | Concluido |
| 4 | Motor de geracao de prompts + templates | Concluido |
| 5 | Memoria com evolucao (e-greedy) | Concluido |
| 6 | API FastAPI (11 endpoints) | Concluido |
| 7 | Frontend Vue 3 (sidebar + chat + score) | Concluido |
| 8 | Integracao + testes + documentacao | Concluido |

## Arquitetura do Projeto

```
D:\prompt_Assist\
├── backend\
│   ├── app\
│   │   ├── api\routes\        # Endpoints REST (4 routers)
│   │   │   ├── templates.py   # GET list, GET detail, POST generate
│   │   │   ├── validate.py    # POST validate
│   │   │   ├── memory.py      # GET stats, GET entries, DELETE, PUT epsilon
│   │   │   └── health.py      # GET health, GET health/llm
│   │   ├── core\              # Validador, gerador, memoria
│   │   ├── services\          # LLM wrapper, templates
│   │   ├── models\            # Schemas Pydantic
│   │   └── api\dependencies.py # Injecao de dependencias
│   ├── requirements.txt
│   ├── .env.example
│   ├── .env.production
│   └── run.py
├── frontend\
│   └── src\
│       ├── components\        # 8 componentes Vue 3
│       ├── composables\       # useTemplates, useGeneration
│       └── services\          # Axios API client
├── scripts\                   # .bat de setup/inicio
├── storage\
│   ├── database\              # SQLite (criado em runtime)
│   ├── logs\
│   └── templates\             # swot.json, image.json, research_chain.json
└── README.md
```

## API Endpoints

| Metodo | Rota | Descricao |
|--------|------|-----------|
| GET | `/api/templates` | Lista templates disponiveis |
| GET | `/api/templates/{name}` | Detalhe completo do template |
| GET | `/api/templates/{name}/schema` | Apenas campos obrigatorios (para o form) |
| POST | `/api/templates/generate` | Gera prompt a partir do template + campos |
| POST | `/api/validate` | Valida um prompt existente |
| GET | `/api/memory/stats` | Estatisticas da memoria adaptativa |
| GET | `/api/memory/entries` | Lista entradas da memoria (admin) |
| DELETE | `/api/memory/entries/{id}` | Remove entrada especifica (admin) |
| PUT | `/api/memory/epsilon/{value}` | Ajusta taxa de exploracao em tempo real |
| GET | `/api/health` | Status geral do sistema (LLM, DB, memoria) |
| GET | `/api/health/llm` | Detalhes da conexao com Ollama |

## Estrutura dos Templates

Os templates estao em `storage/templates/` no formato JSON:

```json
{
  "name": "swot_analysis",
  "version": "1.0",
  "assistant_role": "Estrategista de negocios senior",
  "required_fields": [
    {"name": "produto", "type": "text", "question": "Qual o produto?"}
  ],
  "task_description": "Descricao detalhada da tarefa...",
  "output_format": "Formato esperado da saida...",
  "constraints_default": ["Restricao 1", "Restricao 2"]
}
```

## Proximos Passos (Recomendacoes)

| Prioridade | Melhoria | Justificativa |
|-----------|----------|---------------|
| Alta | **Suporte a Docker** | Elimina instalacao manual de Python/Node/Ollama. Unico comando para subir |
| Alta | **Editor de templates no frontend** | Criar/editar templates sem mexer em JSON |
| Alta | **Export/import da memoria** | Compartilhar prompts validados entre equipes |
| Media | **Comparacao lado a lado** | Ver antes/depois do refinamento |
| Media | **Mais templates** | Segmentar por industria (juridico, saude, tech, educacao) |
| Media | **Batch generation** | Gerar varios prompts de uma vez |
| Media | **Rate limiting** | Proteger API em uso compartilhado |
| Baixa | **Multi-usuario** | Login e separacao de memorias por usuario |
| Baixa | **Plugin para VS Code / JetBrains** | Usar o validador dentro do IDE |
| Baixa | **Modo offline total** | Cache do modelo Ollama embarcado |

## Troubleshooting

| Problema | Solucao |
|----------|---------|
| "Ollama nao conecta" | Execute `ollama serve` |
| Modelo nao encontrado | Execute `ollama pull qwen2.5:14b` e `ollama create qualiprompt-engine -f Modelfile.qualiprompt` |
| Porta 8000 ocupada | Altere `OLLAMA_BASE_URL` no `.env` ou mate o processo |
| Geracao lenta | Verifique VRAM com `nvidia-smi` |
| Erro de conexao API | Backend precisa estar rodando antes do frontend |
| `403 Forbidden` em endpoints admin | Envie header `X-Admin-Token` com o valor correto |
| `__init__()` got multiple values | Verifique se `.env` nao tem espacos extras |
| Frontend nao carrega | Abra o console do navegador (F12) para ver erros de rede |
| "database is locked" | WAL mode ativo — deve ser raro. Se ocorrer, aguarde e tente novamente |

## Licenca

Uso comercial mediante licenca.
