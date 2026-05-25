import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mem0-server")

# ── Config built from environment ────────────────────────────────────────────
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": os.environ.get("MEM0_LLM_MODEL", "qwen3:4b"),
            "ollama_base_url": os.environ.get("MEM0_OLLAMA_BASE_URL", "http://host-gateway:11434"),
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": os.environ.get("MEM0_EMBEDDER_MODEL", "nomic-embed-text"),
            "ollama_base_url": os.environ.get("MEM0_OLLAMA_BASE_URL", "http://host-gateway:11434"),
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": os.environ.get("MEM0_QDRANT_URL", "http://qdrant:6333"),
            "collection_name": os.environ.get("MEM0_QDRANT_COLLECTION", "code-memory"),
        }
    }
}

# ── Memory client — initialised at startup, not at import time ───────────────
# Deferring prevents crash-loop on container start when Qdrant or Ollama
# is not yet ready. FastAPI reports /health immediately; the startup event
# will keep retrying until both backends are reachable.
memory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global memory
    from mem0 import Memory
    import time
    for attempt in range(30):
        try:
            log.info(f"Initialising Memory client (attempt {attempt + 1}/30) ...")
            memory = Memory.from_config(config)
            log.info("Memory client ready.")
            break
        except Exception as e:
            log.warning(f"Memory init failed: {e} — retrying in 10 s")
            time.sleep(10)
    else:
        log.error("Memory client failed to initialise after 30 attempts. Server running but all memory endpoints will return 503.")
    yield
    # Shutdown — nothing to clean up for mem0

app = FastAPI(lifespan=lifespan)

# ── Request models ────────────────────────────────────────────────────────────
class AddRequest(BaseModel):
    messages: list
    user_id: str = "default"

class SearchRequest(BaseModel):
    query: str
    user_id: str = "default"
    limit: int = 5

# ── Helper ────────────────────────────────────────────────────────────────────
def require_memory():
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not ready yet. Check Qdrant and Ollama.")

# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "memory_ready": memory is not None}

@app.post("/memories")
def add_memory(req: AddRequest):
    require_memory()
    return memory.add(req.messages, user_id=req.user_id)

@app.get("/memories/{user_id}")
def get_memories(user_id: str):
    require_memory()
    return memory.get_all(user_id=user_id)

@app.post("/search")
def search(req: SearchRequest):
    require_memory()
    return memory.search(req.query, user_id=req.user_id, limit=req.limit)

@app.delete("/memories/{user_id}")
def delete_memories(user_id: str):
    require_memory()
    memory.delete_all(user_id=user_id)
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)