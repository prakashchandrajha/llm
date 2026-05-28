# Project Trajectory & Master LLM Plan

## Retrospective: What We Have Already Built (Day 0 - Day 3)

### Day 0 & Day 1: Infrastructure & Cloud Cascade
- **API Cascade Configured**: `litellm-config.yml` running with Cerebras (Priority 1), Groq (Priority 2), Mistral (Priority 3), OpenRouter (Priority 4), and NVIDIA (Priority 5).
- **Local Fallback**: Qwen3.6-35B-A3B running on AVX2 CPU for absolute local safety.
- **Docker Stack**: Langfuse (Observability), Memgraph (AST Graph), Graphiti (Temporal Memory), Redis, Mem0, and LiteLLM Proxy all running successfully on `cgroup v2` limits.
- **MCP Servers**: Audited and active (Codebase-Memory, Context7, Serena, Coderunner). Code sandbox execution strictly tested against infinite loops, memory bombs, and network access.

### Day 2: Schema Design & Organ Identity
- **Organ Architectures**: Initialized 7 gapman-style repos (`code-organ`, `reason-organ`, `data-organ`, `debug-organ`, `synthesis-organ`, `gate-organ`, `coordinator-organ`).
- **SOULs & Constraints**: Wrote `SOUL.md` definitions for all organs, including DoCoreAI strict profiles (e.g., Code-Organ locked to Temperature 0.1).
- **Ground Truth Generation**: 150 ground-truth examples manually crafted and validated through Pydantic schemas.
- **Routing Baseline**: Local LLMs (MiniCPM5/Qwen3-0.6b) failed schema strictness, so a deterministic `rule_based_coordinator.py` was built to ensure 100% routing stability.

### Day 3: Bloodstream Construction & Dataset Assembly
- **Code Ingestion**: Switched from REST APIs to `git clone --depth 1` to bypass rate limits. Compressed langchain, llama_index, ktransformers, and autoresearch into repomix blocks.
- **Documentation Ingestion**: Firecrawl scraped 5 major `llms.txt` docs directly into Memgraph.
- **Graph Clustering**: Leiden community detection ran over Memgraph, identifying 42 distinct architectural clusters.
- **Data Synthesis**: ART AutoRL generated 25,000 examples (5k per organ).
- **Filtering**: MinHash LSH deduplication removed 4,320 duplicates. Exactly 20% of examples received live AST context injections. Distilabel removed low-confidence outputs.
- **Upload**: Datasets pushed to HuggingFace private repos, commit hashes locked.

---

## Day 4: Enhanced Master Training (The "Even Better" Plan)

*Note: This plan has been significantly upgraded from the original design after deep system analysis.*

**Goal: Complete master SFT and SIX specialist adapters (including the Coordinator). Integrate Temporal Memory training and force Test-Driven generation.**

### Morning Block: System & Training Prep
- **Switch to Training Profile:** `docker compose --profile training up -d` (Releases VRAM from KTransformers).
- **Apply Hyperparameters:** Load Optuna LoRA ranks and `autoresearch` winning config into Axolotl YAML (ZenFlow enabled, MemAscend enabled).
- **Enforce Kernel Limits:** Run training inside a 14GB `systemd-run` cgroup to protect Memgraph/Graphiti from OOM kills.
- **Enhanced Data Injection (New):** Inject Graphiti Temporal Memory context into 10% of Synthesis/Reasoning examples to teach historical awareness. Ensure Code examples contain forced `pytest` output blocks.

### Midday Block: Train Master 7B Base
- **Stage 1 (Format SFT):** Two epochs on simple schema examples using strictly `completions_only: true`. Validates schema structure without reasoning overhead.
- **Stage 2 (Complex AST/Temporal SFT):** One epoch on complex multi-step reasoning examples containing AST and Graphiti context graphs.
- **Merge & Export:** Unload LoRA adapter into base weights and export as `master-7b-merged` GGUF.

### Afternoon Block: Train SIX Adapters (The Organ Specialization)
- **Train the Missing Coordinator-Organ (New):** Train an adapter exclusively on valid JSON routing examples to fix the MiniCPM/Qwen `<think>` spam issue. We will stop relying on regex rules.
- **Train Task Organs:** Train Code, Debug, Reason, Data, and Synthesis adapters sequentially on the merged Master base.
- **Post-Training Validation:** Every adapter must pass the 30 hand-crafted baseline tests in Langfuse (`adapter-{organ}-posttraining`) with >70% schema intent accuracy and >60% executable-pass rate.

### Evening Block: Live Subgraph Sync Implementation (New)
- Wire Serena MCP (`replace_content`, `create_text_file`) to Codebase-Memory MCP (`detect_changes`).
- Ensure the Memgraph AST remains accurate in real-time during agent interactions, not just after `git commit`.
