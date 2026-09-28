-- M1 — Feature/label table for the Approve/Hold model.
-- LEAKAGE GUARD: features are raw discrepancy *measurements* from gold; the rule OUTPUTS
-- (reason_code, disposition, amt_at_risk) are deliberately EXCLUDED. Label = line_truth ground
-- truth. vendor_exc_rate is leave-one-out to avoid self-leakage.
CREATE OR REPLACE TABLE accord_febar_catalog.ml.features_labeled AS
WITH base AS (
  SELECT g.invoice_id, g.inv_line_no, g.vendor_id,
    coalesce(g.price_var_pct,0.0)   AS price_var_pct,
    coalesce(g.qty_var,0)           AS qty_var,
    coalesce(g.qty_ordered_var,0)   AS qty_ordered_var,
    coalesce(g.receipt_lag_days,-1) AS receipt_lag_days,
    coalesce(g.days_since_po,-1)    AS days_since_po,
    g.invoice_amount,
    g.dup_count,
    CAST(g.has_po AS INT)           AS has_po,
    CAST(g.has_gr AS INT)           AS has_gr,
    CAST(coalesce(g.inv_remit_to = g.vendor_remit_to, false) AS INT) AS remit_match,
    CAST(coalesce(g.inv_uom = g.po_uom, false) AS INT)              AS uom_match,
    CASE WHEN t.true_disposition = 'HOLD' THEN 1 ELSE 0 END          AS y_hold
  FROM accord_febar_catalog.gold.invoice_match_result g
  JOIN accord_febar_catalog.landing.line_truth t USING (invoice_id, inv_line_no)
),
vend AS (SELECT vendor_id, sum(y_hold) v_holds, count(*) v_total FROM base GROUP BY vendor_id)
SELECT b.*,
  round(CASE WHEN v.v_total > 1 THEN (v.v_holds - b.y_hold) / (v.v_total - 1) ELSE 0.0 END, 4) AS vendor_exc_rate
FROM base b JOIN vend v USING (vendor_id);
