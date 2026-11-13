# Chapter 5: Corporate Tax

Applies to financial years starting on or after 1 Jun 2023 (Federal Decree-Law 47 of 2022). The first full filing season
for calendar-year companies ended 30 Sep 2025, and the second (2025 accounts) on 30 Sep 2026. The return starts from
audited-quality financial statements and then adjusts them, so it asks more of the ERP than VAT does.

## Rates

| Who | Rate |
|---|---|
| Taxable profit up to AED 375,000 | 0% |
| Above AED 375,000 | 9% |
| Qualifying Free Zone Person, on qualifying income | 0% (other income 9%) |
| Large multinationals (consolidated revenue ≥ EUR 750m) | Domestic Minimum Top-up Tax to 15% from 1 Jan 2025 |
| Small Business Relief election | Taxable income treated as nil |

## Registration and filing

- Every UAE company and free-zone entity registers, whether or not tax is owed. Individuals register above AED 1m business turnover.
- Late registration AED 10,000, waived if the first return is filed within **7 months** of the first period end (usually 9).
- Return and payment are due **9 months** after year end via EmaraTax (30 Sep for a December year end).
- Late filing AED 500/month for the first 12 months, then AED 1,000/month. Late payment 14% a year, monthly, from 14 Apr 2026.

## Small Business Relief

Resident businesses with revenue ≤ **AED 3m** in the current **and every previous** period can elect nil taxable income
(revenue includes exempt income). It was due to end with periods ending 31 Dec 2026, and advisers report an **extension
to 31 Dec 2029**: confirm the decision text. It must be elected in each return. QFZPs and large MNE members can't use it.
Splitting a business to stay under AED 3m is artificial separation and is penalised. Losses can't be used or carried
forward in relief years. Related-party prices must still be at arm's length (no TP file needed). Track revenue against
AED 3m per company and warn early: crossing it once ends the relief for good.

## Accounting profit to taxable profit (IFRS / IFRS for SMEs, then adjustments)

| Adjustment | Rule | ERP design |
|---|---|---|
| Client entertainment | 50% deductible | Separate expense account |
| Fines and penalties | Not deductible | Separate account |
| Donations | Deductible only to approved charities | Tag the recipient |
| Interest | Net interest above AED 12m capped at 30% of adjusted EBITDA | Interest accounts by type |
| Related-party transactions | Arm's length | Related-party / connected-person flag on partners |
| Payments to owners and directors | At market value to be deductible | Connected-person tagging |
| Unrealised gains and losses | Election to tax on realisation | Revaluation journals kept separate |
| Tax losses | Carried forward; offset up to 75% of a later year's profit | Loss register by year |

## Groups and related parties

- **Tax group**: resident companies with 95% common ownership and the same financial year file one return, and intra-group transactions are eliminated.
- **Transfer pricing** (without a tax group): every intercompany charge at arm's length (shared staff, office, booking
  engines, management fees). Related-party transactions are disclosed with the return. A **master and local file** is
  needed where company revenue is ≥ AED 200m or group revenue ≥ AED 3.15bn.
- In multi-company Odoo: generate intercompany invoices automatically, priced from a documented policy, and matched in both companies' books.

## Audit and records

Audited statements are needed above AED 50m revenue and for all QFZPs. Corporate Tax records are kept **7 years** after the
period (longer than VAT's 5), so **default retention for all accounting records to 7 years**.

## ERP requirements

1. A chart of accounts built for tax: separate accounts for entertainment, fines, donations, interest and related-party items.
2. Partner tags for related parties and connected persons, with a transactions report.
3. An intercompany module: mirror invoices, an elimination report, and a pricing-policy reference.
4. Revenue tracking against AED 3m (SBR), 50m (audit, e-invoicing wave) and 200m (TP file) per company (`uae_readiness_check.py` U04).
5. A tax computation worksheet from accounting to taxable profit, each adjustment linked to its ledger source.
6. A loss register and deadline calendar (7-month waiver window, 9-month filing, audit sign-off).
7. 7-year retention and a period lock after filing.

Identify these accounts by account type or a per-company setting, never by hard-coded code (charts differ per company).
