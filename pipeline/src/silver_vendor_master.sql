-- P2 — Silver: governed vendor master (reference data, conformed + normalized)
-- Sourced from the landing reference table. `vendor_name_norm` is the normalized key the match uses;
-- `remit_to` is the sensitive bank-like field flagged for a UC column mask (Product-domain story).
CREATE OR REFRESH MATERIALIZED VIEW accord_febar_catalog.silver.vendor_master
  COMMENT 'Silver: conformed vendor master. remit_to is the future UC column-mask target.'
AS
SELECT
  CAST(vendor_id AS STRING)                        AS vendor_id,
  CAST(vendor_name AS STRING)                      AS vendor_name,
  UPPER(TRIM(regexp_replace(vendor_name, '[^A-Za-z0-9 ]', ''))) AS vendor_name_norm,
  CAST(address AS STRING)                          AS address,
  LOWER(TRIM(email))                               AS email,
  CAST(remit_to AS STRING)                         AS remit_to,
  UPPER(TRIM(payment_terms))                       AS payment_terms
FROM accord_febar_catalog.landing.vendor_master;
