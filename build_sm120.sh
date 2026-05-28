#!/bin/bash
# Build sm_120 packages: flash-attn + KTransformers
# Logs to /home/vvd/prakash/xorz/llm/phase0-checks/build_sm120.log
set -e
LOG=/home/vvd/prakash/xorz/llm/phase0-checks/build_sm120.log
exec > >(tee -a "$LOG") 2>&1

export TORCH_CUDA_ARCH_LIST="12.0"
export CUDA_HOME=/usr
export MAX_JOBS=4

echo "=== BUILD START $(date) ==="
echo "PyTorch: $(python3 -c 'import torch; print(torch.__version__)')"
echo "nvcc: $(nvcc --version | grep release)"

# ── 1. Uninstall broken flash_attn stub ──────────────────────────────────────
echo "--- Removing stub flash_attn ---"
pip uninstall -y flash-attn 2>/dev/null || true
pip uninstall -y flash_attn 2>/dev/null || true

# ── 2. Build flash-attn from source ─────────────────────────────────────────
echo "--- Cloning flash-attention ---"
cd /tmp
rm -rf flash-attention
git clone --depth 1 https://github.com/Dao-AILab/flash-attention.git
cd flash-attention
echo "--- Building flash-attn (this takes ~60-90 min) ---"
pip install -v --no-build-isolation . 2>&1
echo "--- flash-attn DONE ---"

# ── 3. Build KTransformers from source ──────────────────────────────────────
echo "--- Cloning KTransformers ---"
cd /tmp
rm -rf KTransformers
git clone --depth 1 --recurse-submodules https://github.com/kvcache-ai/ktransformers.git
cd ktransformers
echo "--- Building KTransformers ---"
pip install -v --no-build-isolation . 2>&1
echo "--- KTransformers DONE ---"

# ── 4. Verify ────────────────────────────────────────────────────────────────
echo "--- Verification ---"
python3 -c "from flash_attn import flash_attn_func; print('flash_attn: OK')" 2>&1
python3 -c "import ktransformers; print('ktransformers:', ktransformers.__version__)" 2>&1

echo "=== BUILD COMPLETE $(date) ==="
