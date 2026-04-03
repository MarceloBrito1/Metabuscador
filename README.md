# Metabuscador

Meta-buscador que agrega resultados de múltiplas fontes (DuckDuckGo e Wikipedia) em uma interface única.

## Tecnologias

| Camada    | Tecnologia                                |
|-----------|-------------------------------------------|
| Backend   | Python 3.12, FastAPI, httpx               |
| Frontend  | Vue 3, Vite                               |
| Testes    | pytest + pytest-asyncio (backend), Vitest (frontend) |
| Deploy    | Docker + docker-compose                   |

## Estrutura do projeto

```
Metabuscador/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # Pydantic models
│   │   └── search/
│   │       ├── base.py      # Abstract searcher
│   │       ├── duckduckgo.py
│   │       ├── wikipedia.py
│   │       └── aggregator.py
│   ├── tests/
│   │   ├── test_main.py
│   │   └── test_search.py
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── style.css
│   │   └── components/
│   │       ├── SearchBar.vue
│   │       ├── SearchResults.vue
│   │       └── ResultCard.vue
│   ├── tests/unit/
│   │   ├── SearchBar.spec.js
│   │   ├── SearchResults.spec.js
│   │   └── ResultCard.spec.js
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── vite.config.js
│   └── package.json
└── docker-compose.yml
```

## Executar com Docker

```bash
docker-compose up --build
```

Acesse em: http://localhost

## Executar em modo desenvolvimento

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API disponível em: http://localhost:8000  
Documentação Swagger: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Interface disponível em: http://localhost:5173

## Rodar os testes

### Backend (17 testes)

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v
```

### Frontend (21 testes)

```bash
cd frontend
npm install
npm test
```

## API

| Endpoint        | Método | Descrição                          |
|-----------------|--------|------------------------------------|
| `/`             | GET    | Informações da API                 |
| `/health`       | GET    | Health check                       |
| `/search?q=...` | GET    | Pesquisa agregada (+ `max_results`)|

### Exemplo

```bash
curl "http://localhost:8000/search?q=python&max_results=5"
```
