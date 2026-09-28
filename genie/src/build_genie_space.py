#!/usr/bin/env python3
"""G1 — build the serialized_space payload for the Accord AP 3-Way Match Genie space.

Local helper: emits request.json for `databricks genie create-space --json @request.json`.
Reproducible artifact — re-run to regenerate the payload. Usage:
    python3 build_genie_space.py <warehouse_id> <parent_path> [out_path]
"""
import json, sys

CAT = "accord_febar_catalog"
GOLD = f"{CAT}.gold.invoice_match_result"
VEND = f"{CAT}.silver.vendor_master"
SCORED = f"{CAT}.ml.invoice_scored"

serialized = {
    "version": 2,
    "config": {
        "sample_questions": [
            {"id": "aa000000000000000000000000000001", "question": ["How many invoice lines are on hold for price variance?"]},
            {"id": "aa000000000000000000000000000002", "question": ["Which vendors have the highest exception rate?"]},
            {"id": "aa000000000000000000000000000003", "question": ["What is the total dollars on hold by supplier?"]},
            {"id": "aa000000000000000000000000000004", "question": ["How many invoices were received by month in 2026?"]},
            {"id": "aa000000000000000000000000000005", "question": ["What share of invoice lines were auto-approved vs on hold?"]},
        ]
    },
    "data_sources": {
        "tables": [
            # sorted by identifier: gold, ml, silver
            {"identifier": GOLD, "column_configs": [
                # sorted by column_name
                {"column_name": "amt_at_risk", "description": ["Dollars exposed by the exception on this invoice line; 0 for a clean match."], "synonyms": ["dollars at risk", "exposure", "amount held"]},
                {"column_name": "disposition", "description": ["AUTO_APPROVED = clean 3-way match; HOLD = an exception was found. Manual approve/reject decisions live in the app, not here."], "synonyms": ["status", "held", "on hold", "auto approved"], "enable_entity_matching": True},
                {"column_name": "inv_remit_to", "exclude": True},
                {"column_name": "reason_code", "description": ["Exception type: PRICE_VAR, QTY_OVERBILL, NO_RECEIPT, NO_PO, DUP_INVOICE, VENDOR_MISMATCH, UOM_MISMATCH, or MATCH_OK."], "synonyms": ["exception", "exception reason", "why held", "root cause"], "enable_entity_matching": True},
                {"column_name": "vendor_name", "description": ["Supplier / fragrance house name."], "synonyms": ["supplier", "vendor"], "enable_entity_matching": True},
                {"column_name": "vendor_remit_to", "exclude": True},
            ]},
            {"identifier": SCORED, "column_configs": [
                {"column_name": "hold_probability", "description": ["Model's Approve/Hold confidence (0-1); higher = more likely a genuine exception."], "synonyms": ["confidence", "risk score", "model score"]},
            ]},
            {"identifier": VEND, "column_configs": [
                {"column_name": "payment_terms", "enable_entity_matching": True},
                {"column_name": "remit_to", "exclude": True},
            ]},
        ]
    },
    "instructions": {
        "example_question_sqls": [
            {"id": "bb000000000000000000000000000001",
             "question": ["Total dollars on hold by supplier"],
             "sql": [f"SELECT vendor_name, round(sum(amt_at_risk),2) AS dollars_on_hold, count(*) AS held_lines FROM {GOLD} WHERE disposition = 'HOLD' GROUP BY vendor_name ORDER BY dollars_on_hold DESC"]},
            {"id": "bb000000000000000000000000000002",
             "question": ["Which vendors have the highest exception rate?"],
             "sql": [f"SELECT vendor_name, round(avg(CASE WHEN disposition='HOLD' THEN 1 ELSE 0 END),3) AS exception_rate, count(*) AS lines FROM {GOLD} GROUP BY vendor_name HAVING count(*) > 50 ORDER BY exception_rate DESC LIMIT 10"]},
        ],
        "text_instructions": [
            {"id": "cc000000000000000000000000000001", "content": [
                "## PURPOSE",
                "- Answer accounts-payable three-way-match questions for Maison Lumiere: invoice-line match results, holds, exception reasons, and dollars at risk.",
                "- Audience: AP analysts and finance — assume procure-to-pay fluency.",
                "## DISAMBIGUATION",
                "- 'on hold' / 'held' = disposition = 'HOLD'; 'auto-approved' / 'clean' = disposition = 'AUTO_APPROVED'.",
                "- 'exception' / 'reason' / 'root cause' = reason_code.",
                "- Data covers invoice dates 2025-03 through 2026-08; for 'this year' use year 2026.",
                "## DATA QUALITY NOTES",
                "- gold.invoice_match_result dispositions are only AUTO_APPROVED or HOLD. Manual approve/reject decisions are made in the app and are not in these tables.",
                "- amt_at_risk is 0 for MATCH_OK lines.",
                "## CONSTRAINTS",
                "- Never expose remit-to / bank fields (inv_remit_to, vendor_remit_to, remit_to).",
            ]},
        ],
        "join_specs": [
            {"id": "dd000000000000000000000000000001",
             "left": {"identifier": GOLD, "alias": "invoice_match_result"},
             "right": {"identifier": VEND, "alias": "vendor_master"},
             "sql": ["`invoice_match_result`.`vendor_id` = `vendor_master`.`vendor_id`", "--rt=FROM_RELATIONSHIP_TYPE_MANY_TO_ONE--"]},
            {"id": "dd000000000000000000000000000002",
             "left": {"identifier": GOLD, "alias": "invoice_match_result"},
             "right": {"identifier": SCORED, "alias": "invoice_scored"},
             "sql": ["`invoice_match_result`.`invoice_id` = `invoice_scored`.`invoice_id` AND `invoice_match_result`.`inv_line_no` = `invoice_scored`.`inv_line_no`", "--rt=FROM_RELATIONSHIP_TYPE_ONE_TO_ONE--"]},
        ],
    },
    "benchmarks": {
        "questions": [
            {"id": "ee000000000000000000000000000001", "question": ["How many invoice lines are on hold for price variance?"],
             "answer": [{"format": "SQL", "content": [f"SELECT count(*) AS price_variance_holds FROM {GOLD} WHERE disposition='HOLD' AND reason_code='PRICE_VAR'"]}]},
            {"id": "ee000000000000000000000000000002", "question": ["Which vendors have the highest exception rate?"],
             "answer": [{"format": "SQL", "content": [f"SELECT vendor_name, round(avg(CASE WHEN disposition='HOLD' THEN 1 ELSE 0 END),3) AS exception_rate, count(*) AS lines FROM {GOLD} GROUP BY vendor_name HAVING count(*) > 50 ORDER BY exception_rate DESC LIMIT 10"]}]},
            {"id": "ee000000000000000000000000000003", "question": ["What is the total dollars on hold by supplier?"],
             "answer": [{"format": "SQL", "content": [f"SELECT vendor_name, round(sum(amt_at_risk),2) AS dollars_on_hold FROM {GOLD} WHERE disposition='HOLD' GROUP BY vendor_name ORDER BY dollars_on_hold DESC"]}]},
            {"id": "ee000000000000000000000000000004", "question": ["How many invoices were received by month in 2026?"],
             "answer": [{"format": "SQL", "content": [f"SELECT date_format(invoice_date,'yyyy-MM') AS ym, count(*) AS lines FROM {GOLD} WHERE year(invoice_date)=2026 GROUP BY ym ORDER BY ym"]}]},
            {"id": "ee000000000000000000000000000005", "question": ["What share of invoice lines were auto-approved vs on hold?"],
             "answer": [{"format": "SQL", "content": [f"SELECT disposition, count(*) AS lines, round(100.0*count(*)/sum(count(*)) OVER (),1) AS pct FROM {GOLD} GROUP BY disposition"]}]},
        ]
    },
}

if __name__ == "__main__":
    wid = sys.argv[1] if len(sys.argv) > 1 else "<warehouse_id>"
    parent = sys.argv[2] if len(sys.argv) > 2 else "/Users/me/accord"
    out = sys.argv[3] if len(sys.argv) > 3 else "/tmp/accord_genie_request.json"
    request = {
        "warehouse_id": wid,
        "serialized_space": json.dumps(serialized),
        "title": "Accord — AP 3-Way Match",
        "description": "Ask about invoice-line 3-way match results, holds, exception reasons, and dollars at risk (synthetic Maison Lumiere data).",
        "parent_path": parent,
    }
    with open(out, "w") as f:
        json.dump(request, f)
    print(f"wrote {out}  (serialized_space {len(request['serialized_space'])} chars)")
