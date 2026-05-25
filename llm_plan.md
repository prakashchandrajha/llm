
No AMX: Your i7-14650HX is Raptor Lake HX. AMX requires a specific microcode update. Run cat /proc/cpuinfo | grep microcode and check the version. If microcode is below 0x2e, update with sudo apt install intel-microcode && sudo update-initramfs -u && reboot. AMX may appear after the update. If it still does not appear after microcode update, KTransformers falls back to AVX2 which is still functional, just slower on expert offload.
sm_120 Blackwell: This is actually good news for inference speed. The issue is only prebuilt wheels. You build from source. One extra hour. Not a plan killer.
Real VRAM 7707 MB: The 8GB budget assumed full capacity. Adjust the budget to 7.5GB usable. This means KV cache drops from 3.0GB to 2.5GB. Every other allocation stays the same.


hint :The KV cache adjustment to 2.5GB is already applied in docker-compose.yml at line 199. The files are ready - mem0-server.py and the updated docker-compose.yml with:

Active mem0-server using python:3.11-slim + pip install mem0ai
LiteLLM healthcheck using wget (not curl)
KTransformers KV cache set to 2.5GB for 7.5GB usable VRAM




Hardware Reality Corrections — These Replace Every Previous VRAM Table
REAL VRAM BUDGET — 7707 MB usable, target 7500 MB
Coordinator Qwen3-0.5B Q8:      500 MB permanent
KTransformers attention layers:  3800 MB
XGrammar-2 compilation cache:    400 MB
Active KV cache (tightened):     2500 MB
Safety margin:                   300 MB
TOTAL:                           7500 MB ✓

KV cache at 2500 MB supports:
  - sequence length 512 outputs: fully supported
  - average organ output 65 tokens: fully supported
  - no quality impact from this reduction
KTransformers without AMX: AVX2 is available on your CPU. KTransformers falls back to AVX2 automatically. Expert offload is approximately 2x slower than AMX but still faster than pure llama.cpp for MoE models because KTransformers parallelizes expert computation across your 16 cores more efficiently than llama.cpp's sequential approach. The 35B fallback now generates at 4 to 8 tokens per second instead of 8 to 15. Still usable for the under 5 percent of queries that reach this tier.
sm_120 source builds: All packages that need source build are: KTransformers, flash-attn, bitsandbytes, xformers. These are one-time builds. Add 2 to 3 hours to Phase 0. Everything else in the plan is unchanged.

THE FINAL PLAN — HARDWARE-CORRECTED AND LOCKED

Phase 0: Hardware Verification, Docker Stack, Seed Bloodstream (Day 1)
Hardware Checks First
Check microcode version before anything else:
cat /proc/cpuinfo | grep microcode
sudo apt install intel-microcode
sudo update-initramfs -u
Reboot. Recheck AMX with grep amx /proc/cpuinfo. If AMX appears after microcode update, KTransformers runs at full speed. If it still does not appear, KTransformers runs on AVX2 path which is slower but functional. Either way the plan proceeds identically.
Run fio NVMe benchmark. Target above 3000 MB/s. This number matters more now because without AMX, cold expert loads from NVMe become more frequent.
Confirm GPU compute capability 12.0 via nvidia-smi. Confirm VRAM reads 7707 MiB. Confirm CUDA 13.2. Confirm cgroup v2 active.
Run 10-minute GPU thermal stress test. Record throttle temperature. Blackwell laptop GPUs can throttle more aggressively than desktop cards. If throttle happens within 5 minutes, clean cooling before any training.
Build All sm_120 Packages From Source
This is the one extra step sm_120 requires. Run these builds in order. Each is independent so if one fails you know exactly which package is the problem.
Build PyTorch for sm_120 first. Install from the nightly CUDA 13.2 wheel if available, otherwise build from source with TORCH_CUDA_ARCH_LIST=12.0.
Build bitsandbytes from source:
git clone https://github.com/TimDettmers/bitsandbytes
cd bitsandbytes
CUDA_VERSION=132 make cuda12x
python setup.py install
Build flash-attn from source with sm_120 flag:
FLASH_ATTENTION_FORCE_BUILD=TRUE \
MAX_JOBS=8 \
TORCH_CUDA_ARCH_LIST="12.0" \
pip install flash-attn --no-build-isolation
Build KTransformers from source:
git clone https://github.com/kvcache-ai/ktransformers
cd ktransformers
TORCH_CUDA_ARCH_LIST="12.0" \
CMAKE_CUDA_ARCHITECTURES="120" \
pip install -e . --no-build-isolation
For KTransformers, check the build log specifically for AVX2 versus AMX code path selection. If AMX is unavailable, it falls back to AVX2 silently. This is acceptable. Verify by running the KTransformers quick test and recording expert-offload throughput. Record this number as your actual 35B fallback speed baseline.
All other packages install normally because they do not have CUDA kernel components or already support sm_120.
Docker Stack
Write the complete Docker Compose file. Every service has mem_limit equal to memswap_limit enforcing the cgroup v2 hard limits. Services start in dependency order via healthcheck-based depends_on.
Inference profile services and their RAM limits: langfuse-web and langfuse-worker 0.5GB each, postgres 0.5GB, clickhouse 0.5GB, redis 0.2GB, minio 0.2GB, memgraph 2.5GB, qdrant 1.2GB, ollama 1.0GB, mem0-server 0.5GB, codebase-memory-mcp 0.5GB, serena-mcp 0.3GB, context7-mcp 0.1GB, coderunner-mcp 0.2GB, sglang-server 1.0GB, litellm-proxy 0.3GB, activepieces 0.4GB, routa 0.4GB, jan 0.5GB.
Training profile: identical except sglang-server is stopped and KTransformers GPU allocation is released.
Start Langfuse first. Verify traces appear at localhost:3000. Nothing is debugged blind from this point.
Start remaining services one at a time verifying each healthcheck before the next.
MCP Inspector Audit
Install MCP Inspector globally via npm install -g @mcpjam/inspector. Test Codebase-Memory MCP, Context7 MCP, Serena MCP, and Coderunner MCP through MCP Inspector before registering any tool names. Every tool name that appears in MCP Inspector's tool listing is a valid registered name. This list is your ground truth for the training data tool-name audit.
Coderunner Sandbox Stress Test
Coderunner MCP with Firejail sandboxing replaces the custom iptables sandbox entirely. Run all five stress tests through Coderunner: print statement returns 1.0, infinite loop returns 0.0 within 5 seconds, memory bomb returns 0.0, os.system call returns 0.0, socket.connect call returns 0.0. All five must pass before any training begins.
Pull Models
Pull via Ollama: qwen3:0.5b for Coordinator, qwen3:4b for Mem0 LLM and DoCoreAI, nomic-embed-text for Mem0 embeddings, qwen3:7b for master base, qwen3:3b for Synthesis. Start qwen3:35b-a3b:q4_K_M download immediately in background.
Seed Bloodstream
Run Codebase-Memory pipeline on code-review-graph repository only. ghgrab agent mode pulls tree JSON, then pulls relevant directories. repomix compresses with Tree-sitter. Codebase-Memory writes AST nodes and edges to Memgraph via Bolt. Verify MATCH (n) RETURN count(n) returns at least 1,000 nodes.
Optuna Per-Organ Rank Ablation
Run Optuna with four candidate ranks: 4, 8, 16, 32. Five organs times four ranks times 200 training examples equals 20 trials. Optuna's Bayesian optimization selects the best rank per organ. Estimated 2 to 3 hours. Run before sleeping on Day 1.
Launch autoresearch
Launch autoresearch overnight using the program.md written in Phase 1 (written during Phase 1 day, not yet launched). Note: autoresearch launches after program.md is written in Phase 1 Phase night.
Phase 0 complete when: Langfuse shows traces, all Docker healthchecks pass, all four sm_120 source builds compile without errors, KTransformers loads and reports expert-offload speed (record this number), all five Coderunner sandbox stress tests pass, Memgraph has seed nodes, Optuna rank ablation results ready.