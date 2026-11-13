#!/usr/bin/env python3
"""UAE end-of-service gratuity and final-settlement calculator (Federal Decree-Law 33 of 2021).

Rules implemented (see references/labour-law.md):
  - daily wage = last monthly BASIC salary / 30
  - 21 days per year for the first 5 years, 30 days per year after that, partial years pro-rated
  - unpaid leave days and Savings Scheme periods are excluded from service
  - nothing if net service is under 1 year
  - total capped at 24 x monthly basic (2 years' wage)
  - resignation does NOT reduce gratuity under the 2021 law
The year convention (365 days) and "daily wage = basic/30" are the common convention: confirm with the
client's legal adviser and keep them as settings.

Usage:
  python gratuity.py --basic 6000 --start 2019-01-01 --end 2026-03-31 [--unpaid-days 0] [--scheme-days 0]
      [--leave-days 12 --leave-basis basic] [--other 0] [--deductions 0] [--json]
  python gratuity.py --self-test
"""
import argparse
import datetime as dt
import json
import sys

YEAR_DAYS = 365


def gratuity(basic, start, end, unpaid_days=0, scheme_days=0, year_days=YEAR_DAYS):
    if basic < 0:
        raise ValueError("basic salary cannot be negative")
    if end < start:
        raise ValueError("end date is before start date")
    service_days = (end - start).days + 1
    net_days = max(service_days - unpaid_days - scheme_days, 0)
    years = net_days / year_days
    daily = basic / 30.0
    if years < 1:
        return dict(service_days=service_days, net_days=net_days, years=round(years, 4), daily_wage=round(daily, 2),
                    days_first5=0.0, days_after5=0.0, uncapped=0.0, cap=round(24 * basic, 2), gratuity=0.0,
                    note="net service under 1 year: no gratuity")
    d1 = 21 * min(years, 5)
    d2 = 30 * max(years - 5, 0)
    uncapped = daily * (d1 + d2)
    cap = 24 * basic
    return dict(service_days=service_days, net_days=net_days, years=round(years, 4), daily_wage=round(daily, 2),
                days_first5=round(d1, 4), days_after5=round(d2, 4), uncapped=round(uncapped, 2), cap=round(cap, 2),
                gratuity=round(min(uncapped, cap), 2),
                note="capped at 24 months' basic" if uncapped > cap else "")


def settlement(g, basic, housing=0.0, leave_days=0.0, leave_basis="basic", other=0.0, deductions=0.0, end=None):
    """Final settlement: gratuity + leave encashment + other dues - deductions; due within 14 days of the end date."""
    daily_leave = (basic + (housing if leave_basis == "basic+housing" else 0)) / 30.0
    leave_pay = round(daily_leave * leave_days, 2)
    total = round(g["gratuity"] + leave_pay + other - deductions, 2)
    due = (end + dt.timedelta(days=14)).isoformat() if end else None
    return dict(leave_encashment=leave_pay, other_dues=round(other, 2), deductions=round(deductions, 2),
                total_settlement=total, pay_by=due)


def self_test():
    # Handbook worked example: AED 6,000 basic, 7 years 3 months, no unpaid leave -> AED 34,500
    g = gratuity(6000, dt.date(2019, 1, 1), dt.date(2019, 1, 1) + dt.timedelta(days=int(7.25 * 365) - 1))
    assert abs(g["gratuity"] - 34500) < 10, g  # 7.25 x 365 is not a whole number of days
    assert gratuity(6000, dt.date(2026, 1, 1), dt.date(2026, 6, 30))["gratuity"] == 0  # under a year
    big = gratuity(10000, dt.date(1990, 1, 1), dt.date(2026, 1, 1))
    assert big["gratuity"] == 240000, big  # cap 24 x basic
    u = gratuity(6000, dt.date(2020, 1, 1), dt.date(2021, 12, 31), unpaid_days=365)
    assert abs(u["years"] - 1.0027) < 0.01 and u["gratuity"] > 0, u
    print("self-test passed")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--basic", type=float)
    p.add_argument("--start")
    p.add_argument("--end")
    p.add_argument("--unpaid-days", type=float, default=0)
    p.add_argument("--scheme-days", type=float, default=0, help="days covered by the voluntary Savings Scheme")
    p.add_argument("--housing", type=float, default=0)
    p.add_argument("--leave-days", type=float, default=0, help="unused annual leave days to encash")
    p.add_argument("--leave-basis", choices=["basic", "basic+housing"], default="basic",
                   help="unused leave on exit is usually paid on basic only (confirm per contract)")
    p.add_argument("--other", type=float, default=0, help="unpaid wages, overtime, commission still owed")
    p.add_argument("--deductions", type=float, default=0, help="amounts the employee owes (loans, advances)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if a.basic is None or not a.start or not a.end:
        p.error("--basic, --start and --end are required")
    start, end = dt.date.fromisoformat(a.start), dt.date.fromisoformat(a.end)
    g = gratuity(a.basic, start, end, a.unpaid_days, a.scheme_days)
    s = settlement(g, a.basic, a.housing, a.leave_days, a.leave_basis, a.other, a.deductions, end)
    out = {**g, **s}
    if a.json:
        print(json.dumps(out, indent=2))
        return
    print(f"Service {g['service_days']} days, net {g['net_days']} days = {g['years']} years")
    print(f"Daily wage {g['daily_wage']:,.2f} (basic {a.basic:,.2f} / 30)")
    print(f"Days: {g['days_first5']} (first 5 yrs x21) + {g['days_after5']} (after 5 yrs x30)")
    print(f"Gratuity {g['gratuity']:,.2f}  (uncapped {g['uncapped']:,.2f}, cap {g['cap']:,.2f}) {g['note']}")
    print(f"Leave encashment {s['leave_encashment']:,.2f}; other dues {s['other_dues']:,.2f}; deductions {s['deductions']:,.2f}")
    print(f"TOTAL SETTLEMENT {s['total_settlement']:,.2f}, pay by {s['pay_by']} (14 days after last working day)")


if __name__ == "__main__":
    sys.exit(main())
