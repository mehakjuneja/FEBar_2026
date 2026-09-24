-- P2 — Silver: conformed Goods Receipt lines
CREATE OR REFRESH MATERIALIZED VIEW accord_febar_catalog.silver.gr_line
  COMMENT 'Silver: conformed, typed, deduped goods-receipt lines.'
AS
SELECT
  CAST(gr_id AS STRING)        AS gr_id,
  CAST(gr_line_no AS INT)      AS gr_line_no,
  CAST(po_id AS STRING)        AS po_id,
  CAST(product_no AS STRING)   AS product_no,
  CAST(qty_received AS INT)    AS qty_received,
  UPPER(TRIM(condition))       AS condition,
  CAST(receipt_date AS DATE)   AS receipt_date
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY gr_id, gr_line_no ORDER BY _ingested_at DESC) AS _rn
  FROM gr
)
WHERE _rn = 1;
