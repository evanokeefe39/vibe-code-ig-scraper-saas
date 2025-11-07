### Summary of n8n Postgres Writes and Related Enhancements

In n8n, for writing to a Postgres DB (e.g., appending to a JSONB field like `scraped` in an orchestration task row without reading first), use the built-in Postgres node with a custom SQL `UPDATE` query: `SET scraped = scraped || $1::jsonb` for atomic appends. This leverages Postgres' JSONB concatenation operator (`||`), assuming `scraped` is an array for true append-only behavior.

When migrating to Supabase (Postgres-based), stick with the Postgres node for continuity by updating credentials—it's efficient for custom queries. Alternatives include the Supabase node (for SDK/API features, but may require read-append-update flows) or HTTP Request node (for REST API calls, especially to RPC endpoints for stored procs).

To avoid client-side reads in API scenarios, create a stored procedure in Postgres/Supabase:
```sql
CREATE OR REPLACE FUNCTION append_scraped(task_id int, new_data jsonb) RETURNS void AS $$
UPDATE your_table SET scraped = scraped || new_data WHERE id = task_id;
$$ LANGUAGE sql;
```
This runs server-side atomically. Call it via SQL or Supabase's `/rpc` endpoint.

For Django apps, manage this proc via migrations: Use `migrations.RunSQL` in a custom migration file to execute the `CREATE` SQL (with optional `reverse_sql` for drops). This keeps it version-controlled.

Overall, this enhances efficiency, atomicity, and avoids race conditions in concurrent writes, with minimal workflow changes during migration.