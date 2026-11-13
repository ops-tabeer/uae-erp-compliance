#!/usr/bin/env python3
"""Build or validate a UAE WPS Salary Information File (SIF).

Common layout (banks differ: always test with the client's WPS agent before go-live):
  * comma-separated, no header; one EDR line per employee and one SCR control line (last by default)
  * EDR: EDR, 14-digit employee id, 9-digit routing code, IBAN (AE, 23 chars) or salary card,
         period start YYYY-MM-DD, period end YYYY-MM-DD, days in period, fixed salary, variable pay, unpaid leave days
  * SCR: SCR, 13-digit employer id, 9-digit routing code, file date YYYY-MM-DD, time HHMM, salary month MMYYYY,
         number of EDRs, total (fixed+variable, exact to the fils), currency, employer reference
  * file name: <13-digit employer id><YYMMDD><hhmmss>.sif, date/time matching the SCR

Build:    python wps_sif.py build --employees staff.csv --employer-id 1234567890123 --routing 808610001
              --month 2026-10 [--reference ACME-OCT26] [--scr-first] [--out DIR]
          staff.csv columns: employee_id,routing,account,period_start,period_end,fixed,variable,unpaid_days
Validate: python wps_sif.py validate path/to/file.sif
Self-test: python wps_sif.py self-test
No database access; nothing is sent anywhere.
"""
import argparse
import csv
import datetime as dt
import io
import os
import re
import sys
from decimal import Decimal, InvalidOperation


def iban_ok(iban):
    s = re.sub(r"\s", "", iban or "").upper()
    if not re.fullmatch(r"AE\d{21}", s):
        return False, "UAE IBAN must be AE + 21 digits (23 characters)"
    r = s[4:] + s[:4]
    num = "".join(str(int(c, 36)) for c in r)
    if int(num) % 97 != 1:
        return False, "IBAN check digits are wrong"
    return True, ""


def money(v):
    try:
        d = Decimal(str(v).strip())
    except InvalidOperation:
        return None
    return d


def check_edr(f, n):
    errs = []
    if len(f) < 10:
        return [f"line {n}: EDR has {len(f)} fields, expected 10"]
    if not re.fullmatch(r"\d{14}", f[1]):
        errs.append(f"line {n}: employee id must be 14 digits")
    if not re.fullmatch(r"\d{9}", f[2]):
        errs.append(f"line {n}: routing code must be 9 digits")
    acct = f[3]
    if acct.upper().startswith("AE"):
        ok, why = iban_ok(acct)
        if not ok:
            errs.append(f"line {n}: {why}")
    elif not re.fullmatch(r"\d{8,19}", acct):
        errs.append(f"line {n}: account is neither a UAE IBAN nor a salary card number")
    try:
        s, e = dt.date.fromisoformat(f[4]), dt.date.fromisoformat(f[5])
        if e < s:
            errs.append(f"line {n}: period end before start")
        elif str((e - s).days + 1) != f[6].strip():
            errs.append(f"line {n}: days in period should be {(e - s).days + 1}")
    except ValueError:
        errs.append(f"line {n}: dates must be YYYY-MM-DD")
    for i, name in ((7, "fixed salary"), (8, "variable pay")):
        m = money(f[i])
        if m is None or "," in f[i] or m < 0 or m.as_tuple().exponent < -2:
            errs.append(f"line {n}: {name} must be a non-negative number with at most 2 decimals, no separators")
    if not re.fullmatch(r"\d+", f[9].strip()):
        errs.append(f"line {n}: unpaid leave days must be an integer")
    return errs


def validate_text(text, filename=None):
    lines = [l for l in text.splitlines() if l.strip()]
    errs, edrs, scr = [], [], None
    for n, l in enumerate(lines, 1):
        f = [x.strip() for x in next(csv.reader([l]))]
        if f[0] == "EDR":
            edrs.append(f)
            errs += check_edr(f, n)
        elif f[0] == "SCR":
            if scr:
                errs.append(f"line {n}: more than one SCR")
            scr = (n, f)
        else:
            errs.append(f"line {n}: unknown record type {f[0]!r} (header rows are not allowed)")
    if not scr:
        return errs + ["no SCR control record"]
    n, f = scr
    if len(f) < 9:
        return errs + [f"line {n}: SCR has {len(f)} fields, expected at least 9"]
    if not re.fullmatch(r"\d{13}", f[1]):
        errs.append(f"line {n}: employer id must be 13 digits")
    if not re.fullmatch(r"\d{9}", f[2]):
        errs.append(f"line {n}: employer routing code must be 9 digits")
    try:
        fdate = dt.date.fromisoformat(f[3])
    except ValueError:
        fdate = None
        errs.append(f"line {n}: file date must be YYYY-MM-DD")
    if not re.fullmatch(r"([01]\d|2[0-3])[0-5]\d", f[4]):
        errs.append(f"line {n}: file time must be HHMM 24-hour")
    if not re.fullmatch(r"(0[1-9]|1[0-2])\d{4}", f[5]):
        errs.append(f"line {n}: salary month must be MMYYYY")
    if f[6] != str(len(edrs)):
        errs.append(f"line {n}: record count {f[6]} but file has {len(edrs)} EDR lines")
    try:
        total = sum((Decimal(e[7]) + Decimal(e[8])) for e in edrs)
        if Decimal(f[7]) != total:
            errs.append(f"line {n}: SCR total {f[7]} differs from sum of EDRs {total:.2f}")
    except (InvalidOperation, IndexError):
        errs.append(f"line {n}: cannot total the amounts")
    if filename:
        m = re.fullmatch(r"(\d{13})(\d{6})(\d{6})\.sif", os.path.basename(filename), re.I)
        if not m:
            errs.append("file name must be <13-digit employer id><YYMMDD><hhmmss>.sif")
        else:
            if m.group(1) != f[1]:
                errs.append("file name employer id differs from SCR")
            if fdate and m.group(2) != fdate.strftime("%y%m%d"):
                errs.append("file name date differs from SCR file date")
            if m.group(3)[:4] != f[4]:
                errs.append("file name time differs from SCR file time")
    return errs


def build(rows, employer_id, routing, month, reference="", scr_first=False, now=None):
    now = now or dt.datetime.now()
    y, mth = map(int, month.split("-"))
    edr_lines, total = [], Decimal("0")
    for r in rows:
        fixed, var = Decimal(str(r["fixed"])).quantize(Decimal("0.01")), Decimal(str(r.get("variable") or 0)).quantize(Decimal("0.01"))
        s, e = dt.date.fromisoformat(r["period_start"]), dt.date.fromisoformat(r["period_end"])
        edr_lines.append(",".join(["EDR", r["employee_id"].strip(), r["routing"].strip(), re.sub(r"\s", "", r["account"]).upper(),
                                   s.isoformat(), e.isoformat(), str((e - s).days + 1), f"{fixed}", f"{var}",
                                   str(int(float(r.get("unpaid_days") or 0)))]))
        total += fixed + var
    scr = ",".join(["SCR", employer_id, routing, now.date().isoformat(), now.strftime("%H%M"), f"{mth:02d}{y}",
                    str(len(edr_lines)), f"{total:.2f}", "AED", reference])
    lines = [scr] + edr_lines if scr_first else edr_lines + [scr]
    name = f"{employer_id}{now.strftime('%y%m%d%H%M')}00.sif"
    return name, "\n".join(lines) + "\n"


def wps_due_date(month):
    """WPS due date under Ministerial Resolution 340 of 2026: the 1st of the month after the wage period."""
    y, m = map(int, month.split("-"))
    return dt.date(y + (m == 12), 1 if m == 12 else m + 1, 1)


def self_test():
    assert iban_ok("AE070331234567890123456")[0]
    assert not iban_ok("AE070331234567890123457")[0]
    rows = [dict(employee_id="10012345678901", routing="808610001", account="AE070331234567890123456",
                 period_start="2026-10-01", period_end="2026-10-31", fixed="6000", variable="1500", unpaid_days="0")]
    now = dt.datetime(2026, 10, 28, 9, 30)
    name, text = build(rows, "1234567890123", "808610001", "2026-10", "TEST", now=now)
    assert validate_text(text, name) == [], validate_text(text, name)
    bad = text.replace("7500.00", "7500.01")
    assert any("differs" in e for e in validate_text(bad, name))
    assert wps_due_date("2026-06") == dt.date(2026, 7, 1) and wps_due_date("2026-12") == dt.date(2027, 1, 1)
    print("self-test passed")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--employees", required=True)
    b.add_argument("--employer-id", required=True)
    b.add_argument("--routing", required=True)
    b.add_argument("--month", required=True, help="YYYY-MM wage period")
    b.add_argument("--reference", default="")
    b.add_argument("--scr-first", action="store_true", help="some banks want the SCR as the first line")
    b.add_argument("--out", default=".")
    v = sub.add_parser("validate")
    v.add_argument("file")
    sub.add_parser("self-test")
    a = p.parse_args()
    if a.cmd == "self-test":
        return self_test()
    if a.cmd == "validate":
        errs = validate_text(open(a.file, encoding="utf-8").read(), a.file)
        print("\n".join(errs) if errs else "OK: no errors found")
        return 1 if errs else 0
    rows = list(csv.DictReader(open(a.employees, encoding="utf-8")))
    pre = []
    for i, r in enumerate(rows, 2):
        line = ",".join(["EDR", r["employee_id"], r["routing"], r["account"], r["period_start"], r["period_end"], "0",
                         str(r["fixed"]), str(r.get("variable") or 0), str(r.get("unpaid_days") or 0)])
        pre += [e.replace("line 1:", f"csv row {i}:") for e in check_edr(next(csv.reader([line])), 1) if "days in period" not in e]
    if pre:
        print("Fix these before building:\n" + "\n".join(pre))
        return 1
    name, text = build(rows, a.employer_id, a.routing, a.month, a.reference, a.scr_first)
    errs = validate_text(text, name)
    if errs:
        print("\n".join(errs))
        return 1
    path = os.path.join(a.out, name)
    open(path, "w", encoding="utf-8").write(text)
    print(f"Wrote {path} ({len(rows)} employees). WPS due date: {wps_due_date(a.month)}")


if __name__ == "__main__":
    sys.exit(main())
