# Chapter 6: E-invoicing

From **1 Jan 2027** businesses with annual revenue ≥ **AED 50m** must issue and receive B2B invoices as structured files
over **Peppol**. Everyone else follows on **1 Jul 2027**. A PDF emailed to a business customer no longer counts as an invoice.

## Instruments

| Instrument | What it does |
|---|---|
| Ministerial Decision 243 of 2025 | The system: scope, exclusions, obligations to issue, receive, store, report |
| Ministerial Decision 244 of 2025 | Pilot, voluntary and mandatory phases |
| Ministerial Decision 64 of 2025 | Accreditation of service providers (ASPs) |
| UAE E-Invoicing Guidelines v1.0 + mandatory fields list | Technical guidance (23 Feb 2026) |
| Ministerial Decision 66 of 2026 | Large-business ASP deadline moved 31 Jul → **30 Oct 2026** |
| Ministerial Decision 197 of 2026 (in force 1 Oct 2026) | Tax-group exemption, storage anywhere, failure-notice rule removed; per the handbook, a 14-business-day issue rule (confirm) |
| **Cabinet Decision 173 of 2026** (announced 30 Oct 2026) | Replaces Cabinet Decision 106 of 2025 with lighter penalties |

## Scope

Every business transaction by anyone doing business in the UAE, VAT-registered or not: B2B, B2G and G2B, including exempt
and zero-rated supplies.

**Excluded**: B2C (until a later decision); certain international air transport by qualifying airlines; specified exempt
financial services; sovereign government activities; import reverse charge; and transactions between members of the same
VAT group from 1 Jan 2027 to 31 Dec 2028.

The airline exclusion covers the airline's own invoices only. **A travel agency's invoice to a corporate client for flights
and fees is B2B and in scope.** Corporate travel is the main workload; walk-in leisure customers stay on ordinary tax invoices for now.

## The five-corner model

Supplier ERP → supplier's ASP (validates) → Peppol → buyer's ASP → buyer's ERP, with both ASPs reporting tax data to the
FTA (the fifth corner) close to real time. The supplier never sends straight to the buyer. Each business appoints **one**
ASP from the FTA list. Since May 2026, accredited UAE ASPs may outsource technical work or white-label foreign Peppol platforms.

## Timeline

| Step | Large (≥ AED 50m) | Others |
|---|---|---|
| Pilot / voluntary | from 1 Jul 2026 | from 1 Jul 2026 |
| Appoint an ASP | was due 30 Oct 2026 (passed) | **by 31 Mar 2027** |
| Clean master data (TRNs, Peppol IDs, addresses) | now | by Mar 2027 |
| Map tax codes to PINT AE | now | by Apr 2027 |
| Build and test ERP-ASP integration | Nov-Dec 2026 | Apr-May 2027 |
| Parallel run | Dec 2026 | Jun 2027 |
| **Go live** | **1 Jan 2027** | **1 Jul 2027** |
| Government entities | 1 Oct 2027 | |

## PINT AE data

The UAE version of Peppol PINT, in XML. The FTA specification lists **51 mandatory fields** plus conditional ones
(identifiers, invoice details, totals, VAT breakdown, lines).
- **Identifiers**: Peppol ID = `0235:` + the **first 10 digits of the TRN**. Each VAT-group member uses its own. No TRN → get a TIN first.
- **Currency**: any, but amounts must also appear in AED at the Central Bank rate. Round to 2 decimals at invoice level.
- **Lines**: unlimited, and mixed rates are allowed if each line has the right tax code. Item classification codes are optional now, expected to become mandatory.
- **Timing**: e-invoices and e-credit notes issued and transmitted within **14 business days** of the transaction (per the handbook, citing MD 197/2026: confirm).
- **Unready or non-resident buyers**: still send over Peppol using predefined endpoints. A readable PDF may be attached.
- **Credit notes**: partial credits are allowed, and one credit note can reference several invoices. Advance and milestone invoices must be e-invoices, with adjustments by e-credit note.

## Storage and failures

MD 197/2026 removed the in-UAE storage rule: records may be held anywhere if kept for the Tax Procedures period, intact, and
producible promptly. The 2-business-day system-failure notice was repealed, but a recovery plan is still needed to meet deadlines.

## Penalties (Cabinet Decision 173 of 2026, replacing 106 of 2025)

Per the handbook (Gulf News, Oct 2026): AED 5,000 for an initial failure to implement (issuers and recipients); AED 5,000 per
further month or part month; a cap of AED 50,000 in any 12 consecutive months (not independently confirmed); no penalty for
not reporting a system failure; one penalty when the same person breaches as issuer and recipient. Check the published text,
including any per-invoice penalties, on the MoF site.

## ERP architecture

1. **Master data first**: validate the TRN or TIN and Peppol ID on every partner. Most go-live failures are bad master data, not bad XML.
2. **Tax engine**: map each tax code to its PINT AE tax category and exemption reason code.
3. **Document generator**: build PINT AE XML from posted invoices and credit notes, validated against the FTA schema before sending.
4. **ASP connector**: an ASP-neutral API adapter that sends documents, receives statuses (accepted, rejected, delivered) and writes them back on the invoice.
5. **Inbound**: receive supplier e-invoices, create draft bills, and match them to purchase orders.
6. **Exceptions dashboard**: not sent, rejected, or past the 14-business-day window.
7. **Tax-group flag**: exclude intra-group invoices until 31 Dec 2028, then switch on.
8. **B2C switch**: keep B2C on ordinary invoices, but design so it can be turned on later.
9. **Archive**: XML, ASP acknowledgement and PDF view for the retention period, with integrity hashes.

## Odoo 19 notes

- `account_edi_ubl_cii` is installed with `l10n_ae`. `res.partner.peppol_eas` already offers **0235 (UAE TIN)**, and `peppol_endpoint` holds the 10-digit id.
- `account_peppol` exists (Odoo's own Peppol access point), but **Odoo 19.0 core has no UAE PINT format module** (only SG, MY, JP and ANZ). Options: a custom `l10n_ae_ubl_pint`-style module extending the PINT base, an ASP-provided connector, or a later Odoo release.
- Credit notes must reference the original invoice (`reversed_entry_id`), so create them by reversal (U03).
- Readiness: `uae_readiness_check.py` U01-U03.
