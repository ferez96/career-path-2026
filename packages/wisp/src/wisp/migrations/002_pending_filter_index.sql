-- Index for the list_jobs("pending") subquery.
--
-- The pending filter (sqlite_vault.list_jobs filter='pending') runs:
--
--   SELECT j.* FROM jobs j WHERE EXISTS (
--     SELECT 1 FROM evaluations e
--     WHERE e.job_id = j.id AND e.kind = 'composite' AND e.signal = 'pending'
--       AND e.id = (SELECT MAX(e2.id) FROM evaluations e2
--                   WHERE e2.job_id = j.id AND e2.kind = 'composite')
--   ) ...
--
-- The MAX(id) subquery filters on (job_id, kind) — neither
-- idx_evaluations_job_id (job_id) nor idx_evaluations_job_kind_time
-- (job_id, kind, evaluated_at DESC) covers it well, so the optimizer
-- ends up scanning the leftmost prefix and computing MAX in memory.
--
-- (job_id, kind, id) lets SQLite resolve the subquery as a single
-- "last entry on this prefix" lookup. id is the rowid alias, so the
-- index naturally orders by it.

CREATE INDEX IF NOT EXISTS idx_evaluations_job_kind_id
    ON evaluations(job_id, kind, id);
