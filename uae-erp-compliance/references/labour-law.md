# Chapter 2: UAE Labour Law and the HR module

Federal Decree-Law 33 of 2021 (in force 2 Feb 2022), amended by Decree-Law 20 of 2023 and 9 of 2024, with
Cabinet Resolution 1 of 2022. The regulator is MOHRE. Most of it turns into HR software rules.

## Coverage

Private-sector employees on the mainland and in most free zones. **Not** covered: government employees, domestic
workers (own law), and DIFC and ADGM employees (own employment laws). An HR product needs a **jurisdiction**
setting per company or employee.

## Recent changes

| Date | Change | Software must |
|---|---|---|
| 1 Jun 2026 | WPS: salaries due on the 1st of the next month; threshold 85% (Ministerial Resolution 340 of 2026) | Payroll calendar locked to that date (see wps.md) |
| 1 Jan 2026 | Emirati minimum wage AED 6,000/month for new or renewed permits; existing contracts raised by 30 Jun 2026 | Validation rule on UAE-national contracts |
| 2026 | Emiratisation target for 50+ staff rises to **10% by 31 Dec 2026**; each unfilled role costs AED 9,000/month (some sources say AED 10,000 later in 2026: confirm with MOHRE/Nafis) | Emiratisation tracker and cost forecast |
| 2026 | Automated ILOE (unemployment insurance) checks: AED 400 fine for not subscribing, AED 200 more when a policy lapses | Track ILOE status and expiry per employee |
| 31 Aug 2024 | Decree-Law 9/2024: claims up to **2 years** after exit; MOHRE decides disputes up to AED 50,000 and can order up to 2 months' salary during a dispute | Keep employee and payroll records ≥ 2 years after exit, ideally 5 (7 for tax) |
| 31 Aug 2024 | Fines for serious violations AED 100,000-1,000,000 | Strong evidence trail for work permits and Emiratisation |

## Contracts

All contracts are fixed-term (unlimited contracts no longer exist), usually up to 3 years and renewable. Types:
full-time, part-time, temporary, flexible, remote and job-sharing. A contract states parties, job title, place, start
date, duration, wage and payment, hours, rest days, probation, leave and notice, never below legal minimums.
**Software**: versioned contracts with dates, expiry alerts 60-90 days ahead, and a block on leave or notice below the minimum.

## Probation and notice

| Situation | Rule |
|---|---|
| Probation length | Up to 6 months; can't be extended or repeated with the same employer |
| Employer ends during probation | At least 14 days' written notice |
| Employee leaves in probation to exit the UAE | 14 days' notice |
| Employee leaves in probation to join another UAE employer | 30 days' notice; a 1-year work-permit ban can apply if broken |
| Notice after probation | Per contract, 30-90 days, the same for both sides |

**Software**: compute the last working day from the notice date and length; flag probation resignations and apply notice by reason.

## Hours and overtime

- Up to 8 hours/day and 48/week. 2 hours less per day in Ramadan. At least 1 paid rest day a week.
- Overtime is capped at 2 hours/day, except to prevent serious loss or an accident.
- Ordinary overtime: basic hourly wage plus at least **25%**. Between 22:00 and 04:00: plus at least **50%**.
- Work on a rest day or public holiday: a substitute day off, or basic wage plus at least 50%.
- The premium is on **basic** wage. Hourly basic is usually monthly basic × 12 ÷ 365 ÷ 8. Confirm the
  convention with the client's adviser and make it a setting.

## Leave

| Leave | Entitlement | Pay |
|---|---|---|
| Annual | 2 days/month after 6 months' service; 30 calendar days/year after 1 year | Basic + housing allowance |
| Sick | Up to 90 days/year after probation | 15 days full, 30 days half, 45 days unpaid |
| Maternity | 60 days | 45 full, 15 half; extra unpaid if mother or baby ill |
| Parental | 5 working days within 6 months of birth | Full |
| Bereavement | 5 days spouse; 3 days parent, child, sibling, grandchild, grandparent | Full |
| Study | 10 working days/year after 2 years, at a UAE institution | Full |
| Public holidays | As announced by the Cabinet | Full |
| Hajj | Up to 30 days once during employment | Unpaid |

Unused annual leave on exit is paid on **basic only** (confirm against contracts). **Software**: accrual engine per type
with eligibility dates; sick-pay steps feeding payroll; a holiday calendar admins update (Islamic dates move);
unpaid leave stored separately because it is removed from gratuity service; carry-forward rules and the encashment value at exit.

## End-of-service gratuity

With at least 1 year of continuous service, on the **last basic salary**:
- 21 days' basic for each of the first 5 years, 30 days for each year after, partial years pro-rated
- capped at 2 years' wage (24 × monthly basic)
- unpaid leave days not counted as service
- resignation no longer reduces gratuity (2021 law); it can be withheld only for amounts the employee owes

```
daily wage = last monthly basic / 30
gratuity   = min( daily × [21 × min(Y,5) + 30 × max(Y-5, 0)],  24 × monthly basic )
Y = net years of service (decimal, excluding unpaid leave); 0 if under 1 year
```

Worked example: AED 6,000 basic, 7 years 3 months → daily 200; years 1-5 105 days = 21,000; years 6-7 60 days = 12,000;
last 3 months 7.5 days = 1,500; **total 34,500** (cap 144,000). Use `scripts/gratuity.py`.

**Savings Scheme** (Cabinet Resolution 96 of 2023): employers may make monthly contributions to an approved fund instead
of paying gratuity. The HR system must know who is enrolled and stop accruing gratuity for those periods (`--scheme-days`).

## Final settlement

All dues within **14 days** of the contract ending. The statement covers: salary to the last working day, unused leave
encashment, gratuity (formula and service shown), overtime or commission owed, each deduction with its legal reason
(loans, advances, damage), and the employee's signature or acknowledgement. The software starts a 14-day countdown.

## Records

Per employee: contract, ID and work-permit details, wage, leave and disciplinary records, end-of-service settlement.
50+ employees: written grievance and disciplinary policies. Keep ≥ 2 years after exit. 5-7 years also covers tax.

## HR module checklist

1. Jurisdiction per entity (federal law / DIFC / ADGM).
2. Contract register with expiry alerts, type and versions.
3. Probation tracking with automatic notice rules.
4. Attendance linked to an overtime engine (day, night, holiday rates).
5. A leave engine for all statutory types with eligibility dates and pay steps.
6. A gratuity engine (21/30 days, unpaid-leave exclusion, 2-year cap, Savings Scheme).
7. A final-settlement statement with a 14-day deadline.
8. Document expiry alerts: passport, Emirates ID, visa, work permit, ILOE, medical insurance.
9. An Emiratisation dashboard (share of skilled headcount vs target, forecast cost).
10. Grievance and disciplinary records restricted to HR.

## Odoo 19 notes

`hr.employee`: `permit_no`, `visa_no`, `visa_expire`, `work_permit_expiration_date` (tracked, HR group).
`hr.version` (replaces contract fields in 19): `identification_id` (Emirates ID), `passport_id`, `wage`. Bank
accounts: `hr.employee.bank_account_ids` (relation `employee_bank_account_rel`). Stock payroll is Enterprise;
community stacks (OHRMS) need the gratuity and leave rules added.
