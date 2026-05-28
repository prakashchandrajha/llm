#!/bin/bash
# Test all cloud API keys through LiteLLM proxy
set -euo pipefail

LITELLM="http://localhost:4000/v1/chat/completions"
AUTH="Authorization: Bearer ${LITELLM_MASTER_KEY:-sk-litellm-master-2026}"
CT="Content-Type: application/json"

test_model() {
    local name="$1"
    local model="$2"
    echo -n "Testing $name ($model)... "
    RESP=$(curl -s --max-time 45 -w "\n__HTTP__%{http_code}" "$LITELLM" -H "$CT" -H "$AUTH" \
        -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply with exactly one word: WORKING\"}],\"max_tokens\":200}" 2>&1)
    HTTP=$(echo "$RESP" | grep "__HTTP__" | sed 's/__HTTP__//')
    BODY=$(echo "$RESP" | grep -v "__HTTP__")
    
    if echo "$BODY" | python3 -c "import sys,json; d=json.load(sys.stdin); m=d['choices'][0]['message']; c=m.get('content') or m.get('reasoning_content') or m.get('reasoning') or ''; print(f'✅ OK | model={d.get(\"model\",\"?\")} | response={c[:60]}')" 2>/dev/null; then
        return 0
    else
        echo "❌ FAIL | HTTP=$HTTP"
        echo "$BODY" | python3 -m json.tool 2>/dev/null | head -5
        return 1
    fi
}

echo "═══════════════════════════════════════════"
echo " LiteLLM Cloud API Test Suite"
echo " $(date)"
echo "═══════════════════════════════════════════"
echo ""

# Test active fallback tiers and core local models.
test_model "Cerebras public fallback" "fallback-expert" || true
sleep 2
test_model "Groq active tier" "fallback-expert-groq" || true
sleep 2
test_model "Mistral active tier" "fallback-expert-mistral" || true
sleep 2
test_model "OpenRouter Free active tier" "fallback-expert-openrouter-free" || true
sleep 2
test_model "NVIDIA active tier" "fallback-expert-nvidia" || true
sleep 2
test_model "Coordinator (0.6b)" "coordinator" || true
sleep 1
test_model "Master (8b)" "master" || true

if [[ "${RUN_DIRECT_MODEL_TESTS:-0}" == "1" ]]; then
    echo ""
    echo "Direct-only / caveat models"
    test_model "OpenRouter Auto (direct)" "fallback-expert-openrouter" || true
    sleep 2
    test_model "OpenRouter Qwen3 Coder free (direct)" "openrouter-qwen3-coder-free" || true
    sleep 2
    test_model "Cohere Command A (direct)" "cohere-command-a" || true
    sleep 2
    test_model "NVIDIA Reasoning (direct)" "nvidia-nemotron-reasoning" || true
    sleep 2
    test_model "Gemini (known quota caveat)" "fallback-expert-gemini" || true
    sleep 2
    test_model "DeepSeek (known balance caveat)" "fallback-expert-deepseek" || true
    sleep 2
    test_model "Aion Labs (quality caveat)" "fallback-expert-aion" || true
fi

echo ""
echo "═══════════════════════════════════════════"
echo " Test Complete"
echo "═══════════════════════════════════════════"
