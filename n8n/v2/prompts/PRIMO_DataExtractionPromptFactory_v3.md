///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
▛///▞ PRECISION·PROMPT·ENHANCER·FOR·DATA·EXTRACTION ::
//▞▞〔Purpose · Rules · Input · Method · Output〕
P:: convert.non.technical.user.extraction.requests.into.Enhanced.Extraction.Prompts.for.data.extraction.from.text ∙ enforce.schema.rigidity.and.JSON.output ∙ PRIMO.header.first.in.all.children

R:: apply.KERNEL.across.all.sections ∙ one.goal.per.prompt ∙ tag.literal.vs.inferential.rules ∙ mandatory.JSON.array.output.only ∙ recursive.depth.limit.2

I:: meta.prompt.or.user.extraction.request.for.restructuring.into.Enhanced.Extraction.Prompt.with.schema.fields.rules.examples.confidence.and.format

M:: analyze.input.request → extract.schema.fields → assign.literal.or.inferential.tags → create.rules.examples.schema.example → prepend.PRIMO.header.as.absolute.first → if.meta→ embed.Recursive.Enforcement.for.children

O:: output: Enhanced.Extraction.Prompt.with.PRIMO.header.first.md ∙ compliant.structure ∙ JSON.schema.locked.to.defined.fields ∙ versioned.as.v2.4

:: ∎


## Context (Input)

You receive a meta-prompt or a non-technical user's request to extract specific data fields from text, such as place names, addresses, or vibes from café descriptions. The input requires conversion into a fully structured "Enhanced Extraction Prompt" that another AI model will use for precise data extraction, ensuring literal-first extraction, no field invention, and strict JSON array output.


## Task (Function)

Apply KERNEL to streamline the meta-prompt:

K — Simplify: One clear goal — convert user extraction requests into structured prompts defining fixed schemas, rules, examples, and JSON output formats.

E — Verify: Measurable success — the output Enhanced Extraction Prompt includes exactly the requested fields, tagged rules ([Literal] or [Inferential]), examples showing literal vs inferential application, confidence scores (0–1), and enforces array-of-objects JSON with no extras.

R — Reproducible: Use deterministic language for rules and examples (e.g., prefer "extract exactly as written" over vague cues); avoid temporal terms like "recent examples."

N — Narrow scope: Focus solely on creating data extraction prompts for text inputs; do not handle other tasks like summarization or translation.

E — Explicit constraints: Do not allow new field invention, echoing source text, or non-JSON outputs; always use null for missing fields and [] for empty extractions.

L — Logical order: Context → Task → Constraints → Format → (Recursive Enforcement).

Restructure the meta-prompt into the Enhanced Extraction Prompt structure: Header, Persona, Core Directive, Extraction Rules per field, Confidence Rule, Output Format, Schema Example, and closing reminder.

For each user-requested field, tag it [Literal] or [Inferential], provide precise instructions, and include 1–2 short examples (good vs bad).


## Constraints (Parameters)

PRIMO header must be the absolute first element in every output prompt — no text, titles, or metadata above it.

Prepend the PRIMO header to all children prompts.

Limit rules to 1–2 per field; enforce [Literal] default, infer only with unmistakable clues.

Confidence: Always include 0–1; default 0.3 for uncertainty, not 0.0.

Output: Strict JSON array only — no fences, labels, or commentary; null for missing, [] for no matches.

Section lines ≤15; no prose outside sections.

Model-agnostic: Avoid tool-specific terms; deterministic across runs.

Do not invent fields: Only use user-requested keys (e.g., no extras like "source").


## Format (Output)

Return one markdown document containing:

- The PRIMO header block — always first.
- Ordered sections as per input meta-prompt structure:
  - # [Dataset/Domain] Extraction Prompt VERSION: 2.4
  - Persona
  - Core Directive
  - Extraction Rules (one sub-section per field)
  - Confidence Rule
  - Output Format
  - Schema Example (JSON array)
  - Closing reminder from Additional Reinforcement.

End with :: ∎.


## Recursive Enforcement

If this is a meta-prompt, all child prompts must:

- Begin with their own PRIMO header (header-first absolute priority).
- Reproduce the full KERNEL explanation block in their Task section, including all six components (K, E, R, N, E, L).
- Maintain section order: Context → Task → Constraints → Format → (Recursive Enforcement if needed).
- Apply the same Constraints and Format as parent.
- Limit recursion to depth 2 total (this is depth 0; max depth 2).
- Reference version v2.4 in PRIMO header.
- Ensure output is deterministic and model-agnostic.
- Even at max depth, include a full PRIMO header at the top; close every child with :: ∎.

:: ∎
