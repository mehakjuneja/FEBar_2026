-- P3 — Gold: the three-way match (the heart of Accord)
-- One row per invoice line. Joins invoice -> PO -> GR (+ vendor master), applies the governed
-- match_config tolerances, assigns a disposition + reason_code (severity precedence), computes
-- amt_at_risk and the ML-ready discrepancy features. Reads silver as a batch snapshot.
CREATE OR REFRESH MATERIALIZED VIEW accord_febar_catalog.gold.invoice_match_result
  COMMENT 'Gold: per-invoice-line 3-way match result — disposition, reason_code, amt_at_risk, features.'
AS
WITH cfg AS (
  SELECT price_tol, qty_tol, immaterial_amt
  FROM accord_febar_catalog.silver.match_config WHERE config_key = 'default'
),
-- Pre-aggregate PO and GR to one row per (po_id, product_no) to avoid join fan-out.
po_agg AS (
  SELECT po_id, product_no,
         SUM(qty_ordered)  AS qty_ordered,
         AVG(unit_price)   AS po_unit_price,
         MIN(uom)          AS po_uom,
         MIN(po_date)      AS po_date
  FROM accord_febar_catalog.silver.po_line
  GROUP BY po_id, product_no
),
gr_agg AS (
  SELECT po_id, product_no,
         SUM(qty_received) AS qty_received,
         MIN(receipt_date) AS receipt_date,
         COUNT(*)          AS gr_count
  FROM accord_febar_catalog.silver.gr_line
  GROUP BY po_id, product_no
),
inv AS (
  SELECT *,
         COUNT(*) OVER (PARTITION BY vendor_id, invoice_no, product_no, qty_billed, unit_price) AS dup_count
  FROM accord_febar_catalog.silver.invoice_line
),
joined AS (
  SELECT
    i.invoice_id, i.inv_line_no, i.vendor_id, v.vendor_name,
    i.po_id, i.product_no, i.invoice_no, i.invoice_date,
    i.qty_billed, i.unit_price AS inv_unit_price, i.uom AS inv_uom, i.tax,
    i.remit_to AS inv_remit_to, v.remit_to AS vendor_remit_to,
    p.qty_ordered, p.po_unit_price, p.po_uom, p.po_date,
    g.qty_received, g.receipt_date,
    i.dup_count,
    (p.po_id IS NOT NULL)      AS has_po,
    (g.qty_received IS NOT NULL) AS has_gr,
    c.price_tol, c.qty_tol, c.immaterial_amt
  FROM inv i
  CROSS JOIN cfg c
  LEFT JOIN po_agg p ON i.po_id = p.po_id AND i.product_no = p.product_no
  LEFT JOIN gr_agg g ON i.po_id = g.po_id AND i.product_no = g.product_no
  LEFT JOIN accord_febar_catalog.silver.vendor_master v ON i.vendor_id = v.vendor_id
),
scored AS (
  SELECT *,
    CASE
      WHEN NOT has_po THEN 'NO_PO'
      WHEN dup_count > 1 THEN 'DUP_INVOICE'
      WHEN NOT has_gr THEN 'NO_RECEIPT'
      WHEN qty_billed > qty_received + qty_tol THEN 'QTY_OVERBILL'
      WHEN po_unit_price > 0
           AND abs(inv_unit_price - po_unit_price) / po_unit_price > price_tol
           AND abs(inv_unit_price - po_unit_price) * qty_billed > immaterial_amt THEN 'PRICE_VAR'
      WHEN inv_remit_to <> vendor_remit_to THEN 'VENDOR_MISMATCH'
      WHEN inv_uom <> po_uom THEN 'UOM_MISMATCH'
      ELSE 'MATCH_OK'
    END AS reason_code
  FROM joined
)
SELECT
  invoice_id, inv_line_no, vendor_id, vendor_name, po_id, product_no, invoice_no,
  invoice_date, po_date, receipt_date,
  qty_ordered, qty_received, qty_billed,
  po_unit_price, inv_unit_price, po_uom, inv_uom,
  inv_remit_to, vendor_remit_to, has_po, has_gr, dup_count,
  reason_code,
  CASE WHEN reason_code = 'MATCH_OK' THEN 'AUTO_APPROVED' ELSE 'HOLD' END AS disposition,
  -- dollars exposed by the exception
  round(CASE reason_code
    WHEN 'PRICE_VAR'    THEN (inv_unit_price - po_unit_price) * qty_billed
    WHEN 'QTY_OVERBILL' THEN (qty_billed - qty_received) * inv_unit_price
    WHEN 'MATCH_OK'     THEN 0.0
    ELSE inv_unit_price * qty_billed        -- NO_PO / NO_RECEIPT / DUP / VENDOR / UOM: whole line
  END, 2) AS amt_at_risk,
  -- ML-ready features (Phase 2 reads these; vendor exception-history is derived in M1 to avoid leakage)
  round(CASE WHEN po_unit_price > 0 THEN abs(inv_unit_price - po_unit_price) / po_unit_price END, 4) AS price_var_pct,
  (qty_billed - qty_received)                       AS qty_var,
  (qty_billed - qty_ordered)                        AS qty_ordered_var,
  datediff(receipt_date, po_date)                   AS receipt_lag_days,
  datediff(invoice_date, po_date)                   AS days_since_po,
  round(inv_unit_price * qty_billed, 2)             AS invoice_amount
FROM scored;
