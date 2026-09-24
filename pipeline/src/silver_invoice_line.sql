-- P2 — Silver: conformed Invoice lines
-- Note: business duplicates (DUP_INVOICE) are PRESERVED here (distinct invoice_id) — they are real
-- exceptions the match must catch. We only drop accidental re-ingestion dupes on the natural key.
CREATE OR REFRESH MATERIALIZED VIEW accord_febar_catalog.silver.invoice_line
  COMMENT 'Silver: conformed, typed invoice lines (business duplicates preserved for the match).'
AS
SELECT
  CAST(invoice_id AS STRING)   AS invoice_id,
  CAST(inv_line_no AS INT)     AS inv_line_no,
  CAST(vendor_id AS STRING)    AS vendor_id,
  CAST(po_id AS STRING)        AS po_id,
  CAST(product_no AS STRING)   AS product_no,
  CAST(qty_billed AS INT)      AS qty_billed,
  CAST(unit_price AS DOUBLE)   AS unit_price,
  UPPER(TRIM(uom))             AS uom,
  CAST(tax AS DOUBLE)          AS tax,
  CAST(remit_to AS STRING)     AS remit_to,
  CAST(invoice_no AS STRING)   AS invoice_no,
  CAST(invoice_date AS DATE)   AS invoice_date
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY invoice_id, inv_line_no ORDER BY _ingested_at DESC) AS _rn
  FROM invoice
)
WHERE _rn = 1;
