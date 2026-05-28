#!/usr/bin/env python3
"""
Optuna LoRA Rank Ablation — Phase 0 Day 1
Ranks: 4, 8, 16, 32 × 5 organs × 200 examples = 20 trials
Primary metric: code-executable-pass rate via coderunner MCP
"""
import optuna, json, subprocess, tempfile, os, sys
from pathlib import Path

ORGANS = ["router", "planner", "coder", "reviewer", "synthesizer"]
RANKS = [4, 8, 16, 32]
EXAMPLES_PER_TRIAL = 200
LOG = Path(__file__).parent / "phase0-checks" / "optuna_ablation.log"

DENO = "/home/vvd/.deno/bin/deno"

def run_code_via_mcp(code: str, timeout: int = 10) -> bool:
    """Run Python code via @pydantic/mcp-run-python sandbox. Returns True if success."""
    code_json = json.dumps(code)
    msg = (
        '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05",'
        '"capabilities":{},"clientInfo":{"name":"ablation","version":"1.0"}}}\n'
        f'{{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{{"name":"run_python_code","arguments":{{"python_code":{code_json}}}}}}}\n'
    )
    try:
        result = subprocess.run(
            [DENO, "run", "--node-modules-dir=auto", "-A", "jsr:@pydantic/mcp-run-python", "stdio"],
            input=msg, capture_output=True, text=True, timeout=timeout
        )
        for line in result.stdout.splitlines():
            if '"id":2' in line:
                d = json.loads(line)
                text = d.get("result", {}).get("content", [{}])[0].get("text", "")
                return "<status>success</status>" in text
    except Exception:
        pass
    return False


def simulate_organ_pass_rate(organ: str, rank: int, n: int = EXAMPLES_PER_TRIAL) -> float:
    """
    Placeholder: replace with real LoRA fine-tuning + eval loop.
    Currently returns a synthetic score based on rank characteristics.
    TODO: load organ-specific dataset from /home/vvd/prakash/xorz/llm/data/{organ}/train.jsonl
    """
    # Synthetic: higher rank = better up to 16, then diminishing returns
    base = {"router": 0.55, "planner": 0.60, "coder": 0.65, "reviewer": 0.58, "synthesizer": 0.62}[organ]
    rank_bonus = {4: 0.0, 8: 0.05, 16: 0.08, 32: 0.07}[rank]
    import random; random.seed(rank + hash(organ) % 100)
    noise = random.gauss(0, 0.02)
    score = min(1.0, base + rank_bonus + noise)

    # Verify coderunner sandbox is alive
    sandbox_ok = run_code_via_mcp("print('ping')")
    if not sandbox_ok:
        print(f"  WARNING: coderunner sandbox not responding", flush=True)

    return score


def objective(trial: optuna.Trial) -> float:
    organ = trial.suggest_categorical("organ", ORGANS)
    rank = trial.suggest_categorical("rank", RANKS)
    score = simulate_organ_pass_rate(organ, rank)
    with open(LOG, "a") as f:
        f.write(json.dumps({"trial": trial.number, "organ": organ, "rank": rank, "score": score}) + "\n")
    print(f"  Trial {trial.number}: organ={organ} rank={rank} score={score:.4f}", flush=True)
    return score


if __name__ == "__main__":
    print(f"Starting Optuna rank ablation: {len(ORGANS)} organs × {len(RANKS)} ranks = 20 trials")
    print(f"Log: {LOG}")
    LOG.parent.mkdir(exist_ok=True)

    study = optuna.create_study(
        direction="maximize",
        study_name="rank_ablation",
        sampler=optuna.samplers.BruteForceSampler(),  # exhaustive for small search space
    )
    study.optimize(objective, n_trials=len(ORGANS) * len(RANKS))

    print("\n=== RESULTS ===")
    best_per_organ = {}
    for trial in study.trials:
        organ = trial.params["organ"]
        if organ not in best_per_organ or trial.value > best_per_organ[organ][1]:
            best_per_organ[organ] = (trial.params["rank"], trial.value)

    for organ, (rank, score) in sorted(best_per_organ.items()):
        print(f"  {organ:15s}: best_rank={rank:2d}  pass_rate={score:.4f}")

    print("\nNOTE: Replace simulate_organ_pass_rate() with real LoRA training once")
    print("organ datasets exist at /home/vvd/prakash/xorz/llm/data/{organ}/train.jsonl")
