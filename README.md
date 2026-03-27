# 🔍 Metabuscador

Um meta-buscador que agrega resultados de múltiplos motores de busca, com autenticação JWT, limite diário de buscas, paginação e interface moderna.

## ✨ Funcionalidades

- 🔎 **Meta-busca** — Agrega resultados do DuckDuckGo (extensível a outros)
- 🔐 **Autenticação JWT** — Registro, login e proteção de rotas
- 💾 **Persistência** — SQLite via SQLAlchemy (usuários, histórico, limite diário)
- 📄 **Paginação** — Navegação por múltiplas páginas de resultados
- ⚡ **Limite diário** — Controle de buscas por usuário/dia (configurável)
- 📝 **Logging** — Logs estruturados em todo o backend
- 🐳 **Docker** — Deploy com um único comando

## 🏗️ Tecnologias

| Camada | Stack |
|---|---|
| Backend | Python 3.11 · FastAPI · SQLAlchemy · SQLite · JWT |
| Frontend | Vue 3 · Vite · Pinia · Vue Router |
| Testes | pytest (backend) · Vitest (frontend) |
| Deploy | Docker · Docker Compose · Nginx |

## 🚀 Como rodar

### Com Docker (recomendado)

```bash
# 1. Copiar variáveis de ambiente
cp backend/.env.example backend/.env

# 2. Subir os serviços
docker-compose up --build
```

- Frontend: http://localhost:80
- Backend API: http://localhost:8000
- Docs da API: http://localhost:8000/docs

### Desenvolvimento local

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
# API em http://localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# UI em http://localhost:5173
```

## 🧪 Testes

**Backend (pytest):**
```bash
cd backend
python -m pytest tests/ -v
```

**Frontend (Vitest):**
```bash
cd frontend
npm test
```

## ⚙️ Configuração

Edite `backend/.env`:

| Variável | Padrão | Descrição |
|---|---|---|
| `SECRET_KEY` | `change-me-in-production` | Chave para assinar tokens JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Expiração do token em minutos |
| `DATABASE_URL` | `sqlite:///./metabuscador.db` | URL do banco de dados |
| `DAILY_SEARCH_LIMIT` | `50` | Máximo de buscas por usuário/dia |

## 📁 Estrutura do projeto

```
.
├── backend/
│   ├── app/
│   │   ├── main.py          # Entrada da API
│   │   ├── config.py        # Configurações
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── models.py        # Modelos ORM
│   │   ├── schemas.py       # Schemas Pydantic
│   │   ├── auth.py          # Lógica JWT
│   │   ├── logger.py        # Logging
│   │   ├── search/          # Motores de busca
│   │   └── routers/         # Endpoints
│   ├── tests/               # Testes pytest
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/           # Páginas Vue
│   │   ├── components/      # Componentes reutilizáveis
│   │   ├── stores/          # Pinia stores
│   │   └── api/             # Axios client
│   ├── tests/               # Testes Vitest
│   └── Dockerfile
└── docker-compose.yml
```

## 🔌 API Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/auth/register` | Criar conta |
| `POST` | `/api/auth/token` | Login (retorna JWT) |
| `GET` | `/api/auth/me` | Dados do usuário logado |
| `GET` | `/api/search/?q=...&page=1&per_page=10` | Buscar (requer auth) |
| `GET` | `/api/health` | Health check |
