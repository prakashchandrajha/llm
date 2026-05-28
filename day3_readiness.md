# Day 3 Readiness

Date: 2026-05-28

## Ready
- Day 0 system prerequisites are verified: cgroup v2, sm_120 CUDA target, API key inventory, and `.env` ignored for future commits.
- Day 1 services are configured and LiteLLM is healthy after reload.
- Active `fallback-expert` chain is intentionally conservative:
  1. Cerebras `gpt-oss-120b`
  2. Groq `llama-3.3-70b-versatile`
  3. Mistral `mistral-large-latest`
  4. OpenRouter `openrouter/free`
  5. NVIDIA `meta/llama-3.3-70b-instruct`
  6. Local Ollama `qwen3.6:35b-a3b-q4_K_M`
- Direct-only models are configured for manual use: OpenRouter auto, OpenRouter Qwen3 Coder free, OpenRouter Nemotron free, Cohere, NVIDIA Nemotron reasoning, Aion Labs, Gemini, DeepSeek, and xAI.
- Day 2 schema, reward functions, 150 examples, organ SOUL files, and validation harness are present.
- MiniCPM5-1B is installed and configured as `coordinator-minicpm5`, but it failed routing tests.
- `qwen3:0.6b` also failed the strict 10-case coordinator schema test.
- Day 3 should use the deterministic rule-based coordinator baseline in `training/rule_based_coordinator.py` until a trained/grammar-constrained coordinator is available.

## Caveats
- MiniCPM5-1B should not be promoted yet. It emits long `<think>` blocks and invalid coordinator schema through Ollama/LiteLLM.
- The local tiny LLM coordinators are not schema-reliable yet. Do not let them control Day 3 ingestion or data routing without a gate/grammar layer.
- Gemini generation currently returns quota/free-tier 429.
- DeepSeek chat currently returns insufficient balance / 402.
- xAI currently reports no credits/licence.
- Aion Labs responds but produced poor final content in a strict one-word smoke test, so it remains direct-only.

## Quick Checks Already Passing
```bash
python3 training/test_schema.py
python3 -m py_compile training/test_coordinator_model.py
docker compose --profile inference config
```

## Commands To Run Before Day 3
MiniCPM5 has already been pulled and tested. It failed, so do not block Day 3 on it.

```bash
python3 training/test_coordinator_model.py --model rule-based
```

Current result: passes all 10 routing cases.

LLM coordinator candidates can be retested later:

```bash
python3 training/test_coordinator_model.py --model coordinator
python3 training/test_coordinator_model.py --model coordinator-minicpm5 --max-tokens 768
```

Current result: both fail strict schema/routing tests.

Optional broader smoke test:

```bash
timeout 480 bash test_all_apis.sh
RUN_DIRECT_MODEL_TESTS=1 timeout 480 bash test_all_apis.sh
```
