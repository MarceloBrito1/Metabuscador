# Metabuscador Limpo 🔍

## 📖 Descrição

O **Metabuscador Limpo** é um projeto experimental que reúne resultados de múltiplos motores de busca (Google, Bing e DuckDuckGo), aplicando filtros inteligentes para remover duplicidades, ocultar anúncios e organizar os links conforme perfis de interesse (científico, jornalístico, compras).

Além disso, o sistema controla o limite diário de **100 buscas por usuário**, garantindo transparência e evitando custos inesperados.

---

## 🚀 Funcionalidades

- Integração com Google, Bing e DuckDuckGo.
- Remoção de duplicidades e anúncios patrocinados.
- Perfis de busca configuráveis:
  - 🔬 **Científico** → prioriza `.edu` e `.gov`.
  - 📰 **Jornalístico** → prioriza veículos de imprensa confiáveis.
  - 🛒 **Compras** → prioriza comparadores e reviews.
- Controle de limite diário (100 buscas por usuário).
- Interface web simples e responsiva em React.

---

## 🛠️ Tecnologias

- **Backend:** Python + FastAPI
- **Frontend:** React + TailwindCSS
- **Banco de dados/cache:** memória em Python (pode evoluir para Redis/PostgreSQL)
- **APIs externas:** Bing Search API, DuckDuckGo Instant Answer API, Google Custom Search (opcional)

---

## 📦 Instalação

### Backend

1. Vá até a pasta `backend`.
2. Instale dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Rode o servidor:
   ```bash
   uvicorn app:app --reload
   ```

### Frontend

1. Vá até a pasta `frontend`.
2. Instale dependências:
   ```bash
   npm install
   ```
3. Rode o frontend:
   ```bash
   npm start
   ```

---

## 📊 Estrutura do projeto

```
metabuscador-limpo/
│
├── backend/
│   ├── app.py              # API principal FastAPI
│   ├── filters.py          # Funções de limpeza
│   ├── profiles.py         # Regras de perfis
│   ├── usage.py            # Controle de limite diário
│   ├── engines.py          # Integração com Google, Bing, DuckDuckGo
│   └── requirements.txt    # Dependências
│
├── frontend/
│   ├── src/
│   │   ├── App.js          # Componente principal React
│   │   ├── SearchBar.js    # Campo de busca
│   │   ├── Results.js      # Exibição dos resultados
│   │   └── ProfileSelector.js # Seleção de perfil
│   ├── package.json        # Dependências
│   └── README.md           # Documentação do frontend
│
└── README.md               # Documentação geral
```

---

## 📈 Roadmap futuro

- Implementar login via OAuth (Google).
- Adicionar cache com Redis para acelerar buscas repetidas.
- Evoluir para metabuscador completo com múltiplas fontes e ranking inteligente.
- Criar versão mobile (Android/iOS).

---

## 📜 Licença

Este projeto é experimental e pode ser usado como base para estudos e desenvolvimento de soluções de busca personalizadas.