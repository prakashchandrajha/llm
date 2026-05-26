Cross-Examination First
Speculative decoding on 8GB VRAM confirmed fails — splitting VRAM between draft and target models is structurally slower than one model using all VRAM. The MoE 35B-A3B at 8.6 tok/s is the actual answer for local inference on this hardware class. arXiv
DFlash has confirmed checkpoints for Qwen3.5-35B-A3B specifically, delivering 2.5x improvement over EAGLE-3 by replacing the sequential draft head with a block diffusion model that generates all K tokens simultaneously. It integrates with SGLang via the same flags as EAGLE-3. arxiv
So DFlash on the 35B-A3B local model gives approximately 15 to 20 tok/s locally. Free cloud gives 500 to 2000 tok/s. Combined they make the bottleneck irrelevant.
The key insight: LLM inference is memory-bandwidth-bound, not compute-bound. GPUs sit idle waiting for weights to load. Speculative decoding batches that idle time into useful token verification instead of wasting it. Speedup ratios are higher on cards with less VRAM because the draft model's predictions allow the target model to verify multiple tokens during cycles that would otherwise be bottlenecked by memory swapping. GitHub
Your RTX 5050 with 7.7GB VRAM benefits more from speculative decoding than a 24GB card precisely because of the memory constraint. This is the engineering beating the physics insight.


hint :The KV cache adjustment to 2.5GB is already applied in docker-compose.yml at line 199. The files are ready - mem0-server.py and the updated docker-compose.yml with:

Active mem0-server using python:3.11-slim + pip install mem0ai
LiteLLM healthcheck using wget (not curl)
KTransformers KV cache set to 2.5GB for 7.5GB usable VRAM


DAY 0: Environment Verification (Do Tonight)
Goal: Confirm hardware, fix the sm_120 build problem, nothing more.
Action 1: Check microcode and attempt AMX unlock.
Run sudo apt install intel-microcode && sudo update-initramfs -u then reboot. After reboot run grep amx /proc/cpuinfo. If AMX appears, KTransformers runs faster. If not, the plan works on AVX2 plus DFlash plus free cloud.
Action 2: Check actual NVMe speed.
Run fio --name=test --rw=read --bs=1M --size=4G --numjobs=1 --ioengine=libaio --direct=1. Record the number. If below 2500 MB/s, the local 35B fallback will be slow. The free cloud cascade becomes even more important.
Action 3: Confirm GPU.
Run nvidia-smi. Confirm 7707 MiB. Run python3 -c "import torch; print(torch.cuda.get_device_properties(0))". Confirm compute capability 12.0.
Action 4: Thermal check.
Run GPU stress test for 10 minutes. If throttle happens within 5 minutes, clean the cooling system before any training.
Action 5: Build sm_120 packages from source. Set export TORCH_CUDA_ARCH_LIST="12.0" and build bitsandbytes, flash-attn, and KTransformers from source. This takes 2 to 3 hours. Start it and leave.
Action 6: Get free API keys. These are all zero cost, no credit card.
Cerebras: sign up at cerebras.ai/developers.
Groq: sign up at console.groq.com.
Gemini: key from aistudio.google.com.
Mistral: sign up at console.mistral.ai with phone number, no card.
Store all four keys in a .env file. Never commit this file to git.
End of Day 0: sm_120 builds complete, four free API keys in .env file.

DAY 1: Full Infrastructure Stack
Goal: Every Docker service running, every MCP server tested, Langfuse showing traces.

Step 1.1 — Docker Compose File (Morning, 1 hour)
Write the complete Docker Compose file with cgroup v2 hard limits on every service. Two profiles: inference and training. Training profile stops KTransformers to free RAM.
Services and RAM limits:
Langfuse-web 0.5GB. Langfuse-worker 0.5GB. Postgres 0.5GB. ClickHouse 0.5GB. Redis 0.3GB. MinIO 0.2GB. Memgraph 2.5GB. Qdrant 1.0GB. Ollama 1.0GB. Graphiti 0.5GB. Codebase-Memory-MCP 0.5GB. Serena-MCP 0.3GB. Context7-MCP 0.1GB. Coderunner-MCP 0.2GB. SGLang-server 1.0GB. LiteLLM-proxy 0.3GB. Activepieces 0.4GB. Jan 0.5GB on port 1337.
Every service has mem_limit equal to memswap_limit. This makes memory overruns into visible OOM kills rather than silent swap exhaustion.

Step 1.2 — Start Services in Order (Morning, 1 hour)
Start Langfuse first. Open localhost:3000. Verify a test trace appears. From this moment every LLM call is visible.
Then start services one at a time verifying healthchecks: Memgraph, Qdrant, Ollama, Redis, Graphiti, Codebase-Memory-MCP, Serena-MCP, Context7-MCP, Coderunner-MCP, LiteLLM-proxy, Jan.

Step 1.3 — Pull Models (Start immediately, runs in background)
ollama pull qwen3:0.5b
ollama pull qwen3:4b
ollama pull qwen3:7b
ollama pull qwen3:3b
ollama pull nomic-embed-text
Start downloading Qwen3-35B-A3B Q4-K-M via huggingface-cli. 22GB. Runs all day in background.
Also download the DFlash draft checkpoint for Qwen3-35B-A3B from z-lab on HuggingFace. This is the block diffusion draft model that gives 2.5x speedup on top of the base model.

Step 1.4 — LiteLLM Configuration (Afternoon, 30 minutes)
Write the LiteLLM config.yaml with the five-tier fallback chain.
yamlmodel_list:
  - model_name: fallback-expert
    litellm_params:
      model: openai/qwen-3-235b-instruct
      api_base: https://api.cerebras.ai/v1
      api_key: os.environ/CEREBRAS_API_KEY
      rpm: 30

  - model_name: fallback-expert
    litellm_params:
      model: groq/llama-3.3-70b
      api_key: os.environ/GROQ_API_KEY
      rpm: 30

  - model_name: fallback-expert
    litellm_params:
      model: gemini/gemini-2.5-pro
      api_key: os.environ/GEMINI_API_KEY
      rpm: 5

  - model_name: fallback-expert
    litellm_params:
      model: mistral/mistral-large-latest
      api_key: os.environ/MISTRAL_API_KEY
      rpm: 2

  - model_name: fallback-expert
    litellm_params:
      model: openai/qwen3-35b-local
      api_base: http://localhost:30000/v1
      api_key: "local-bypass-key"

router_settings:
  routing_strategy: latency-based-routing
  enable_pre_call_check: true
  cooldown_time: 30
  num_retries: 3
  redis_host: "localhost"
  redis_port: 6379
  fallbacks:
    - fallback-expert:
        - groq-llama
        - gemini-pro
        - mistral-large
        - local-avx2
Test each API key by making one test call through LiteLLM. All four must respond before proceeding.

Step 1.5 — MCP Inspector Audit (Afternoon, 30 minutes)
Install MCP Inspector globally: npm install -g @mcpjam/inspector. Test all four MCP servers: Codebase-Memory, Context7, Serena, Coderunner. For each server verify protocol handshake passes and at least one tool invocation returns a result. Write down every tool name from every server. This list is your training data ground truth for tool-name validation.

Step 1.6 — Coderunner Sandbox Verification (Afternoon, 20 minutes)
Run five test cases through Coderunner MCP. Print statement returns 1.0. Infinite loop returns 0.0 within 5 seconds. Memory bomb returns 0.0. os.system call returns 0.0. Socket call returns 0.0. All five must pass.

Step 1.7 — Seed Bloodstream and Optuna Rank Ablation (Evening, launch overnight)
Run Codebase-Memory pipeline on one repository to seed Memgraph. ghgrab pulls code-review-graph repo, repomix compresses, Codebase-Memory writes AST nodes and edges to Memgraph. Verify at least 1,000 nodes via MATCH (n) RETURN count(n).
Launch Optuna rank ablation overnight. Ranks 4, 8, 16, 32 tested on 200 examples per organ. 5 organs x 4 ranks = 20 trials. Bayesian optimization selects best rank per organ. Primary metric is code-executable-pass rate via Coderunner.
End of Day 1: All services healthy in Langfuse, all MCP servers audited, seed bloodstream built, rank ablation running overnight.