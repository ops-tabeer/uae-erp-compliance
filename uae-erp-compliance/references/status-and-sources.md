# Status, verification notes and sources

Source: a *UAE Compliance Handbook for ERP, HR and Payroll Software* (14 Nov 2026),
reflecting public sources as of that date. It is a planning summary, **not legal or tax advice**. Confirm each
rule against the official Ministry of Finance, FTA and MOHRE texts, or with a licensed adviser, before relying on it.

## Regimes at a glance

| Chapter | Regime | Main law | Regulator | Most urgent date |
|---|---|---|---|---|
| 1 | Personal data protection | Federal Decree-Law 45 of 2021 (PDPL) | UAE Data Office → Federal Authority for AI and Data | Executive Regulations still awaited; 6 months to comply once issued |
| 2 | Labour Law | Federal Decree-Law 33 of 2021 (amended by 20/2023 and 9/2024); Cabinet Resolution 1 of 2022 | MOHRE | Emiratisation 10% by 31 Dec 2026 (50+ staff) |
| 3 | Wage Protection System | Ministerial Resolution 340 of 2026 (replaced 598 of 2022), effective 1 Jun 2026 | MOHRE and the Central Bank | Salaries due on the 1st of every month |
| 4 | VAT | Federal Decree-Law 8 of 2017, amended by 16 of 2025; Tax Procedures 17 of 2025 | FTA | VAT credits from 2021 lapse in 2026; transition window ends 1 Jan 2027 |
| 5 | Corporate Tax | Federal Decree-Law 47 of 2022 | FTA | Return 9 months after year end |
| 6 | E-invoicing | Ministerial Decisions 243 and 244 of 2025 as amended (incl. 64/2025, 66/2026, 197/2026) | MoF and FTA | Go-live 1 Jan 2027 (AED 50m+), 1 Jul 2027 (others); others appoint an ASP by 31 Mar 2027 |

## Independent checks made when this skill was built (14 Nov 2026)

| Claim | Result |
|---|---|
| WPS Resolution 340 of 2026: wages due on the 1st, compliance threshold 80% → 85%, effective 1 Jun 2026 | **Confirmed** (Clyde & Co, Morgan Lewis, Deloitte, u.ae). Secondary sources **disagree on the escalation days** (some say penalties start day 2, some cite a 10-day grace, some day 21 for travel bans). Check the resolution text before hard-coding escalation steps. |
| E-invoicing penalties replaced in October 2026 | **Confirmed**: the instrument is **Cabinet Decision 173 of 2026** (MoF announcement 30 Oct 2026), replacing Cabinet Decision 106 of 2025, with no penalty for failing to report system failures and no double penalty for the same person as issuer and recipient. The handbook's **AED 50,000 / 12-month cap** was **not independently confirmed**. Check the decision text. |
| Ministerial Decision 197 of 2026 (in force 1 Oct 2026): tax-group exclusion until 31 Dec 2028, storage anywhere, failure-notice rule removed | **Confirmed** (Crowe, Fiscal Requirements, MoF). The **14-business-day issue rule** comes from the handbook and wasn't found in the search results, so confirm it before quoting. |
| E-invoicing phases (1 Jul 2026 pilot, 1 Jan 2027 AED 50m+, 1 Jul 2027 others, 1 Oct 2027 government) | Confirmed earlier (KPMG, Gulf News, Grant Thornton) |
| PDPL Executive Regulations not issued as of mid/late 2026; new Federal Authority for AI and Data announced June 2026 | Confirmed (BusinessDubai Aug 2026, Morgan Lewis June 2026) |
| Odoo 19 support | `l10n_ae` and `account_edi_ubl_cii` exist, and the partner Peppol EAS list includes **0235 (UAE TIN)**. `account_peppol` exists. **There is no UAE PINT format module** in Odoo 19.0 core (PINT exists for SG, MY, JP and ANZ only), so plan a custom generator or the ASP's connector. |

When you answer a user, say which items are confirmed and which come from the handbook alone.

## Handbook sources (as listed, 14 Nov 2026)

Morgan Lewis (Federal Authority for AI and Data, Jun 2026); Recording Law (UAE data privacy laws);
BusinessDubai (Is the PDPL enforceable yet?, Aug 2026); BCL (UAE Labour Law 2026; Small Business Relief extended
to 2029); FMC Group (UAE Labor Law News 2026); Gulf News (gratuity and the 14-day rule; salary rule changes from
1 June; UAE eases e-invoicing rules and revises fines, Oct 2026); Clyde & Co (stricter WPS enforcement, Jun 2026);
DLA Piper (stricter salary payment rules, May 2026; VAT amendments effective 1 Jan 2026); Zoho Payroll (WPS SIF
format); PwC (Tax Procedures, VAT and Excise updates; public clarification VATP040); Al Tamimi (tax penalty reform
effective 14 Apr 2026); Alvarez & Marsal via Mondaq (Cabinet Decision 129 of 2025); Stackcue (VAT penalties);
Mazeed (Corporate Tax penalties 2026); KPMG (UAE e-invoicing framework, Oct 2025); Fiscal Requirements (e-invoicing
legal framework, MD 197 of 2026); Lookuptax (ASP deadline moved to 30 Oct 2026); Khaleej Times (ASP outsourcing, May 2026).

Additional sources checked for this skill: WAM / MoF announcement of updated administrative penalties
(Oct 2026); Crowe UAE on Ministerial Decision 197 of 2026; Deloitte and u.ae on WPS from 1 June 2026.
