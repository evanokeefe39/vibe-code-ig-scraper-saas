# Functional Requirements (What the Meta-Template Must Do)

| ID      | Requirement                     | Description                                                                                         | Verification Criteria                                                                                             |
| ------- | ------------------------------- | --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **F1**  | **Input Interpretation**        | Accept a free-form user message describing what data they want extracted.                           | The meta-prompt correctly identifies target entities, attributes, and context from natural language input.        |
| **F2**  | **Schema Definition**           | Generate a fixed, explicit list of fields to be extracted.                                          | Enhanced prompt includes a schema section or field list that can be validated by downstream logic.                |
| **F3**  | **Rule Generation**             | Produce per-field extraction rules, each tagged as `[Literal]` or `[Inferential]`.                  | Each field definition includes rule type, behavior description, and examples.                                     |
| **F4**  | **Output Format Specification** | Define exactly how the extraction model must format its output JSON.                                | Enhanced prompt enforces valid JSON array output with correct field names and fallback patterns (`null` or `[]`). |
| **F5**  | **Example Construction**        | Provide concrete examples of correct and incorrect outputs.                                         | At least one illustrative input/output example appears in every enhanced prompt.                                  |
| **F6**  | **Constraint Enforcement**      | Include directives that forbid extra keys, markdown fences, commentary, or source text echoing.     | Generated prompt always contains explicit “forbidden behavior” reminders.                                         |
| **F7**  | **Confidence Rule Definition**  | Require and define behavior for a `confidence` field.                                               | Downstream model instructed to include `confidence` in every record.                                              |
| **F8**  | **Error/Fallback Behavior**     | Specify how to handle cases with no extractable data.                                               | Enhanced prompt mandates returning `[]` instead of null or empty string.                                          |
| **F9**  | **Multi-Entity Handling**       | Allow multiple entities per input when appropriate.                                                 | Enhanced prompt instructs downstream model to return multiple JSON objects in one array.                          |
| **F10** | **Output Delivery**             | Output a single, self-contained *Enhanced Extraction Prompt* suitable for immediate downstream use. | Output text contains no commentary and begins with header line `# [Domain] Extraction Prompt VERSION: X`.         |

# Non-Functional Requirements (Qualities & Constraints)

| ID       | Requirement                      | Description                                                                                      | Measure / Target                                                                |
| -------- | -------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------- |
| **NF1**  | **Reproducibility**              | Same user input should yield functionally identical enhanced prompts over time.                  | ≥ 95 % textual consistency at temperature ≤ 0.2                                 |
| **NF2**  | **Simplicity**                   | Avoid verbosity; each rule must be concise and action-oriented.                                  | Average section length ≤ 15 lines; no redundant instructions.                   |
| **NF3**  | **Clarity & Verifiability**      | Every directive should be objectively testable (no vague terms like “engaging” or “insightful”). | All success criteria measurable via string/regex validation.                    |
| **NF4**  | **Extensibility**                | Template adaptable to new domains by changing only schema and examples.                          | ≥ 80 % of text remains static across use cases.                                 |
| **NF5**  | **Model-Agnostic Compatibility** | Works with any LLM that accepts text prompts; no dependency on vendor-specific syntax.           | Confirmed operational across GPT, Claude, Gemini, Llama, etc.                   |
| **NF6**  | **Schema Stability**             | Field naming conventions remain consistent across versions.                                      | Backward-compatible schema instructions maintained.                             |
| **NF7**  | **Readability**                  | Human reviewers can audit prompts without special tooling.                                       | Uses markdown-style sectioning and PRISM header block.                          |
| **NF8**  | **Safety / Determinism**         | Prevents hallucination or unsafe text reproduction.                                              | Explicitly disallows paraphrasing, copying full text, or generating commentary. |
| **NF9**  | **Composability**                | Compatible with chained or automated workflows (e.g., n8n, Airflow, Prefect).                    | Output cleanly parsable as a string parameter.                                  |
| **NF10** | **Traceability / Versioning**    | Each prompt identifies its version (e.g., v2.43) and change scope.                               | Header always includes `VERSION:` tag; changelog maintained.                    |


## Derived Quality Attributes

Precision: High information fidelity between user request and generated schema.

Determinism: Minimal variability given same input (temperature ≤ 0.2).

Auditability: Humans and scripts can validate structure via regex or JSON schema.

Reusability: Works as a foundation for any extraction domain (finance, retail, media, etc.).

Maintainability: Version upgrades (2.44, 2.45 …) change only framework logic, not the downstream extraction format.