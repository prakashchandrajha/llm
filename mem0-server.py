import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mem0 import Memory

app = FastAPI()

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

memory = Memory.from_config(config)

class AddRequest(BaseModel):
    messages: list
    user_id: str = "default"

class SearchRequest(BaseModel):
    query: str
    user_id: str = "default"
    limit: int = 5

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/memories")
def add_memory(req: AddRequest):
    result = memory.add(req.messages, user_id=req.user_id)
    return result

@app.get("/memories/{user_id}")
def get_memories(user_id: str):
    return memory.get_all(user_id=user_id)

@app.post("/search")
def search(req: SearchRequest):
    return memory.search(req.query, user_id=req.user_id, limit=req.limit)

@app.delete("/memories/{user_id}")
def delete_memories(user_id: str):
    memory.delete_all(user_id=user_id)
    return {"status": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)