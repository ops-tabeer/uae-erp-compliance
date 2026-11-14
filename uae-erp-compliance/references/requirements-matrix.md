# Chapter 7: Shared foundations, requirements matrix and roadmap

The regimes overlap. A clean partner record (TRN, Peppol ID, related-party flag, consent) serves VAT, Corporate Tax,
e-invoicing and PDPL at once, and so does one retention and audit-trail design. Build the foundations once.

## In one page: what the software must do

1. Issue B2B invoices as PINT AE e-invoices through an accredited provider, within 14 business days.
2. Pay salaries through WPS by the 1st of each month, with a SIF the bank won't reject.
3. Calculate leave, overtime, gratuity and final settlement as the Labour Law sets them.
4. Apply the right VAT treatment to every line, including travel agent and principal cases.
5. Keep the accounts ready for Corporate Tax: related parties, non-deductible items, thresholds.
6. Protect personal data: classify, mask, log, honour rights, handle breaches.
7. Keep an unchangeable audit trail, and keep records for 7 years.

## Shared foundations

| Foundation | Serves | Rule |
|---|---|---|
| Audit trail | All | Log who created, changed, approved, viewed or exported each record, and when; logs can't be edited |
| Retention engine | All | CT 7 years, VAT 5 years (+2 while a refund claim is pending), labour claims 2 years after exit; a legal hold beats an erasure request |
| Period locking | VAT, CT, e-invoicing | No edits after a return is filed; corrections by credit note or adjustment |
| Segregation of duties | Payroll, payments, invoicing | Whoever prepares can't approve; whoever edits bank details can't release payments |
| Partner master data | VAT, CT, e-invoicing, PDPL | Validated TRN or TIN, Peppol ID, related-party flag, consent records |
| Role-based access with field masking | PDPL, HR | Sensitive fields masked by default, every view logged |
| Deadline calendar | All | WPS on the 1st; VAT on the 28th; final settlement in 14 days; e-invoice in 14 business days; tax invoice in 14 days; CT at 9 months |

## Requirements matrix

| # | Requirement | Regime | Module | Priority |
|---|---|---|---|---|
| 1 | PINT AE e-invoice generation and ASP connector | E-invoicing | Accounting | Must, before 1 Jul 2027 (1 Jan 2027 if ≥ AED 50m) |
| 2 | WPS due-date engine and SIF validation | WPS | Payroll | Must, now |
| 3 | 85% compliance check and exclusions register | WPS | Payroll | Must, now |
| 4 | Gratuity, leave and final-settlement engines | Labour Law | HR | Must |
| 5 | Tax-code master with travel agent/principal logic | VAT | Accounting, bookings | Must |
| 6 | TRN validation and Peppol ID on partners | VAT, e-invoicing | Contacts | Must |
| 7 | Input VAT ageing toward the 5-year limit | VAT | Accounting | Should |
| 8 | Related-party tagging and intercompany module | Corporate Tax | Accounting | Must for groups |
| 9 | Revenue threshold monitor (AED 3m, 50m, 200m) | CT, e-invoicing | Reporting | Should |
| 10 | Field classification, masking and view logging | PDPL | Platform | Must |
| 11 | Consent records and marketing opt-out | PDPL | CRM | Must |
| 12 | Data-subject-request workflow | PDPL | Platform | Should, before PDPL rules are issued |
| 13 | Breach register with a 72-hour clock | PDPL | Platform | Should |
| 14 | Document expiry alerts (passport, visa, Emirates ID, ILOE) | Labour Law | HR | Should |
| 15 | Emiratisation dashboard | Labour Law | HR | Should, for 50+ staff |

## Roadmap

1. **Now to Dec 2026**: WPS hardening (2-3); partner data clean-up for e-invoicing (6); audit trail and period locks.
2. **Jan-Mar 2027**: build and pilot the e-invoicing module on one company (1); help clients appoint an ASP by 31 Mar 2027.
3. **Apr-Jun 2027**: roll out e-invoicing for the 1 Jul 2027 go-live; VAT tax-code clean-up (5, 7).
4. **H2 2027**: PDPL toolkit (10-13), timed for the expected regulations; HR engines (4, 14, 15); Corporate Tax features (8, 9).

## Glossary

ASP = Accredited Service Provider; DPIA = Data Protection Impact Assessment; DPO = Data Protection Officer;
EDR/SCR = Employee Detail Record / Salary Control Record (SIF lines); EmaraTax = FTA portal; FTA = Federal Tax Authority;
ILOE = Involuntary Loss of Employment insurance; MOHRE = Ministry of Human Resources and Emiratisation; PDPL = Federal
Decree-Law 45 of 2021; Peppol = e-invoice network and standard; PINT AE = UAE Peppol invoice format; QFZP = Qualifying Free
Zone Person; SIF = Salary Information File; TRN/TIN = Tax Registration / Identification Number; WPS = Wage Protection System.
