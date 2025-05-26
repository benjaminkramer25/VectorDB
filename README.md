# VectorDB – a miniature vector database in Python 

> How to build a very small, but end-to-end, vector database: you can add text chunks, create an index, and query with k-nearest-neighbour search — all behind a clean FastAPI REST interface.
> 
---

## Quick start

```bash
# clone and step in
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload  # API at http://127.0.0.1:8000/docs
```

### With Docker

```bash
docker compose up --build  # same URL, no local Python needed
```

---

## Quick demo

```bash
# 1. create a library
curl -X POST http://127.0.0.1:8000/api/v1/libraries/ -d '{"name": "demo"}' -H "Content-Type: application/json"
# response → {"id": "abc..."}
LIB=the-id-from-above

# 2. add a chunk
curl -X POST http://127.0.0.1:8000/api/v1/chunks/ -d "{\"lib_id\": \"$LIB\", \"text\": \"hello vector world\"}" -H "Content-Type: application/json"

# 3. build the index (linear scan by default)
curl -X POST http://127.0.0.1:8000/api/v1/libraries/$LIB/index -d '{}' -H "Content-Type: application/json"

# 4. query with a dummy 26-dim embedding (character counts)
curl -X POST http://127.0.0.1:8000/api/v1/libraries/$LIB/query \
     -d '{"embedding": [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1], "k": 3}' \
     -H "Content-Type: application/json"
```

---

## Design

```
app/
 ├─ core/            # config + toy embedding function
 ├─ domain/          # entities, repository, service layer
 ├─ infrastructure/  # hand-rolled indexes (linear, KD-tree, LSH)
 ├─ api/             # FastAPI routers – pure I/O
 └─ main.py          # application factory
```

* **Domain-Driven** – HTTP knows nothing about storage; storage knows nothing about HTTP.
* **Concurrency** – one in-memory store guarded by an asyncio reader/writer lock (read-heavy, write-light).
* **Indexes**
  * *Linear Scan* – exact, O(n·d).
  * *KD-Tree* – good for small-dimensional exact search.
  * *Random-projection LSH* – approximate, sub-linear for high dimensions.

---

## Running tests

```bash
pytest -q    # <1 s on my laptop
```

---

## Environment variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `EMBEDDING_API_KEY` | external embedding provider (unused in stub) | demo key |

---
