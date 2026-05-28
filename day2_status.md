# Day 2: Schema Design and Training Preparation Status

Date: 2026-05-28

## Completed
- Ten-intent boundary definitions written in `training/day2_intents.md`.
- Pydantic schema written in `training/schema.py`.
- Reward functions written in `training/rewards.py`.
- Ground-truth generator written in `training/generate_day2_examples.py`.
- 150 ground-truth examples generated at `training/examples/ground_truth.jsonl`.
- Example split verified:
  - 30 examples per organ for code, reason, data, debug, synthesis.
  - 6 AST-context examples per organ.
  - 30 total AST-context examples.
- Validation harness written in `training/test_schema.py`.
- Autoresearch warm-start program written in `training/autoresearch/program.md`.
- Axolotl QLoRA template written in `training/axolotl/qwen3_lora_template.yml`.
- Seven organ `SOUL.md`, `tools.json`, and `rewards.json` files updated with concrete roles, audited MCP tools, and reward weights.
- MiniCPM5-1B added as coordinator candidate in `litellm-config.yml` as `coordinator-minicpm5`.
- MiniCPM5-1B was pulled successfully, then failed the 10-case coordinator routing/schema test. Do not promote it before Day 3.
- `qwen3:0.6b` also failed the strict coordinator routing/schema test.
- Deterministic rule-based coordinator baseline added in `training/rule_based_coordinator.py` and passes all 10 routing cases.
- Ten coordinator routing smoke tests added in `training/coordinator_routing_tests.jsonl`.
- Coordinator test harness added in `training/test_coordinator_model.py`.
- Day 3 readiness checklist written in `day3_readiness.md`.

## Verification
Command:

```bash
python3 training/test_schema.py
```

Result:

```json
{
  "examples": 150,
  "code_examples_executable_above_0_5": 30,
  "average_weighted_scores": {
    "code-organ": 0.9898,
    "data-organ": 0.9433,
    "debug-organ": 0.989,
    "reason-organ": 0.9098,
    "synthesis-organ": 0.9083
  }
}
```

## Not Run Automatically
- Full autoresearch overnight run: expected to exceed 10 minutes.
- Axolotl training: expected to exceed 10 minutes.
- MiniCPM5 prompt/runner investigation: it emits long `<think>` blocks and invalid routing schema; keep `qwen3:0.6b` active unless this is fixed later.
- LLM coordinator promotion is deferred until grammar-constrained output or coordinator fine-tuning exists.
- Any git commits inside organ repos: left uncommitted unless explicitly requested.
