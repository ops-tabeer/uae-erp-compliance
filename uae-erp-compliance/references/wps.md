# Chapter 3: Wage Protection System (WPS)

Since **1 Jun 2026** every MOHRE-registered private employer must pay each month's wages through WPS **by the 1st
of the following month**. Anything later is delayed. Source: Ministerial Resolution 340 of 2026, replacing
Resolution 598 of 2022. The old 15-day grace is gone, so payroll needs a hard deadline and a fully automated
salary file. Paying earlier (e.g. on the 28th) remains compliant.

## How it works

1. Payroll is approved in HR/ERP.
2. The system generates the Salary Information File (SIF) and the payment instruction.
3. The employer uploads both to its WPS agent (bank or exchange house).
4. The agent validates the file (rejecting any error) and pays employee accounts or salary cards.
5. The Central Bank records payment, and MOHRE matches it to the registered contract and work permit.
6. MOHRE flags employers below the compliance threshold.

Covers all MOHRE-registered establishments: the mainland plus free zones that apply WPS, such as JAFZA and DMCC.
DIFC and ADGM are outside it. Salaries may be in AED or a contractually agreed currency.

## Resolution 340 vs 598

| Rule | Before (598/2022) | Now (340/2026) |
|---|---|---|
| Due date | Contract pay date + 15-day grace | 1st of the month after the wage period (June wages due 1 July) |
| Threshold | 80% of total wages | **85%** of total wages paid by the due date |
| New employees | 30-day grace | Grace removed |
| Per-employee test | none | An employee paid ≥ 85% isn't counted as unpaid, but can still claim the rest |

## Escalation (per handbook, citing Gulf News; verify the resolution text, since sources differ)

| Days late | Measure |
|---|---|
| 1 | Electronic monitoring starts |
| 2 | Notices and reminders |
| 5 | Formal warning; new work permits can be suspended |
| 11 | Administrative fines; a repeat within 6 months can drop the company to Category 3 (costlier permits) |
| 16 | Automatic labour dispute for companies with 25+ workers |
| 21 | Asset attachment, travel bans on responsible managers, referral to Public Prosecution (50+ workers, after two consecutive months) |

For a travel company, suspended work permits are painful: no new hires and no visa renewals until salaries are paid.

## Excluded from the 85% test (11 categories; the ones payroll must handle)

Employees with a wage claim in court; reported absent (for the report period); on approved, notified and documented
unpaid leave; held under a legal order (MOHRE notified); foreign employees of foreign companies paid abroad (with
consent and approval); mission work permits of 3 months or less.
**Software**: a WPS exclusion flag on the employee with reason, document and dates. Otherwise an unpaid employee on
approved leave drags the company below 85%.

## SIF format (common layout; banks differ, so build per-bank templates and test with each bank)

- Comma-separated text, **no header**. One **EDR** per employee, plus one **SCR** control record (commonly last).
- File name: `<13-digit MOHRE employer id><YYMMDD><hhmmss>.sif`, with date and time matching the SCR.

EDR fields:

| # | Field | Format |
|---|---|---|
| 1 | Record type | `EDR` |
| 2 | Employee ID | 14-digit MOHRE labour card / person number |
| 3 | Employee's agent routing code | 9 digits |
| 4 | Account | UAE IBAN (23 chars, AE, valid check digits) or salary card number |
| 5 | Pay period start | YYYY-MM-DD |
| 6 | Pay period end | YYYY-MM-DD |
| 7 | Days in period | end − start + 1 |
| 8 | Fixed salary | decimal, no thousands separator, not negative |
| 9 | Variable pay | decimal, 0.00 if none |
| 10 | Unpaid leave days in period | integer, 0 if none |

SCR fields: `SCR`, 13-digit employer id, 9-digit employer routing code, file date YYYY-MM-DD, file time HHMM (24h),
salary month MMYYYY, number of EDRs, total (sum of fixed + variable, exact to the fils), currency `AED`, optional reference.

```
EDR,10012345678901,808610001,AE070331234567890123456,2026-10-01,2026-10-31,31,6000.00,1500.00,0
EDR,10012345678902,803320101,AE460260001015123456789,2026-10-01,2026-10-31,31,9000.00,0.00,2
SCR,1234567890123,808610001,2026-10-28,0930,102026,2,16500.00,AED,ACME-OCT26
```
(invented numbers; some banks, e.g. HSBC, use their own Excel layouts)

## Why files get rejected

The SCR total differs from the EDR sum (even by 0.01); record count mismatch; file name date or time doesn't match
the SCR; wrong date format (DD-MM-YYYY), 12-hour time, or commas in amounts; invalid IBAN or IBAN bank ≠ routing code;
expired work permit or invalid employee id; fixed salary ≠ the MOHRE-registered contract.
`scripts/wps_sif.py validate <file>` catches all but the last three (which need MOHRE/bank data).

## Payroll module requirements

1. **Due-date engine**: the WPS due date per period (1st of next month), with escalation to the finance manager at T-5, T-3 and T-1 if unsent.
2. **Contract matching**: fixed salary vs the MOHRE contract, blocking mismatches.
3. **Validation before export**: IBANs, routing codes, work-permit expiry, totals, counts.
4. **85% check**, computed the way MOHRE does, excluding flagged categories.
5. **Exclusions register** with reason, document and dates.
6. **Partial payments**: track the shortfall and carry it to the next file.
7. **Proof of payment**: store the SIF, bank acknowledgement and payment confirmation per run (courts expect WPS records).
8. **Segregation of duties**: one person prepares and another approves. Whoever can edit bank details can't release payments.
9. **Bank detail changes**: an IBAN change needs a second approval and notifies the employee. This blocks the most common payroll fraud.
