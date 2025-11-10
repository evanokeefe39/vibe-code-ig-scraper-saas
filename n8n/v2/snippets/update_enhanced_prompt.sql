-- SQL Query to update enhanced_prompt in core_run table
-- Use this in n8n PostgreSQL Execute Query node
-- Replace {{ $json.enhanced_prompt }} with your enhanced prompt variable
-- Replace {{ $json.run_id }} with your run_id variable

UPDATE core_run 
SET enhanced_prompt = {{ $json.enhanced_prompt }}
WHERE id = {{ $json.run_id }};

-- Alternative with parameterized query (recommended for production):
-- UPDATE core_run 
-- SET enhanced_prompt = $1
-- WHERE id = $2;

-- For use in n8n with parameterized query:
-- Parameters: [$json.enhanced_prompt, $json.run_id]