-- P1 — Bronze: raw Goods Receipt lines
-- Auto Loader ingestion of the CSV `gr` feed (partitioned by _ym) from the landing volume.
CREATE OR REFRESH STREAMING TABLE gr
  COMMENT 'Bronze: raw goods-receipt lines ingested from the gr file feed via Auto Loader.'
AS
SELECT
  *,
  _metadata.file_path AS _source_file,
  current_timestamp() AS _ingested_at
FROM STREAM read_files(
  '${feeds_root}/gr',
  format      => 'csv',
  header      => 'true',
  inferSchema => 'true'
);
