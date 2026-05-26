import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("mem0-server")

OLLAMA_BASE_URL = os.environ.get("MEM0_OLLAMA_BASE_URL", "http://host-gateway:11434")
os.environ.setdefault("OLLAMA_HOST", OLLAMA_BASE_URL)

config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": os.environ.get("MEM0_LLM_MODEL", "qwen3:4b"),
            "ollama_base_url": OLLAMA_BASE_URL,
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": os.environ.get("MEM0_EMBEDDER_MODEL", "nomic-embed-text"),
            "ollama_base_url": OLLAMA_BASE_URL,
            "embedding_dims": 768,
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "url": os.environ.get("MEM0_QDRANT_URL", "http://qdrant:6333"),
            "collection_name": os.environ.get("MEM0_QDRANT_COLLECTION", "code-memory"),
            "embedding_model_dims": 768,
        }
    }
}

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
        log.error("Memory client failed after 30 attempts.")
    yield

app = FastAPI(lifespan=lifespan)

class AddRequest(BaseModel):
    messages: list
    user_id: str = "default"

class SearchRequest(BaseModel):
    query: str
    user_id: str = "default"
    limit: int = 5

def require_memory():
    if memory is None:
        raise HTTPException(status_code=503, detail="Memory client not ready.")

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
    return memory.search(req.query, filters={"user_id": req.user_id}, limit=req.limit)

@app.delete("/memories/{user_id}")
def delete_memories(user_id: str):
    require_memory()
    memory.delete_all(user_id=user_id)
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
