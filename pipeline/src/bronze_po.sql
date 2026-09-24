-- P1 — Bronze: raw Purchase Order lines
-- Auto Loader ingestion of the CSV `po` feed (partitioned by _ym) from the landing volume.
-- Raw layer: ingest as-landed + provenance columns; typing/dedup happen in silver (P2).
CREATE OR REFRESH STREAMING TABLE po
  COMMENT 'Bronze: raw PO lines ingested from the po file feed via Auto Loader.'
AS
SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files(
  '${feeds_root}/po',
  format      => 'csv',
  header      => 'true',
  inferSchema => 'true'
);
