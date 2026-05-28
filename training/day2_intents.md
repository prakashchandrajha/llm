# Day 2 Intent Boundaries

## route
Definition: choose the organ or organ chain that should handle the request.
Clear examples: route a code generation request to code-organ; route a failing traceback to debug-organ; route a schema check to data-organ; route a synthesis request to synthesis-organ; route a multi-step proof to reason-organ.
Boundary examples: code-looking request that only asks who should handle it; debug-looking request that only needs routing; retrieval-looking request that must pick graph versus docs first; plan-looking request whose output is only an organ chain; summarize-looking request asking which organ should summarize.

## code
Definition: generate, complete, or modify executable code.
Clear examples: write a parser; modify a function; add a test; implement a CLI flag; generate a migration.
Boundary examples: code wording but asks for a plan; error text where the answer is a patch; evaluation request where no code should be generated; retrieval request asking where code lives; debug request that needs diagnosis before code.

## reason
Definition: produce a connected chain of at least three reasoning steps.
Clear examples: explain a tradeoff; choose an architecture; infer root cause; compare fallback paths; reason from graph evidence.
Boundary examples: multi-step output that is only a plan; retrieval that needs no inference; classification with a single category; code task with simple implementation; summary that compresses prior reasoning.

## classify
Definition: assign a request or object to a defined class.
Clear examples: classify an intent; classify an error type; classify risk level; classify tool need; classify handoff target.
Boundary examples: retrieval question with categorical answer; debug text that asks only for error class; code task that asks for language category; evaluate request that requires pass/fail; route request where class equals organ.

## retrieve
Definition: fetch knowledge from Graphiti, Codebase-Memory, Context7, or another memory source.
Clear examples: get symbol neighbors; find docs for a library; fetch prior decision; retrieve AST context; find a snippet.
Boundary examples: retrieve-looking prompt that asks for classification; code prompt that needs graph context first; reason prompt where retrieval is only one step; summarize prompt asking to compress retrieved nodes; evaluate prompt asking whether retrieved facts are sufficient.

## summarize
Definition: compress information into a short, dense output.
Clear examples: summarize trace findings; summarize organ outputs; summarize a graph query; summarize test failures; summarize a handoff.
Boundary examples: summary request that asks for next actions; route request requiring organ chain; evaluate request requiring pass/fail; retrieve request asking for source facts; reason request needing causal steps.

## plan
Definition: produce ordered future actions.
Clear examples: plan Day 2 tasks; plan test rollout; plan dataset validation; plan service restart; plan fallback hardening.
Boundary examples: multi-step reasoning not intended as actions; code task that asks for implementation now; debug task that asks for immediate fix; route task that only picks organs; handoff task that creates external work.

## debug
Definition: diagnose and fix a failure, with an error field.
Clear examples: fix traceback; explain failing test; resolve bad config; repair API 429 handling; diagnose container unhealthy.
Boundary examples: error-looking request that only asks for classification; code task that includes no failure; evaluate request that judges a fix; retrieve request asking for logs only; plan request for a debugging strategy.

## evaluate
Definition: assess correctness or quality, usually as bool or JSON.
Clear examples: validate schema; grade output; check tool list; assess risk; verify service health.
Boundary examples: debug request where failing output must be fixed; classify request that only assigns type; summarize request that compresses findings; route request that picks next organ; retrieve request that gathers evidence before judging.

## handoff
Definition: escalate to a human or external workflow.
Clear examples: send quota fix to user; create Activepieces workflow; ask human for missing key; schedule long training; escalate repeated gate failure.
Boundary examples: plan request that mentions a human but needs steps; summarize request for handoff text only; route request selecting handoff path; debug request that can be fixed locally; evaluate request deciding if handoff is needed.

