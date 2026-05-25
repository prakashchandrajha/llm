# Phase 0 — Hardware Check Report

Date: 2026-05-25
Host: i7-14650HX laptop, RTX 5050 Laptop GPU, 24 GB RAM, 1× NVMe (937 GB)

## 1. NVMe sequential read (fio)
- Command: `fio --rw=read --bs=1M --size=2G --iodepth=16 --direct=1 --ioengine=libaio --runtime=20 --time_based`
- Result: **READ bw = 4817 MiB/s ≈ 5050 MB/s**, IOPS=4816
- Threshold: ≥3000 MB/s — **PASS**
- KTransformers expert NVMe fallback path: feasible from disk perspective.

## 2. AMX in CPU flags
- `grep -i amx /proc/cpuinfo` → **no match**
- i7-14650HX is Raptor Lake-HX Refresh; AMX is **not present** (only Sapphire/Emerald Rapids server CPUs and Granite Rapids client carry AMX).
- Microcode: not checked (deferred — kernel/microcode update would require sudo + possible reboot).
- **Implication:** KTransformers AMX-optimized expert kernels are unavailable on this host. The plan's CPU-side expert offload performance estimates (which assume AMX) will not hold. KTransformers must be configured with the generic AVX2/AVX-512 path, or replaced with llama.cpp CUDA for the 35B fallback. **KTransformers install deferred per user instruction.**

## 3. GPU
- `nvidia-smi`: NVIDIA GeForce RTX 5050 Laptop GPU, driver 595.71.05, CUDA 13.2, 8151 MiB total, idle 15 MiB, 45 °C, P4.
- PyTorch CUDA capability: **major=12, minor=0 (sm_120, Blackwell)**, total_memory **7707 MB**, 20 SMs.
- Plan requirement: capability ≥ 8.9 — **PASS** (12.0 > 8.9).
- **VRAM caveat:** 7707 MB usable, not full 8 GB. Plan budget 0.5+4.0+0.5+3.0 = 8.0 GB has zero headroom; KV cache will need to be trimmed to ≤2.7 GB or attention layer count reduced.
- **sm_120 caveat:** Prebuilt wheels for KTransformers, flash-attn, xformers, bitsandbytes typically target sm_80/86/89/90. Any GPU-kernel package will need to be built from source against CUDA 13.2 with `TORCH_CUDA_ARCH_LIST=12.0`.

## 4. GPU 10-min thermal stress test
- **DEFERRED** per user instruction (will revisit before Phase 1 training).
- Recommend `gpu-burn` or `nvidia-smi dmon` with sustained `python -c "import torch; x=torch.randn(8192,8192,device='cuda'); [x@x for _ in range(100000)]"`.

## 5. cgroup v2
- `cat /sys/fs/cgroup/cgroup.controllers` → `cpuset cpu io memory hugetlb pids rdma misc dmem`
- cgroup v2 unified hierarchy **active**. No kernel boot-param edit required. **PASS**

## 6. Docker
- `docker --version` → 29.4.2 (cgroup driver: v2). **PASS**
- `docker compose version` → v5.1.3 (Compose v2-syntax compatible). **PASS**

## Resource budgets (24 GB RAM host) — to enforce in compose
| Service | Plan limit | Notes |
|---|---|---|
| OS reserved | 3.5 GB | not a container |
| Langfuse stack total | 1.8 GB | pg+ch+redis+minio+web+worker combined |
| Memgraph | 2.5 GB | |
| Qdrant (Mem0) | 1.2 GB | |
| Ollama models in-RAM | 1.0 GB | host model cache reservation |
| KTransformers hot experts | 6.0 GB | **deferred** |
| Master 7B Q4-K-M | 6.0 GB | served via Ollama in inference, off in training |
| Context7 MCP | 0.1 GB | |
| Serena MCP | 0.3 GB | |
| Coderunner MCP | 0.2 GB | |
| Pipeline overhead | 0.8 GB | shell + python harness |
| Safety margin | 0.6 GB | |
| **Total** | **24.0 GB** | |

In training mode, KTransformers profile is disabled → ~6 GB RAM and 4 GB VRAM freed
for the training job (cgroup hard limit 14 GB via systemd-run).
