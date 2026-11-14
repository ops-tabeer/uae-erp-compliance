# Chapter 4: VAT

5% since 1 Jan 2018 under Federal Decree-Law 8 of 2017 and its Executive Regulation (Cabinet Decision 52 of 2017),
administered by the FTA through EmaraTax. For a travel company the hard part isn't the rate: it's classifying each
part of a booking.

## What changed in 2026

| Effective | Instrument | Change | Software impact |
|---|---|---|---|
| 1 Jan 2026 | FDL 16 of 2025 (VAT) and 17 of 2025 (Tax Procedures) | No self-issued invoices for reverse-charge imports; they go straight on the return | Remove the self-invoice step from the import workflow |
| 1 Jan 2026 | same | **5-year limit** on claiming refunds and excess input tax; older credits lapse, with a transition window to **1 Jan 2027** | Age VAT credits and alert before expiry |
| 1 Jan 2026 | same | The FTA can refuse input VAT if the buyer knew or should have known the supply was linked to evasion | Supplier due diligence: check TRNs, keep evidence |
| 14 Apr 2026 | Cabinet Decision 129 of 2025 | Late payment becomes a flat **14% a year** (instead of 2% + 4%/month); voluntary-disclosure penalties scale by delay | Recalculate penalty estimates |
| 1 Apr 2026 | Tax Procedures Executive Regulation amendments | Record retention extended by 2 years while a refund claim is pending | Retention engine |

## Registration

Mandatory above AED 375,000 of taxable supplies and imports in the last 12 months, or expected in the next 30 days.
Voluntary above AED 187,500 of supplies or expenses. Late registration costs AED 10,000. Companies under common
control can form a **VAT group** with one TRN, and supplies within the group are ignored. A **TRN is 15 digits**:
validate it on every customer and supplier and store the verification date.

## The four treatments (every line needs exactly one; force a choice)

| Treatment | Rate | Input VAT recoverable? | Travel examples |
|---|---|---|---|
| Standard | 5% | Yes | UAE hotels, desert safaris, local tours, service fees to UAE customers, visa service fees |
| Zero-rated | 0% | Yes | International flights; domestic legs of an international journey by the **same** carrier; qualifying exports of services |
| Exempt | none | No | Local passenger transport, residential rent, some financial services |
| Out of scope | none | n/a | Hotels and services consumed outside the UAE when acting as principal; government fees passed through as disbursements |

Zero-rated and exempt look the same on the invoice but differ for recovery. Never leave the tax blank.

## Travel: agent or principal

- **Agent**: arranges the supply between customer and airline or hotel in the supplier's name. Only the commission or
  service fee is its own supply. The ticket or room price passes through as a disbursement if the customer is liable to
  the supplier, it's passed on at cost and it's shown separately.
- **Principal**: buys hotel, transfers and tours and sells a package in its own name. Each component is its own supply,
  taxed by where it is consumed.

| Component | As agent | As principal |
|---|---|---|
| International air ticket | Fare passes through; service fee to a UAE customer at 5% | Zero-rated |
| Hotel in Dubai | Room passes through; commission at 5% | 5% |
| Hotel abroad (e.g. Turkey) | Room passes through; commission treatment depends on who pays and where they are | Out of scope |
| Desert safari in Dubai | Pass-through; fee at 5% | 5% |
| Visa processing | Government fee as disbursement; service fee at 5% | Service element at 5% |
| Travel insurance | Commission usually exempt (financial service), so confirm | Usually exempt |

Commissions from overseas suppliers may be zero-rated as exports of services under strict conditions. Get written advice
and record the reasoning in the tax-code notes. The zero rate for domestic legs only applies if the same supplier provides
the international leg (PwC on FTA clarification VATP040).

## Tax invoices

Issue within **14 days** of supply. A full tax invoice shows: "Tax Invoice"; the supplier's name, address and TRN; the
customer's name, address and TRN (if registered); a unique sequential number; the issue date (and supply date if
different); a description; per line quantity, unit price, rate and amount in AED; any discount; the total in AED; total
VAT in AED with the exchange rate for foreign currency; and a reverse-charge statement where relevant. A **simplified
invoice** is allowed for unregistered customers, or registered ones at AED 10,000 or less. A **tax credit note** shows
"Tax Credit Note", the parties, the **original invoice reference**, the credit value, the VAT adjusted and a short reason.
From 2027, B2B documents must also be e-invoices (see e-invoicing.md).

## Returns, records, penalties

- Quarterly by default (monthly for some large businesses). Return and payment are due by the **28th day** after period end,
  reporting sales by emirate and treatment, reverse charge, input VAT and adjustments. Errors under AED 10,000 go in the
  next return; larger ones need a voluntary disclosure.
- Records (invoices, credit notes, imports, ledgers, working papers) are kept ≥ **5 years** after the period, longer while
  an audit or dispute is open. They may be electronic, readable in Arabic on request, and producible quickly.

| Failure | Penalty |
|---|---|
| Late registration | AED 10,000 |
| Late payment | 14% a year on unpaid tax, monthly, from 14 Apr 2026 |
| Understatement found by the FTA | 15% of the shortfall + 1% a month (per Stackcue) |
| Voluntary disclosure | Scaled by delay: lower the sooner you correct |
| Missing or wrong tax invoices | Per-document, per Cabinet Decision 40 of 2017 as amended (check the current table) |

## ERP requirements

1. A validated 15-digit TRN on every customer and supplier, with a verification date.
2. A tax-code master: one code per treatment and travel scenario, each with a written reason.
3. Booking lines tagged agent or principal, driving the treatment automatically.
4. Place-of-supply logic (where consumed → UAE, out of scope or zero-rated).
5. Gapless sequential numbering, not editable after posting; corrections only by credit note.
6. Multi-currency invoices with AED totals at the Central Bank rate on the invoice date.
7. A 14-day invoicing check from the supply date, with an exceptions report.
8. A VAT return report by emirate and box, reconciled to the GL.
9. Input VAT ageing, alerting at 4 years ahead of the 5-year limit.
10. Lock dates after each return, so a filed period changes only through voluntary disclosure.

## Odoo 19 notes

`l10n_ae` provides the UAE chart, taxes and VAT report tags. Use explicit 0% taxes for zero-rated, exempt and out-of-scope,
never untaxed lines (`uae_readiness_check.py` U03). Partner TRN goes in `res.partner.vat`. After filing, set the **tax lock
date** (`res.company.tax_lock_date`) (U05). Hash-secure the sales journal and keep the restrictive audit trail on.
