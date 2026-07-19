# AI Influencer Marketing Platform

A backend platform (FastAPI) that connects brands with content creators/influencers using semantic search and LLM‑based ranking.

## Overview

This project provides a backend API for a platform where brands can:

- Register and log in  
- List products  
- Register creator profiles  
- Search for creators using natural language (semantic search via a vector database)  
- Receive an AI‑ranked shortlist of the best‑fit creators for a campaign, along with reasoning  

The “AI” component consists of:

1. **Semantic retrieval** – Creator profiles are embedded and stored in Milvus (via `langchain-milvus`). A free‑text query retrieves semantically similar creators even without exact keyword matches.  
2. **LLM ranking** – The retrieved candidates are re‑ranked by Google Gemini (via LangChain) which returns a JSON‑structured list of recommendations with reasons.

## Features

- **Authentication** – JWT‑based auth (python‑jose) with bcrypt password hashing.  
- **Product & Creator CRUD** – Basic create/list endpoints (currently not scoped to a user).  
- **Semantic creator search** – Powered by Milvus + HuggingFace `all-mpnet-base-v2` embeddings.  
- **LLM‑driven ranking** – Google Gemini (`gemini-2.5-flash`) returns ranked creators with explanations.  
- **Observability** – LangSmith tracing via `@traceable` decorators.  
- **Configuration** – Environment variables via `python-dotenv` (except Milvus/Postgres URLs, which are hardcoded – see Known Issues).  

## Architecture

```
app/
├── main.py                 # FastAPI app entrypoint, includes routers
├── database.py             # SQLAlchemy engine/session, get_db dependency
├── model.py                # SQLAlchemy ORM models: User, Product, Creator
├── schemas.py              # Pydantic request/response schemas + enums
├── routers/
│   ├── auth.py             # /register, /login, /me
│   ├── products.py         # /create_product, /fetch_product
│   └── creators.py         # /register_creator, /fetch_creator, /search
├── utils/
│   ├── security.py         # JWT create/verify, get_current_user dependency
│   ├── embeddings.py       # creator_to_document() text formatter
│   └── vector_db.py        # Milvus vectorstore, insert_creator, search_creators
└── services/
    └── llm.py              # Gemini prompt + rank_creators()
```

### Data Model (PostgreSQL)

| Table   | Fields                                                            |
|---------|-------------------------------------------------------------------|
| User    | `id`, `name`, `email` (unique), `hashed_password`                |
| Product | `id`, `prod_name`, `category`, `description`, `brand` (no FK to User) |
| Creator | `id`, `name`, `niche`, `platform`, `bio` (no FK to User)         |

**Enums (Pydantic)**  

- `NicheEnum`: Gaming, Technology, Fitness, Fashion, Education, Travel, Food  
- `PlatformEnum`: YouTube, Instagram, TikTok, Snapchat  

### API Endpoints

#### Auth (`/register`, `/login`, `/me`)
- `POST /register` – create a User (bcrypt‑hashed password). Returns error if email exists.  
- `POST /login` – verify password, return JWT (`{sub: email}`).  
- `GET /me` – protected; returns the current user's email (decoded from JWT).

#### Products (`/create_product`, `/fetch_product`)
- Both protected (`get_current_user`).  
- `POST /create_product` – insert a Product (no owner link).  
- `GET /fetch_product` – return **all** products (no pagination/filtering).

#### Creators (`/register_creator`, `/fetch_creator`, `/search`)
- `POST /register_creator` (protected):  
  1. Insert Creator row into Postgres.  
  2. Convert creator to text via `creator_to_document()`.  
  3. Embed with HuggingFace model and store in Milvus (metadata includes Postgres `id`).  
- `GET /fetch_creator` (protected): return all Creators from Postgres.  
- `GET /search?query=...` (**not protected** by default):  
  1. Milvus similarity search → top‑5 creator IDs.  
  2. Fetch full Creator rows from Postgres.  
  3. Pass query + candidate list to Gemini (`rank_creators`).  
  4. Gemini returns structured JSON `{recommendation: [{creator_id, rank, reason}]}`.  
  5. Return that list to the client.

## Setup

### Prerequisites

- Python 3.9+  
- PostgreSQL (running locally or accessible via URL)  
- Milvus (stand‑alone or Docker) running on `http://localhost:19530`  
- Google Gemini API key  

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd krecon

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt   # (ensure you have a requirements.txt; if not, install packages from project-summary)

# Copy the example environment file and fill in your secrets
cp .env.example .env   # create if missing
# Edit .env with your values:
#   SECRET_KEY=
#   ALGORITHM=HS256
#   ACCESS_TOKEN_EXPIRE_MINUTES=30
#   GEMINIAPIKEY=your_gemini_key
#   DATABASE_URL=postgresql://user:password@localhost/dbname   # optional, currently hardcoded
#   MILVUS_URI=http://localhost:19530                         # optional, currently hardcoded
```

### Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`.

## Environment Variables

| Variable                  | Description                                              | Example                           |
|---------------------------|----------------------------------------------------------|-----------------------------------|
| `SECRET_KEY`              | Secret for JWT signing                                   | `supersecretkey`                  |
| `ALGORITHM`               | JWT algorithm                                            | `HS256`                           |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry minutes                                 | `30`                              |
| `GEMINIAPIKEY`            | Google Gemini API key                                    | `AIza…`                           |
| `DATABASE_URL` (optional) | PostgreSQL connection string (if moved from hardcode)    | `postgresql://user:pw@localhost/db` |
| `MILVUS_URI` (optional)   | Milvus server URL (if moved from hardcode)               | `http://localhost:19530`          |

> **Note:** As of the current codebase, `DATABASE_URL` and `MILVUS_URI` are hardcoded in `database.py` and `vector_db.py`. Moving them to `.env` is a recommended improvement (see Known Issues).

## Known Issues & Technical Debt

- **Hardcoded DB credentials** – `DATABASE_URL` in `database.py` should be moved to `.env`.  
- **Hardcoded Milvus URI** – same as above.  
- **Missing authentication on `/search`** – endpoint is currently public; decide if it should be protected.  
- **No foreign keys** – `Product` and `Creator` are not linked to `User`; implies no ownership.  
- **Debug print statements** – e.g., `print(results)` in search route, `print(type(ACCESS_TOKEN_EXPIRE_MINUTES))` in `security.py`.  
- **Type mismatch** – `CreatorRecommendation.creator_id` is `str` in Pydantic schema while DB/Milvus ID is `int`. Ensure Gemini’s output matches expectations.  
- **No pagination** on `/fetch_product` and `/fetch_creator`.  
- **Minor typos** in strings and variable names (e.g., `create_acess_token`, `registerd`).  

## Suggested First Tasks for New Contributors

1. Move all secrets/URLs to `.env` (Postgres URL, Milvus URI).  
2. Add `user_id` foreign keys to `Product` and `Creator` tables to enable ownership.  
3. Add authentication to the `/search` endpoint (or document intentional public access).  
4. Remove debug `print` statements.  
5. Create a `.env.example` and a brief `README` (this file).  
6. Write unit/tests for core services (auth, vector store, LLM ranking).  
7. Add pagination to list endpoints.  

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---
*Generated with the help of Claude Code.*