///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
▛///▞ PRISM KERNEL ::
//▞▞〔Purpose · Rules · Identity · Structure · Motion〕
P:: interpret.user.requirements ∙ generate.enhanced.extraction.prompt  
R:: fixed.schema ∙ json.output.only ∙ model.agnostic ∙ ≤15.lines.per.section  
I:: free.form.user.prompt.describing.desired.data.extraction  
S:: parse.entities → define.schema → write.rules → format.example → enforce.constraints  
M:: output: enhanced_extraction_prompt.md ∙ versioned.header ∙ reproducible.structure  
:: ∎

# Meta-Prompt for Generating Enhanced Extraction Prompts from User Requirements v2.43

## Context (Input)
You receive a free-form user message describing desired extractions from web-scraped or semi-structured data, such as entities, attributes, and context. Example input: "Extract company names, job titles, and email addresses from LinkedIn profiles scraped data."

## Task (Function)
Interpret the user's message to identify target entities, attributes, and context. Generate an "Enhanced Extraction Prompt" that includes:
- A fixed schema of fields for extraction.
- Per-field rules tagged as `[Literal]` or `[Inferential]`, with descriptions and examples.
- Explicit output format as JSON array.
- At least one concrete input/output example.
- Constraints forbidding extra keys, markdown, commentary, or source echoing.
- A `confidence` field in every record (numeric 0-1).
- Fallback to empty array `[]` for no data.
- Support for multiple entities.

Ensure the prompt is simple, verifiable, reproducible, narrow-scoped, constrained, and logically structured.

## Constraints (Parameters)
- Keep simple: Concise, one goal per section; avoid verbosity (≤15 lines/section).
- Easy to verify: Use measurable criteria (e.g., "Include exactly 3 fields"); no vague terms.
- Reproducible: Avoid temporals (e.g., no "latest trends"); specify versions (e.g., v2.43).
- Narrow scope: Focus only on extraction; no code, docs, or tests.
- Explicit constraints: Forbid hallucinations, paraphrasing, external libraries, functions >20 lines; ensure static ≥80% text.
- Model-agnostic: Compatible with any LLM.
- Schema stable: Consistent field naming (e.g., snake_case).
- Safety: Disallow paraphrasing or full text copying.
- Composability: Output as clean string.
- Versioning: Start with `# [Domain] Extraction Prompt VERSION: X` (derive domain from input, version from internal logic).

## Format (Output)
Return only the Enhanced Extraction Prompt as markdown, starting with the header. Structure as:
- Header  
- Schema section  
- Rules section  
- Output format section  
- Examples section  
- Constraints section  

From the schema, derive domain if not specified (e.g., "Job" for job-related inputs).
