# Metabuscador Limpo 🔍

## 📖 Descrição
O **Metabuscador Limpo** é um projeto experimental que reúne resultados de múltiplos motores de busca (Google, Bing e DuckDuckGo), aplicando filtros inteligentes para remover duplicidades, ocultar anúncios e organizar os links conforme perfis de interesse (científico, jornalístico, compras).  
Além disso, o sistema controla o limite diário de 100 buscas por usuário, garantindo transparência e evitando custos inesperados.

---

## 🚀 Funcionalidades
- Integração com **Google, Bing e DuckDuckGo**
- Remoção de duplicidades e anúncios patrocinados
- Perfis de busca configuráveis:
  - 🔬 Científico → prioriza `.edu`, `.gov`, arXiv, PubMed, etc.
  - 📰 Jornalístico → prioriza veículos de imprensa confiáveis
  - 🛒 Compras → prioriza comparadores e reviews
- Controle de limite diário (100 buscas por usuário)
- Interface web simples e responsiva em React + TailwindCSS

---

## 🛠️ Tecnologias
| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11+ + FastAPI + httpx |
| Frontend | React 18 + Vite + TailwindCSS |
| Cache/DB | Memória Python (pronto para Redis/PostgreSQL) |
| APIs externas | Bing Search API, DuckDuckGo HTML, Google Custom Search (opcional) |

---

## 📦 Instalação

### Backend

```bash
cd backend
pip install -r requirements.txt

# Copie o arquivo de variáveis de ambiente e preencha suas chaves
cp .env.example .env

# Inicie o servidor
uvicorn main:app --reload
```

O servidor iniciará em `http://localhost:8000`.  
Documentação interativa disponível em `http://localhost:8000/docs`.

#### Variáveis de ambiente (`backend/.env`)

| Variável | Descrição | Obrigatório |
|---|---|---|
| `BING_API_KEY` | Chave da Bing Search API (Azure) | Para resultados Bing |
| `GOOGLE_API_KEY` | Chave da Google Custom Search API | Opcional |
| `GOOGLE_CSE_ID` | ID do Custom Search Engine (Google) | Opcional |
| `DAILY_LIMIT` | Limite diário de buscas por usuário (padrão: 100) | Não |

> 💡 O DuckDuckGo **não precisa** de chave de API.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

O frontend iniciará em `http://localhost:5173` e encaminhará as chamadas `/api/*` automaticamente para o backend em `http://localhost:8000`.

---

## 📡 Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/search` | Realiza a meta-busca |
| `GET` | `/limit/{user_id}` | Consulta o limite diário |
| `GET` | `/profiles` | Lista os perfis disponíveis |

### Exemplo de requisição `/search`

```json
POST /search
{
  "query": "inteligência artificial",
  "profile": "scientific",
  "user_id": "alice",
  "results_per_engine": 10
}
```

### Perfis disponíveis

| ID | Nome | Comportamento |
|---|---|---|
| `general` | Geral | Sem ordenação por domínio |
| `scientific` | Científico 🔬 | Prioriza `.edu`, `.gov`, arXiv, PubMed, etc. |
| `journalistic` | Jornalístico 📰 | Prioriza BBC, Reuters, Folha, G1, etc. |
| `shopping` | Compras 🛒 | Prioriza Amazon, Mercado Livre, Buscapé, etc. |

---

## 🏗️ Estrutura do projeto

```
Metabuscador/
├── backend/
│   ├── main.py          # FastAPI app + endpoints
│   ├── profiles.py      # Perfis e listas de domínios
│   ├── filters.py       # Deduplicação e remoção de anúncios
│   ├── limiter.py       # Controle de limite diário
│   ├── search/
│   │   ├── bing.py      # Adaptador Bing Search API
│   │   ├── duckduckgo.py# Adaptador DuckDuckGo
│   │   └── google.py    # Adaptador Google Custom Search
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx      # Componente principal
    │   └── main.jsx
    ├── vite.config.js
    └── package.json
```
