-- P1 — Bronze: raw Invoice lines
-- Auto Loader ingestion of the JSON `invoice` feed (partitioned by _ym) from the landing volume.
CREATE OR REFRESH STREAMING TABLE invoice
  COMMENT 'Bronze: raw invoice lines ingested from the invoice file feed via Auto Loader.'
AS
SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files(
  '${feeds_root}/invoice',
  format => 'json'
);
