# autoresearch Program: Day 2 Warm Start

Primary metric: weighted validation score across held-out organ examples.

Weights:
- Code Organ code-executable-pass: 0.40
- Debug Organ code-executable-pass: 0.30
- Reason Organ chain-step-validity: 0.30

Search space:
- learning_rate: 5e-5 to 5e-4
- batch_size: 2, 4, 6, 8 within the 14 GB training limit
- warmup_steps: 10 to 100
- gradient_accumulation_steps: 2 to 8
- lora_alpha: 8 to 64
- sequence_length: 256 or 512

Fixed:
- base_model: Qwen3-8B local master base unless Day 4 swaps to a HuggingFace Qwen3-7B checkpoint
- qlora: 4-bit
- completions_only: true
- per-organ LoRA rank: fill from Optuna result before Day 4
- ZenFlow: enabled when installed
- MemAscend: enabled when installed

Allowed modifications:
- optimizer choice
- scheduler warmup shape
- data ordering
- gradient accumulation policy
- training-loop instrumentation

Forbidden modifications:
- changing the Day 2 schema
- removing required reward functions
- changing the 6-per-organ AST context ratio
- training on proprietary code outside approved local repos

