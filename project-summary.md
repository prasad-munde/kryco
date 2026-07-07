# Project Summary — AI Influencer Marketing Platform

Paste this whole file into any LLM as context if you want help continuing the project.

## 1. What this project is

A backend (FastAPI) for a platform that connects **brands** with **content creators/influencers**. Brands can:
- Register/login
- List products
- Register creator profiles
- Search for creators using natural language (semantic search via vector DB)
- Get an AI-ranked shortlist of the best-fit creators for a campaign, with reasons

The "AI" part is two-fold:
1. **Semantic retrieval** — creator profiles are embedded and stored in a vector DB (Milvus), so a query like "fitness youtuber for a protein brand" can retrieve relevant creators even without exact keyword matches.
2. **LLM ranking** — the retrieved creators are then passed to Gemini (via LangChain) which ranks them and gives a reason for each ranking, returned as structured JSON.

## 2. Tech stack

| Layer | Tech |
|---|---|
| API framework | FastAPI |
| DB (relational) | PostgreSQL via SQLAlchemy ORM |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Vector DB | Milvus (via `langchain-milvus`) |
| Embeddings | HuggingFace `sentence-transformers/all-mpnet-base-v2` |
| LLM | Google Gemini `gemini-2.5-flash` via `langchain-google-genai` |
| Structured output | LangChain `.with_structured_output()` + Pydantic |
| Observability | LangSmith (`@traceable` decorators) |
| Config | `.env` via `python-dotenv` |

## 3. Folder / module layout (inferred)

```
app/
├── main.py                 # FastAPI app entrypoint, includes routers
├── database.py              # SQLAlchemy engine/session, get_db dependency
├── model.py                  # SQLAlchemy ORM models: User, Product, Creator
├── schemas.py                # Pydantic request/response schemas + enums
├── routers/
│   ├── auth.py                # /register, /login, /me
│   ├── products.py            # /create_product, /fetch_product
│   └── creators.py            # /register_creator, /fetch_creator, /search
├── utils/
│   ├── security.py            # JWT create/verify, get_current_user dependency
│   ├── embeddings.py          # creator_to_document() text formatter
│   └── vector_db.py           # Milvus vectorstore, insert_creator, search_creators
└── services/
    └── llm.py                  # Gemini prompt + rank_creators()
```

## 4. Data models (Postgres via SQLAlchemy)

- **User**: `id, name, email (unique), hashed_password`
- **Product**: `id, prod_name, category, description, brand` — *not linked to a User via foreign key currently*
- **Creator**: `id, name, niche, platform, bio` — *not linked to a User via foreign key currently*

Pydantic schemas mirror these for create/response, plus enums:
- `NicheEnum`: Gaming, Technology, Fitness, Fashion, Education, Travel, Food
- `PlatformEnum`: YouTube, Instagram, TikTok, Snapchat

## 5. API endpoints

### Auth (`/register`, `/login`, `/me`)
- `POST /register` — creates a User with bcrypt-hashed password. Errors if email exists.
- `POST /login` — verifies password, returns a JWT bearer token (`{sub: email}`).
- `GET /me` — protected; returns the current user's email (decoded from JWT).

### Products (`/create_product`, `/fetch_product`)
- Both protected by `get_current_user` (must be logged in).
- `create_product` just inserts a row — no ownership link back to the user who created it.
- `fetch_product` returns *all* products (no filtering/pagination).

### Creators (`/register_creator`, `/fetch_creator`, `/search`)
- `register_creator` (protected): inserts a Creator row into Postgres **and** calls `insert_creator()` to embed + store it in Milvus. This is the key place where relational and vector data are kept in sync.
- `fetch_creator` (protected): returns all creators from Postgres.
- `search` (**not** protected — no `get_current_user` dependency, unlike the other two): 
  1. Takes a free-text `query`.
  2. Calls `search_creators(query)` → Milvus similarity search, top 5 results.
  3. Extracts creator IDs from the vector search metadata.
  4. Re-fetches those creators from Postgres for full/fresh data.
  5. Passes the creator list + original query to `rank_creators()` (Gemini) to get a ranked list with reasons.
  6. Returns the LLM's structured ranking.

## 6. Core flow: how a creator becomes searchable

1. Brand calls `POST /register_creator` with name/niche/platform/bio.
2. Row saved to Postgres `creator` table.
3. `creator_to_document()` turns the creator into a plain-text block (name/niche/platform/bio).
4. That text is embedded with the HuggingFace model and stored in Milvus, with the creator's Postgres `id` and other fields as metadata, using the creator's own `id` as the vector's `id` too.

## 7. Core flow: how a search + recommendation works

1. Brand calls `GET /search?query=...`.
2. Milvus retriever does a top-5 similarity search over creator embeddings.
3. IDs from Milvus metadata are used to pull the authoritative rows from Postgres.
4. `rank_creators(query, creator_data)` sends the query + candidate creators to Gemini with a prompt asking it to rank best→worst based on niche/bio/platform/relevance, with a reason per creator.
5. Gemini's output is forced into the `CreatorRecommendationList` Pydantic schema (`recommendation: List[{creator_id, rank, reason}]`).
6. This structured list is returned directly to the client.

## 8. Environment variables required (`.env`)

```
SECRET_KEY=...
ALGORITHM=...                    # e.g. HS256
ACCESS_TOKEN_EXPIRE_MINUTES=...  # integer, e.g. 30
GEMINIAPIKEY=...                 # Google Gemini API key
```
Milvus URI is currently hardcoded to `http://localhost:19530` (not env-driven).
Postgres URL is currently hardcoded in `database.py` (see issues below).

## 9. Known issues / tech debt worth fixing early

These are things I noticed reading the code — worth raising with the team or fixing as quick wins:

1. **Hardcoded DB credentials**: `DATABASE_URL` in `database.py` has a literal username/password/host committed in code. Should move to `.env`.
2. **`/search` endpoint has no auth** while the other creator/product endpoints do — likely an oversight, not an intentional public endpoint.
3. **Leftover debug statements**: `print(results)`, `print(results[0])` in the search route, and `print(type(ACCESS_TOKEN_EXPIRE_MINUTES))` in `security.py` — remove before shipping.
4. **No foreign keys**: `Product` and `Creator` aren't linked to the `User` who created them, so there's no concept of "my products" or "my creators" yet — everyone sees everyone's data.
5. **Milvus URI hardcoded**, not read from environment — will break in any non-local deployment.
6. **Type mismatch risk**: `CreatorRecommendation.creator_id` is typed `str` in the Pydantic schema, but `Creator.id` is an `int` in the DB and in Milvus metadata (`int(doc.metadata["id"])`). Worth double-checking Gemini's structured output matches what you expect downstream.
7. **No pagination** on `fetch_product` / `fetch_creator` — fine for now, will need it as data grows.
8. **Minor typos in code/strings** (not bugs, but worth cleaning): `create_acess_token`, `registerd`, `Sucessfully`, `currrent_user` (param name in creators router) — cosmetic but shows up in API responses too (e.g. `"user registerd Sucessfully"`).
9. **No refresh tokens / token revocation** — JWT is stateless with just an expiry; fine for an MVP, but worth flagging for production.

## 10. Suggested first tasks for a new engineer

- Move all secrets/URLs into `.env` (Postgres URL, Milvus URI).
- Add `user_id` foreign keys to `Product` and `Creator` so brands only manage their own data.
- Add auth to the `/search` endpoint (or confirm intentionally public).
- Remove debug print statements.
- Write a `.env.example` and a short `README.md` for local setup (Postgres + Milvus running, env vars, `uvicorn main:app --reload`).
