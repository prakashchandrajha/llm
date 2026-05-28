# Day 0 and Day 1: System State and Verification Record

**Purpose:** This document is the source of truth for any AI coding assistant (Gemini, Claude, Copilot, etc.) joining the project. It details exactly what was achieved during Phase 0 (Day 0 & Day 1), what services are currently running, and any known environment caveats.

## 1. Cloud Cascade & API Setup (Day 0)
- **API Keys:** Successfully provisioned and stored in `.env` for Cerebras, Groq, Gemini, Mistral, OpenRouter, and NVIDIA.
- **LiteLLM Config:** Located at `litellm-config.yml`. Uses a robust fallback chain (`fallback-expert`) that routes requests to:
  1. Cerebras (`gpt-oss-120b`)
  2. Groq (`llama-3.3-70b-versatile`)
  3. Mistral (`mistral-large-latest`)
  4. OpenRouter free router (`openrouter/free`)
  5. NVIDIA (`meta/llama-3.3-70b-instruct` via NVIDIA NIM)
  6. Local fallback (`ollama/qwen3.6:35b-a3b-q4_K_M`)
- **Direct-only providers:** OpenRouter auto, OpenRouter Qwen3 Coder free, OpenRouter Nemotron free, Aion Labs, Cohere Command A, Cohere Command A Reasoning, NVIDIA Nemotron reasoning, Gemini, DeepSeek, and xAI are configured as named models.
- **Provider Caveats:** Gemini currently returns free-tier quota `0` / HTTP 429 for generation. DeepSeek can list models but chat returns insufficient balance / HTTP 402. xAI currently reports no credits/licence. Aion Labs responds, but the smoke test produced poor final content, so it is direct-only. These are not in the active fallback path.
- **System Constraints Checked:** `cgroup v2` is active, `TORCH_CUDA_ARCH_LIST="12.0"` set in `.bashrc`. NVMe read speed confirmed at ~5050 MB/s.

## 2. Local Models (Ollama)
The following models are available via `http://localhost:11434`:
- `qwen3:0.6b` (Coordinator tier)
- `qwen3:1.7b` (Synthesis tier)
- `qwen3:4b` (Graphiti/Memory tier)
- `qwen3:8b` (Master base)
- `qwen2.5-coder:7b` (Coder tier)
- `nomic-embed-text` (Embedding tier)
- `qwen3.6:35b-a3b-q4_K_M` (Heavy local fallback)

## 3. Docker Infrastructure
All services are running under the `inference` profile (`docker compose --profile inference up -d`).
- **Langfuse** (Host: `http://localhost:3000`): User `admin@example.com` created, Public/Secret keys generated and added to `.env`.
- **LiteLLM Proxy** (Port 4000): Gateway for all LLM calls. Connected to Langfuse for tracing.
- **Memgraph** (Ports 7687/7444): Core AST/Temporal graph database. Loaded with ~3110 seed nodes.
- **Graphiti** (Port 8000): Temporal Knowledge Graph service using Zep Graphiti. Compatibility patched for Memgraph (`zep_graphiti_patch.py`, `neo4j_driver_patch.py`).
- **Qdrant** (Port 6333): Vector store for Mem0.
- **Mem0 Server** (Port 8765): Custom FastAPI wrapper (`mem0-server.py`) around Mem0 AI, utilizing Qdrant and Ollama.
- **Redis** (Port 6380): Caching layer for LiteLLM and Graphiti.
- **Activepieces** (Port 8080): Automation workflow engine (Currently up, but requires manual configuration for workflows).

## 4. MCP Servers & Audit
Configured in `mcp-servers.json`:
- **Context7**: `resolve-library-id`, `query-docs`
- **Codebase-Memory**: `index_repository`, `search_graph`, `query_graph`, `trace_path`, `get_code_snippet`, `get_graph_schema`, `get_architecture`, `search_code`, `list_projects`, `delete_project`, `index_status`, `detect_changes`, `manage_adr`, `ingest_traces`
- **Serena**: `create_text_file`, `replace_content`, `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol`, `read_file`, `list_dir`, `find_file`, `search_for_pattern`, `get_symbols_overview`, `find_symbol`, `find_referencing_symbols`, `find_implementations`, `find_declaration`, `get_diagnostics_for_file`, `rename_symbol`, `safe_delete_symbol`, `write_memory`, `read_memory`, `list_memories`, `delete_memory`, `rename_memory`, `edit_memory`, `execute_shell_command`, `activate_project`, `get_current_config`, `onboarding`, `initial_instructions`
- **Coderunner**: `python-code-runner`, `javascript-code-runner`

**Coderunner Verification Completed:** The sandbox was strictly tested and verified via `@pydantic/mcp-run-python`:
- Normal code execution: **Passed**
- Infinite loops: **Passed** (Timed out successfully)
- Memory bombs: **Passed** (Caught `OverflowError`)
- Network calls: **Passed** (Blocked, `AttributeError` on socket connect)
- Malicious commands (`rm -rf`): Runs safely inside the isolated environment.

## 5. Build & Environment Caveats (CRITICAL for AI context)
- **Host GPU:** RTX 5050 Laptop (sm_120, Blackwell architecture). **AMX is NOT present**.
- **Source Builds:** `flash-attn` and `KTransformers` were successfully compiled from source for CUDA 13.2 (`sm_120`).
- **Python Environment:** The system runs Python 3.12 without a virtual environment. Packages were forced-installed via `pip install --break-system-packages`. 
- **Resolved Packages & Alternatives:**
  - `ghgrab` v2.0.1: ✅ Successfully compiled and installed at `/home/vvd/.cargo/bin/ghgrab`.
  - `repomix` v1.14.1: ✅ Works via `npx -y repomix`. No global install needed.
  - `gapman`: Replaced by a manual directory structure (`code-organ`, `reason-organ`, `data-organ`, `debug-organ`, `synthesis-organ`, `gate-organ`, `coordinator-organ`). Each organ has its own Git repo, `SOUL.md`, `tools.json`, and `rewards.json`.
- **Missing Packages (DO NOT ATTEMPT TO REINSTALL):**
  - `swe-smith`: Fails to install due to Python 3.12 incompatibility. Skip this — use HuggingFace datasets and ART AutoRL for training data instead.

## 6. Verification Refresh — 2026-05-28
- `cgroup v2`: Active (`cpuset cpu io memory hugetlb pids rdma misc dmem`).
- `.bashrc`: `TORCH_CUDA_ARCH_LIST="12.0"` is set.
- Docker runtime: Langfuse stack and project services are up. `memgraph`, `graphiti`, `mem0-server`, `redis`, and `litellm-proxy` are healthy.
- Ollama inventory: `qwen3:0.6b`, `qwen3:1.7b`, `qwen3:4b`, `qwen3:8b`, `qwen2.5-coder:7b`, `nomic-embed-text`, and `qwen3.6:35b-a3b-q4_K_M` are present.
- MiniCPM5-1B: Installed as Ollama model `openbmb/minicpm5` and configured as `coordinator-minicpm5`, but it failed the 10-case coordinator routing/schema test. Keep `qwen3:0.6b` as active coordinator for Day 3.
- GPU check: RTX 5050 Laptop GPU, driver `595.71.05`; PyTorch reports CUDA capability `12.0`.
- Python imports: `ktransformers`, `flash_attn`, and `bitsandbytes` import successfully.
- Memgraph seed graph: `MATCH (n) RETURN count(n)` returned `3110`.
- MCP audit: Context7, Serena, Codebase-Memory, and Coderunner all listed expected tools.
- LiteLLM API smoke test: `fallback-expert`, Groq, Mistral, OpenRouter auto, OpenRouter free, NVIDIA, NVIDIA reasoning, Cohere Command A, coordinator, and master returned valid responses. Aion Labs responded but produced poor final content; Gemini direct test returned HTTP 429 quota errors; DeepSeek chat returned HTTP 402 insufficient balance; xAI model list returned no credits/licence.
- Test script update: `test_all_apis.sh` now uses `max_tokens=200` so reasoning models can finish a final answer.

## Conclusion
Day 0 and Day 1 are officially **COMPLETE**, with Gemini parked as a direct-only provider until quota is restored. The infrastructure is solid, the models are downloaded, memory/graph endpoints are online, code execution is sandboxed, LiteLLM includes Cerebras as Priority 1, and the active free cloud cascade is routed correctly.

**Next Step:** Proceed to Day 2 — Organ Identity (SOUL.md customization and token economy configurations).
