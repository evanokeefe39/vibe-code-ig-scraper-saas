
# High-Level Plan – Minimal Implementation

## 🧭 Goal
Deliver a working prototype where a user:
1. Creates a **run** in the Django frontend.
2. Triggers an **n8n scraping workflow** that saves raw JSON to `core_run.data`.
3. Automatically launches an **extraction workflow** that uses the user’s prompt + LLM to extract/enrich data.
4. Saves results to `core_run.extracted_data`.
5. Allows the user to **“Add to List”**, merging extracted results into `core_list` with optional column-mapping if schemas differ.

---

## 🧱 Core Components

| Component | Purpose |
|------------|----------|
| **Django Frontend** | UI for creating runs, viewing results, and merging to lists. |
| **Postgres DB** | Persists scraped data, extracted results, staging, and lists. |
| **n8n Workflow – Scraping** | Existing workflow that fetches data and populates `core_run.data`. |
| **n8n Workflow – Extraction (new)** | Takes a run ID, loads scraped data, calls LLM extraction, and writes to `core_run.extracted_data`. |
| **Simple Agent (n8n node)** | Wraps a single LLM call for extraction — later evolves into a multi-tool MCP agent. |
| **Staging Table (ephemeral)** | Temporary workspace for intermediate results per run (`staging_run_<id>`). |
| **core_list Table** | Persistent user lists for long-term storage of enriched data. |

---

## ⚙️ Execution Flow

1. **Run Creation (Frontend)**
   - User enters URL/config + extraction prompt.
   - Django creates `core_run` row → triggers **Scraping Workflow**.

2. **Scraping Workflow (n8n)**
   - Collects raw data.
   - Updates `core_run.data`.
   - Calls **Extraction Workflow** webhook.

3. **Extraction Workflow (n8n)**
   - Creates ephemeral `staging_run_<id>` table.
   - Loads `core_run.data` → staging.
   - Runs LLM extraction (simple agent).
   - Writes extracted results back to staging + `core_run.extracted_data`.


4. **Frontend Display**
   - User can view extracted results in Django once status is `complete`.

5. **Add to List**
   - User clicks “Add to List”.
   - Backend compares `core_run.extracted_data` schema with target `core_list.schema`.
   - If mismatch → popup for column addition/mapping.
   - If approved → data appended to `core_list` and schema updated.

---

## 🧩 Scope Simplifications

| Area | Decision |
|-------|----------|
| Prompt validation | Skipped |
| Normalization / mapping | Skipped |
| Translation | Skipped |
| Tool orchestration | Single LLM call |
| Security isolation | Simple staging table per run |
| Schema management | Handled manually via “Add to List” popup |

---

## 🚀 Deliverables

1. **Postgres schema updates**
   - `core_run` (with `data`, `extracted_data`, `status`, `extraction_prompt`)
   - `staging_run_<id>` (ephemeral)
   - `core_list` (persistent list + schema)

2. **New n8n Extraction Workflow JSON**
   - Webhook → Load run → Create staging → LLM call → Save result

3. **Minimal LLM Agent Script**
   - Takes `prompt + data` → returns structured JSON.

4. **Django Endpoint / Frontend**
   - “Create Run” → triggers scraping.
   - “Add to List” → schema compare + merge popup.

---

### Summary

> **Scrape → Extract → Review → Merge**

A lightweight, production-ready loop that proves the data extraction concept and sets the stage for future expansion into agent orchestration, MCP tooling, and automated schema management.
