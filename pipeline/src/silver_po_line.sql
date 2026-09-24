-- P2 — Silver: conformed Purchase Order lines
-- Typed + deduped on the natural key. Reads the bronze `po` streaming table as a batch snapshot.
CREATE OR REFRESH MATERIALIZED VIEW accord_febar_catalog.silver.po_line
  COMMENT 'Silver: conformed, typed, deduped PO lines.'
AS
SELECT
  CAST(po_id AS STRING)        AS po_id,
  CAST(po_line_no AS INT)      AS po_line_no,
  CAST(vendor_id AS STRING)    AS vendor_id,
  CAST(product_no AS STRING)   AS product_no,
  CAST(qty_ordered AS INT)     AS qty_ordered,
  CAST(unit_price AS DOUBLE)   AS unit_price,
  UPPER(TRIM(uom))             AS uom,
  CAST(ship_to AS STRING)      AS ship_to,
  CAST(po_date AS DATE)        AS po_date
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY po_id, po_line_no ORDER BY _ingested_at DESC) AS _rn
  FROM po
)
WHERE _rn = 1;
