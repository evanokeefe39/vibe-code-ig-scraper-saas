
# High-Level Plan – Minimal Implementation

## 🧭 Goal
Deliver a working prototype where a user:
1. Creates a **run** in the Django frontend.
2. Triggers an **n8n scraping workflow** that saves raw JSON to `core_run.scraped`.
3. Automatically launches an **extraction workflow** that uses the user’s prompt + LLM to extract/enrich data.
4. Saves results to `core_run.extracted`.
5. Allows the user to **“Add to List”**, merging extracted results into `core_list` with optional column-mapping if schemas differ.

---

## 🧱 Core Components

| Component | Purpose |
|------------|----------|
| **Django Frontend** | UI for creating runs, viewing results, and merging to lists. |
| **Postgres DB** | Persists scraped data, extracted results, staging, and lists. |
| **n8n Workflow – Scraping** | Existing workflow that fetches data and populates `core_run.scraped`. |
| **n8n Workflow – Extraction (new)** | Takes a run ID, loads scraped data, calls LLM extraction, and writes to `core_run.extracted`. |
| **Simple Agent (Python/n8n node)** | Wraps a single LLM call for extraction — later evolves into a multi-tool MCP agent. |
| **Staging JSON (ephemeral)** | Temporary workspace for intermediate results per run (in-memory JSON). |
| **UserList + ListColumn + ListRow** | Persistent user lists for long-term storage of enriched data. |

---

## ⚙️ Execution Flow

1. **Run Creation (Frontend)**
   - User enters URL/config + extraction prompt.
   - Django creates `core_run` row → triggers **Scraping Workflow**.

2. **Scraping Workflow (n8n)**
   - Collects raw data.
   - Updates `core_run.scraped`.
   - Calls **Extraction Workflow** webhook (status tracked in n8n).

3. **Extraction Workflow (n8n)**
   - Creates ephemeral staging JSON.
   - Loads `core_run.scraped` → staging.
   - Runs LLM extraction (simple agent).
   - Writes extracted results back to staging + `core_run.extracted`.
   - Status tracked in n8n.

4. **Frontend Display**
   - User can view extracted results in Django once n8n execution is complete.

5. **Add to List**
   - User clicks "Add to List".
   - Backend compares `core_run.extracted` schema with target `UserList` columns.
   - If mismatch → popup for column addition/mapping.
   - If approved → data appended to `UserList` and columns updated.

---

## 🧩 Scope Simplifications

| Area | Decision |
|-------|----------|
| Prompt validation | Skipped |
| Normalization / mapping | Skipped |
| Translation | Skipped |
| Tool orchestration | Single LLM call |
| Security isolation | Simple staging JSON per run |
| Schema management | Handled manually via “Add to List” popup |

---

## 🚀 Deliverables

1. **Postgres schema updates**
   - `core_run` (already has `scraped`, `extracted`, `enable_extraction`, `input` with prompt)
   - No staging tables needed (use JSON)
   - `UserList` with `ListColumn` + `ListRow` (already exists)

2. **New n8n Extraction Workflow JSON**
   - Webhook → Load run → Create staging JSON → LLM call → Save result

3. **Minimal LLM Agent Script**
   - Takes `extraction_prompt + scraped data` → returns structured JSON.

4. **Django Endpoint / Frontend**
   - “Create Run” → triggers scraping.
   - “Add to List” → schema compare + merge popup.

---

### Summary

> **Scrape → Extract → Review → Merge**

A lightweight, production-ready loop that proves the data extraction concept and sets the stage for future expansion into agent orchestration, MCP tooling, and automated schema management.
