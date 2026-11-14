---
name: uae-erp-compliance
description: UAE legal compliance for ERP, HR and payroll software (Odoo first). Covers the PDPL data protection law (FDL 45/2021) and its status, the Labour Law (FDL 33/2021) including leave, overtime, end-of-service gratuity and the 14-day final settlement, WPS under Ministerial Resolution 340 of 2026 (salaries by the 1st, 85% threshold, SIF salary files), VAT (5%, TRN, travel agent vs principal, tax invoices, 28-day returns, 5-year credit limit, 2026 penalties), Corporate Tax (9%, Small Business Relief, related parties, 7-year records), and e-invoicing (Peppol PINT AE, ASPs, 1 Jan 2027 / 1 Jul 2027 go-live, Cabinet Decision 173 of 2026 penalties). Use it whenever someone asks what UAE law requires of a system, wants to build or check a WPS file, calculate gratuity or a final settlement, set up VAT tax codes for travel bookings, prepare Odoo for UAE e-invoicing, check TRN or Peppol readiness, or plan a UAE compliance roadmap, even if they only mention one term like "WPS", "SIF", "gratuity", "TRN" or "PINT".
---

# UAE compliance for ERP, HR and payroll

Built from a *UAE Compliance Handbook for ERP, HR and Payroll Software* (14 Nov 2026), checked against
public sources and the Odoo 19 source. It serves two readers. **Builders** need the features each law requires.
**Operators** (e.g. a UAE travel company) need their obligations in plain terms. Ask which one the user is if it isn't clear.

## How to answer

1. **Identify the regime(s)** and read only the matching reference:

   | Topic | Read |
   |---|---|
   | Personal data, consent, passports, breaches, cross-border | `references/pdpl.md` |
   | Contracts, probation, leave, overtime, gratuity, settlement, Emiratisation, ILOE | `references/labour-law.md` |
   | Salary payment deadline, 85% rule, SIF file, rejections | `references/wps.md` |
   | VAT treatment, TRN, tax invoices, returns, travel agent/principal | `references/vat.md` |
   | Corporate Tax, Small Business Relief, related parties, thresholds | `references/corporate-tax.md` |
   | E-invoicing, Peppol, PINT AE, ASP, timeline, penalties | `references/e-invoicing.md` |
   | Roadmap, cross-regime requirements, deadline calendar | `references/requirements-matrix.md` |

2. **Check the status.** `references/status-and-sources.md` records what was independently confirmed and what comes
   only from the handbook (for example the e-invoicing AED 50,000 cap, the 14-business-day rule, the WPS escalation
   days). Say which is which. Several 2026 instruments are new and still moving.
3. **Make it concrete.** Use the tools rather than doing the arithmetic or checks by hand, because they encode the
   edge cases:
   - `scripts/gratuity.py --basic 6000 --start 2019-01-01 --end 2026-03-31 [--unpaid-days N] [--scheme-days N] [--leave-days N] [--deductions X]`:
     gratuity (21/30 days, unpaid-leave exclusion, 24-month cap, Savings Scheme) and the final-settlement total with its 14-day pay-by date.
   - `scripts/wps_sif.py build|validate|self-test`: builds or validates a SIF (IBAN check digits, routing codes,
     14/13-digit ids, dates, totals to the fils, record count, file name) and gives the WPS due date.
   - `scripts/uae_readiness_check.py --db <db> --out <dir>`: a read-only Odoo check of UAE companies:
     - U01 modules (l10n_ae, Peppol, PINT AE availability)
     - U02 TRN and Peppol IDs on partners
     - U03 untaxed invoice lines and orphan credit notes
     - U04 revenue against the 375k/3m/50m/200m thresholds
     - U05 VAT tax lock dates
     - U06 employee WPS data (IBAN, Emirates ID, permits, expiries)
     - U07 audit trail and retention
4. **Map to Odoo.** Each reference ends with Odoo 19 notes (fields, modules, settings). Key facts:
   - Partner TRN is in `res.partner.vat`, and the Peppol ID is `peppol_eas = 0235` plus `peppol_endpoint` = first 10 digits of the TRN.
   - Odoo 19.0 core has **no UAE PINT module**, so plan a custom generator or the ASP connector.
   - Emirates ID is `hr.version.identification_id`.
   - Employee bank accounts are `hr.employee.bank_account_ids`.
   - Lock filed VAT periods with `tax_lock_date`.
5. **Say what it is not.** End compliance answers with a line saying it isn't legal or tax advice. The user should
   confirm against MoF, FTA or MOHRE texts or a licensed adviser, especially for penalties and dates. Never quote PDPL fines as fact.

## Rules that cross every regime

- One clean partner record (TRN/TIN, Peppol ID, related-party flag, consent) serves VAT, CT, e-invoicing and PDPL.
- **Retain 7 years** by default (CT 7, VAT 5 plus 2 while a refund is pending, labour claims 2 years after exit).
  Anonymise personal data instead of deleting financial records. A legal hold beats an erasure request.
- Lock periods after filing; correct by credit note or adjustment only.
- Segregation of duties: preparer ≠ approver, and whoever edits bank details can't release payments. An IBAN change needs a second approval.
- Deadlines:
  - WPS on the 1st
  - VAT return on the 28th
  - tax invoice within 14 days
  - e-invoice within 14 business days
  - final settlement within 14 days
  - CT return at 9 months
- Never hard-code account codes. Use account types or per-company settings.

## Related skills

For fraud investigation use `erp-fraud-forensics`. For control design and the money-moving-module guardrails use
`erp-controls-compliance`. For security, 2FA and server hardening use `erp-security-hardening`.
