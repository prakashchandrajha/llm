

# THE DEFINITIVE LOCKED FINAL PLAN

---

## Your Confirmed Hardware

i7-14650HX, 16 cores 24 threads, AMX supported, Ubuntu 24.04.4 LTS. RTX 5050 8GB GDDR7 VRAM, CUDA 13.2. 24GB DDR5 5600MHz, one empty slot. Micron 1TB NVMe SSD. This is everything. No purchases. No cloud GPU.

---

## What You Are Building

A machine-first intelligence infrastructure where GitHub repos and HuggingFace datasets are parsed into AST graphs before training. The model learns to navigate structured knowledge rather than recall flat text. At inference time, FLARE monitors generation confidence and queries the local AST graph only when the model is uncertain. KTransformers distributes a large sparse MoE model across VRAM, RAM, and SSD simultaneously. The entire system runs locally, improves from every use, and costs zero after setup.

---

## Three-Tier Memory Architecture

This is the core physics-beating design. Every hardware component has one job.

VRAM 8GB holds attention mechanisms, MLA matrices, shared experts, and the active KV cache. These are accessed on every token and benefit from GPU bandwidth.

System DRAM 24GB holds hot routed experts currently being computed. The i7 CPU executes these experts using AMX instruction sets directly in RAM without touching the GPU.

NVMe SSD 1TB holds cold routed experts and deep historical prefix caches. GPU Direct Storage enables direct DMA from SSD to VRAM bypassing CPU memory entirely, achieving 3 to 4x layer loading speedup versus standard file I/O.

These three tiers operate as one unified memory pool. The model never knows it is distributed. It just runs.

---

## DAY ZERO: Environment Verification and Complete Installation

Verify hardware before installing anything. Run fio sequential read on NVMe: target above 3GB/s. Below 2.5GB/s means cold expert loading will bottleneck inference. Check that AMX is available in CPU flags with grep amx /proc/cpuinfo. Verify CUDA 13.2 with nvidia-smi and verify Python sees your GPU.

Install KTransformers from source to get AMX kernel support for your specific i7. The pip version may not include the latest AMX optimizations. Clone the KTransformers repo and build with CUDA 13.2 and AMX flags enabled.

Install MemAscend for pinned-memory optimization during training. Install ZenFlow for gradient prioritization during training.

Install SGLang with RadixAttention for the fast inference path.

Build llama.cpp from source with CUDA and GPU Direct Storage enabled if your system supports GDS. Install dots.ocr GGUF files for document parsing.

Install the knowledge graph stack in this order: Tree-sitter Python bindings first, then code-review-graph which depends on Tree-sitter for AST parsing, then Graphify for knowledge graph visualization and community detection, then Understand-Anything for multi-agent semantic analysis.

Install the data pipeline: ghgrab, repomix, Firecrawl, PageIndex, Distilabel.

Install the training stack: Axolotl with Unsloth backend, ART from OpenPipe for GRPO, autoresearch from jsegov fork. Run one 5-minute autoresearch test experiment to confirm it works on your GPU.

Install memory layer: MemPalace with ChromaDB and SQLite. Initialize it immediately.

Install FastMCP, rank-bm25, sentence-transformers, MCP Toolbox binary, n8n via Docker, AnythingLLM via Docker.

Install OpenClaw-RL for continuous model improvement from live usage.

Download models: Qwen3-8B via Ollama for the fast router. Start downloading Qwen3-35B-A3B Q4-K-M immediately. 22GB. Start it now and let it run.

Run the smoke test: SGLang serves Qwen3-8B, KTransformers loads a test model, code-review-graph initializes an SQLite AST database on a sample directory, FLARE fires on a test generation, MemPalace stores and retrieves a test entry. All five passing means Day Zero is done.

---

## DAY 1: Schema Design and AST-Native Training Format

The most important day. Paper only for the first three hours.

Your model outputs machine state. It never outputs prose. Define the schema once and lock it.

The schema has these fields: intent (one of ten exact values), confidence (float 0 to 1), domain, target-model (local-fast, local-strong, local-deep), exec-ready (boolean, true only when tools-needed is non-empty), ast-context (always null in training, populated at runtime by code-review-graph), steps (list max five items), output-format (code, json, text, bool), tools-needed (exact registered tool names only), memory-check (boolean), next (explicit state name), fallback (explicit route), error (compact error or null), state-id (UUID).

Ten intents: route, code, reason, classify, retrieve, summarize, plan, debug, evaluate, handoff.

The novel training format is the key insight from the senior's document. Each training example has three parts. Part one is the query. Part two is the AST traversal path that answers it, formatted as a sequence of node types and relationship edges from the code-review-graph SQLite database. Part three is the structured schema output. The model learns to generate an AST path before generating the schema. This is what teaches the model to navigate structured knowledge rather than hallucinate from memory.

An example of this format for a coding task: the query asks for a safe JSON parser. The AST path shows the traversal: function node json.loads, exception node JSONDecodeError, pattern node try-except, then the structured output with intent code, exec-ready true, steps for the logical build sequence, tools-needed containing code-executor. The model seeing thousands of these examples learns that code questions require AST traversal before schema output.

Write 30 hand-crafted examples in this format. Spend at minimum three hours. Write ten code examples, ten reasoning examples, ten boundary cases. The boundary cases are the most important training signal in your entire dataset and cannot be automated.

Write five reward functions: valid-JSON (1.0 or 0.0), required-fields (checks only intent-specific fields), intent-valid (exact ten strings, case-sensitive), exec-consistency (exec-ready true only when tools-needed is non-empty), token-economy (1.0 at 40 tokens, linearly to 0.0 at 150 tokens). Combined weights: 0.30, 0.25, 0.20, 0.15, 0.10.

Write test-schema-py and verify all 30 examples pass before Day 1 ends.

Write Axolotl training YAML with Qwen3-8B base, LoRA rank 16 starting point, QLoRA 4-bit, completions-only mode, sequence length 512. Version-control this file.

---

## DAY 2: Build the AST Knowledge Graph Bloodstream

This day builds the structured knowledge that makes your model genuinely intelligent rather than statistically fluent.

The pipeline for every repository runs in this exact sequence. ghgrab fetches the repository tree as JSON to identify which directories contain relevant code before downloading anything. Then ghgrab pulls only those directories. Then repomix compresses the directory into a single LLM-readable file using Tree-sitter to strip implementation details while preserving code signatures. For documents over 20 pages, PageIndex builds a hierarchical tree index preserving structural hierarchy. Then code-review-graph runs Tree-sitter over the repomix output to parse functions, classes, imports, and variables into its local SQLite database. Then Leiden community detection runs over the compiled graph to cluster related nodes into thematic modules. PageRank and Tarjan SCC identify god nodes and circular dependencies. Then Understand-Anything runs its multi-agent pipeline to generate plain-English summaries of every node and map technical structures to logical workflows. The resulting combined artifact feeds LightRAG for retrieval.

Run this full pipeline on five repositories: langchain agents and tools directories, llama-index agent core, autoresearch source, ktransformers operators, code-review-graph source itself. Processing code-review-graph on its own source is intentional — the system learns the tool it uses to understand code.

Run Firecrawl LLMs.txt on five documentation sites. Feed PageIndex on every documentation site output because technical docs have deep hierarchy. Feed the tree-indexed docs into LightRAG.

Download HuggingFace datasets in parallel: 8,000 from AM-DeepSeek-R1-Distilled-1.4M, 8,000 from OpenHermes-2.5, 5,000 from Magpie-Reasoning-V2-250K, 5,000 from CodeFeedback-Filtered-Instruction.

Convert HuggingFace examples to AST training format. For each example, run a code-review-graph query using the example's input. code-review-graph returns the AST subgraph relevant to that query. Insert that subgraph as the AST path section between the query and the output. This is the step that converts generic HuggingFace data into your novel training format.

Generate 5,000 additional examples via ART AutoRL.

Register the code-review-graph SQLite database as a local MCP server. This exposes query-graph, pagerank, shortest-path, and get-neighbors as callable tools for agents during inference.

---

## DAY 3: Dataset Conversion, FLARE Configuration, and autoresearch Launch

Auto-convert all raw examples. Keyword rules classify intent. Only intent-specific required fields populated. ast-context is null in every training example without exception. state-id as UUID, error as null. JSONL output.

Run Distilabel filtering: remove below 0.65 confidence, under 40 character inputs, near-duplicates via MinHash LSH, examples where any reward function returns below 0.5, examples where tools-needed contains tool names not registered in your MCP server.

Run test-schema-py against 200 random cleaned examples. Target 90 percent passing all five reward functions. If below 88 percent, find the failing intent class and fix its keyword rules.

Configure the FLARE loop for inference. Write flare-engine.py. During generation, after each token, check the token log probability. If it falls below your configured threshold, pause generation. Extract the low-confidence segment as a forward-looking query. Run a targeted code-review-graph query against the local SQLite MCP server. Inject the returned AST subgraph as a context patch. Regenerate the segment. This loop fires only when the model is uncertain. It keeps context compact while eliminating hallucination.

Write program.md for autoresearch: goal is finding optimal LoRA configuration for Qwen3-8B on AST-format training data, hardware is RTX 5050 with 8GB VRAM plus MemAscend for RAM optimization plus ZenFlow for gradient prioritization, five minutes per experiment, variables are LoRA rank 8 to 64 and learning rate and alpha and target modules and sequence length, constraints are QLoRA 4-bit always and completions-only always and must fit in 8GB VRAM.

Upload cleaned dataset to HuggingFace private. Launch autoresearch before sleeping. 100 experiments overnight.

---

## DAY 4: SFT Training with ZenFlow and MemAscend

Apply autoresearch winning configuration to Axolotl YAML. Enable ZenFlow to keep top gradients in VRAM and offload the rest to RAM. Enable MemAscend to optimize pinned-memory allocations and reduce peak RAM usage by approximately 40 percent during training.

Stage one is format SFT on simpler examples with zero or one step items. Two epochs. Completions-only mode is mandatory. Expected time on RTX 5050 with these optimizations: 4 to 6 hours. Save checkpoint to HuggingFace after each epoch.

Watch training loss. Should drop from 2.0 toward 0.9 by end of epoch one. Plateau above 1.5 at step 500 means chat template is wrong. Stop and fix before continuing.

Stage two is reasoning SFT on complex examples with three or more step items including the AST traversal paths. One epoch. Expected time: 2 to 3 hours.

Merge LoRA before export. Export to GGUF Q5-K-M. Register in SGLang. Run all 30 hand-crafted examples. Target 85 percent JSON validity and 78 percent intent accuracy.

---

## DAY 5: GRPO Reinforcement Learning via ART

Load Day 4 checkpoint into ART. Combined reward function at established weights. Num-rollouts 4. Learning rate 1e-5.

Select 50 most ambiguous boundary-case examples as GRPO environment. These are the examples where the AST traversal path is unclear because the query spans multiple domains. GRPO learns from variance. Hard boundary examples that sometimes succeed and sometimes fail provide the clearest gradient.

Activate ART MCP-RL simultaneously pointing at your code-review-graph MCP server. ART generates training scenarios from every exposed tool: query-graph, pagerank, shortest-path, get-neighbors. After MCP-RL, the model reliably outputs the correct tool names for AST queries.

Monitor combined reward every 10 steps. Should climb from 0.65 toward 0.85. Crash after climbing means reduce learning rate to 5e-6. Never moves above 0.70 after 50 steps means a reward function has a bug outside 0.0 to 1.0 range.

At step 50 and 100, run all 30 examples through the checkpoint. JSON validity and intent accuracy should climb. Token length climbing instead of falling means token-economy weight is too high. Reduce to 0.05.

Stop when combined reward plateaus for 20 consecutive steps. Merge LoRA. Export GGUF Q5-K-M. Download.

Go/no-go before Day 6: JSON validity 92 percent or higher, intent accuracy 85 percent or higher, average output tokens 65 or fewer, zero crashes on all 30 examples.

Launch autoresearch overnight targeting GRPO configuration. Update program.md with GRPO-specific variables.

---

## DAY 6: Full System Integration

Wire in strict order. Each component reaches verified working state before the next.

KTransformers three-tier deployment for the 35B deep tier. Configure the optimize-config.yaml assigning attention layers and MLA matrices and shared experts to VRAM, hot routed experts to system DRAM with AMX execution, cold experts to NVMe SSD with GPU Direct Storage DMA. Enable Expert Deferral. Enable the 3-layer GPU-CPU-SSD prefix cache. Verify with a real query timing measurement. Target 8 to 15 tokens per second after expert cache warmup.

SGLang serving your fine-tuned 9B model with RadixAttention and XGrammar-2 TagDispatch. Verify all five test queries return valid typed Pydantic objects.

FLARE engine wired to SGLang generation stream and code-review-graph MCP server. Test: generate a response about your codebase, verify FLARE pauses at low-confidence tokens, queries the AST graph, injects the context patch, regenerates. Measure latency overhead. FLARE adds approximately 50 to 100ms when it fires. It should not fire on high-confidence tokens.

FastMCP coordinator using BM25 plus MiniLM-L6-v2. Under 5ms routing. Queries MemPalace before every dispatch. High-confidence MemPalace hit returns adapted prior trace and skips model inference entirely.

MemPalace for lossless trace storage. Wire to store every successful execution trace. Query before every model call. Seed with your 30 hand-crafted examples immediately.

code-review-graph MCP server exposing query-graph, pagerank, shortest-path, get-neighbors to all agents. The blast-radius analysis fires on every file save or git commit, re-parsing only changed AST nodes. Agents receive the minimal subgraph relevant to their query rather than full file contents.

LiteLLM fleet dispatch: local-fast to Qwen3-4B via Ollama, local-strong to your fine-tuned 9B via SGLang, local-deep to 35B MoE via KTransformers.

MCP Toolbox after tool-name audit. Every value in tools-needed across your entire training dataset must have a registered MCP tool. Fix all mismatches first.

Gate validation layer as deterministic Python rule checks. No LLM call. Fires on every organ output. Triggers retry with error field populated on failure. Escalates to 35B after two failures.

OpenClaw-RL wired to SGLang endpoint. Successful routing decisions are positive reward. Failed tool calls are negative reward. Runs on idle GPU cycles.

n8n for handoff intent workflows. AnythingLLM as UI connecting all components.

MessagePack on every model output. One line. 10x faster parse.

Token-Optimizer audit after full integration. Find ghost tokens. Remove unfired MCP tools.

---

## DAY 7: Validation and Packaging

Run all 30 hand-crafted examples through the complete pipeline. Full pipeline means: FastMCP routing, MemPalace query, code-review-graph AST context retrieval, FLARE-augmented model inference, XGrammar-2 output guarantee, Gate validation, LiteLLM dispatch, tool execution, MemPalace storage, MessagePack output.

Measure: JSON validity targeting 100 percent, intent accuracy targeting 88 percent or higher, average output tokens targeting 65 or fewer, MemPalace recall rate targeting 20 percent or higher after seeding, 9B router latency targeting under 300ms, 35B KTransformers targeting 8 to 15 tokens per second, FLARE benefit targeting reduced hallucination rate measurable by Gate rejection rate before versus after FLARE enabled.

Run 20 adversarial tests: five ambiguous boundary queries, five with typos, three under five words, two in Hindi or mixed Hindi-English, five that should trigger handoff intent. Acceptance criteria: valid JSON, valid intent, zero crashes.

Run the blast-radius test. Make a code change in a tracked file. Verify code-review-graph's file-hash-deduplicated CPU hook fires, re-parses only the changed AST nodes, and the next agent query receives the updated subgraph without full re-indexing.

Run the error recovery test. Disable one MCP tool. Run five queries requiring it. Confirm error field populates correctly in subsequent schema outputs and fallback routes to an alternative.

Package as Docker Compose. The compose includes: SGLang with fine-tuned GGUF, KTransformers with 35B model mounted from SSD, dots.ocr llama-server on port 8111, code-review-graph MCP server with SQLite database, Graphify for visualization, Understand-Anything, LightRAG with persistent graph store, MemPalace, LiteLLM, FastMCP coordinator, Gate validation, MCP Toolbox, n8n, AnythingLLM, OpenClaw-RL. Port 8080, POST input, returns MessagePack AgentState.

---

## Complete Final Tool Stack

```
PHYSICS-BEATING HARDWARE LAYER
Three-tier memory pool:
  VRAM 8GB     attention, MLA, shared experts, active KV cache
  DRAM 24GB    hot routed experts, AMX execution by i7 CPU
  NVMe 1TB     cold experts, historical prefix caches, full model
GPU Direct Storage (GDS)  direct DMA NVMe-to-VRAM, bypasses CPU
KTransformers             AMX kernels, Expert Deferral, 3-layer cache
                          27.7x prefill speedup over llama.cpp baseline
MemAscend                 40% RAM reduction during training
ZenFlow                   top gradients in VRAM, rest offloaded to RAM

AST KNOWLEDGE BLOODSTREAM
code-review-graph         Tree-sitter AST to SQLite, 49x token reduction
                          blast-radius analysis on every file change
                          MCP server: query_graph, pagerank, shortest_path
                          this is the bloodstream all agents read from
Graphify                  Leiden clustering, god node detection, visualization
Understand-Anything       multi-agent semantic summaries of every AST node
LightRAG                  graph + vector retrieval for natural language queries
repomix                   codebase compression preserving code signatures
ghgrab                    surgical repo extraction, agent mode tree JSON first
PageIndex                 hierarchical tree index for long docs before LightRAG
Firecrawl LLMs.txt        clean documentation crawl

INTELLIGENCE SOURCES
HuggingFace datasets      26000 examples from DeepSeek-R1, GPT-4, Llama-405B
                          converted to AST traversal training format
ART AutoRL                5000 examples from plain English description

TRAINING — LOCAL RTX 5050 ONLY
autoresearch jsegov fork  100 overnight experiments, optimal config found
Axolotl with Unsloth      YAML-orchestrated two-stage SFT
                          completions-only always, merge LoRA before export
ZenFlow + MemAscend       enable during training for VRAM and RAM efficiency
ART GRPO + MCP-RL         RL on boundary cases, exact AST tool name training
OpenClaw-RL               continuous RL from live usage, idle GPU cycles

INFERENCE GENERATION LOOP
SGLang + RadixAttention   fine-tuned 9B serving, shared-prefix cache
XGrammar-2 TagDispatch    guaranteed valid JSON at token sampling level
FLARE engine              monitors token log probabilities during generation
                          pauses at low confidence, queries AST graph
                          injects context patch, regenerates segment
                          eliminates hallucination at source not aftermath
KTransformers 35B         deep fallback, heterogeneous three-tier execution
dots.ocr GGUF             3B document parser, 4.2GB VRAM, port 8111

MEMORY
MemPalace                 verbatim trace storage, ChromaDB + SQLite, free
                          96.6% recall, zero API, zero cloud

ROUTING AND DISPATCH
FastMCP                   async MCP framework, BM25 + MiniLM-L6-v2
                          under 5ms routing, zero VRAM consumed
Gate layer                deterministic Python rules, no LLM call
LiteLLM                   target-model field to correct local backend
MCP Toolbox               real tool execution, audit all names first
n8n                       external workflows from handoff intent
AnythingLLM               UI layer connecting all components

QUALITY
test-schema-py            30 ground truth examples run every day
Token-Optimizer           ghost token elimination after integration
12-Factor-Agents          every decision checked here

TRANSPORT
MessagePack               one line, 10x faster parse, 30% smaller

NOT IN PLAN
Memanto                   paid Moorcheh API key required
MiroFish                  public opinion simulation, not training tool
Paperweight               email privacy tool, zero relevance
AirLLM                    sequential dense layer loading, too slow for MoE
GridSearchCV              sklearn classical ML, wrong tool
Colab                     unreliable GPU, not needed
```

---

## What You Have After Day 7 and Why It Beats Static Models

The model does not memorize answers. It learns to navigate AST graphs. When an agent asks about your codebase, the model generates an AST traversal path to the answer using code-review-graph's SQLite database, then outputs structured machine state. This is why a 9B model trained on graph traversal outperforms a 400B model trained on flat text for your specific domain: the 400B model hallucinated from token statistics while your 9B model navigated actual structure.

FLARE ensures the model never generates low-confidence tokens without pausing to verify against the AST graph. Hallucination becomes structurally impossible for code and technical queries.

The three-tier memory pool means your 35B MoE fallback runs at 8 to 15 tokens per second across VRAM plus DRAM plus SSD simultaneously. This is the heterogeneous execution that beats physics — you do not need more hardware, you orchestrate existing hardware correctly.

After one week of real agent use, MemPalace handles 20 to 30 percent of queries from prior traces. OpenClaw-RL improves the model continuously from real usage on idle GPU cycles. autoresearch runs every Sunday night with an updated program.md reflecting the week's failure patterns. The system compounds intelligence from every use while any cloud model remains static.

Start Day Zero tonight. Verify NVMe speed with fio first. Verify AMX availability in CPU flags second. Everything follows from those two numbers.
