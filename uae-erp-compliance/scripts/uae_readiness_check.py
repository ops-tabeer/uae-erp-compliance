#!/usr/bin/env python3
"""Read-only UAE compliance readiness check for an Odoo 17-19 database (UAE companies only).

  U01 UAE localisation and e-invoicing modules (l10n_ae, account_edi_ubl_cii, account_peppol; PINT AE format)
  U02 Partner master data for VAT/e-invoicing: B2B customers and suppliers without a valid 15-digit TRN,
      without a Peppol endpoint (EAS 0235 = first 10 digits of the TRN), duplicate TRNs
  U03 Invoices: posted customer invoices with untaxed lines (every line needs a tax treatment), credit notes
      not linked to an original invoice, foreign-currency invoices
  U04 Revenue thresholds per company (last 12 months of income): AED 375k VAT registration, 3m Small Business
      Relief, 50m e-invoicing wave 1 and audit, 200m transfer-pricing file
  U05 Period locks: tax lock date vs the last quarter whose VAT return is due (28 days after quarter end)
  U06 Employees in UAE companies (WPS/HR): missing or invalid IBAN, missing Emirates ID, work-permit/visa/passport
      expired or expiring within 60 days
  U07 Record keeping: restrictive audit trail and 7-year retention reminder
Writes UAE_READINESS.md and one CSV per check. Never writes to the database.

Usage: python uae_readiness_check.py --db mydb --out ./uae [--company "Dubai"] [--host ... --user ...]
"""
import argparse
import csv
import datetime as dt
import os
import re
import sys

try:
    import psycopg2
except ImportError:  # pragma: no cover
    sys.exit("psycopg2 is required (use the Odoo venv's python)")

TODAY = dt.date.today()


def args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--db", required=True)
    for k in ("host", "port", "user", "password"):
        p.add_argument(f"--{k}")
    p.add_argument("--out", required=True)
    p.add_argument("--company", help="substring of company name (default: all companies whose country is AE)")
    return p.parse_args()


class DB:
    def __init__(self, a):
        kw = {"dbname": a.db, **{k: getattr(a, k) for k in ("host", "port", "user", "password") if getattr(a, k)}}
        self.conn = psycopg2.connect(**kw)
        self.conn.set_session(readonly=True, autocommit=True)
        self.cur = self.conn.cursor()

    def q(self, sql, p=None):
        self.cur.execute(sql, p or {})
        return [d[0] for d in self.cur.description], self.cur.fetchall()

    def one(self, sql, p=None):
        return self.q(sql, p)[1][0][0]

    def has_col(self, t, c):
        return self.one("select count(*)>0 from information_schema.columns where table_name=%(t)s and column_name=%(c)s",
                        {"t": t, "c": c})

    def has_table(self, t):
        return self.one("select to_regclass(%(t)s) is not null", {"t": t})


def iban_ok(s):
    s = re.sub(r"\s", "", s or "").upper()
    if not re.fullmatch(r"AE\d{21}", s):
        return False
    return int("".join(str(int(c, 36)) for c in s[4:] + s[:4])) % 97 == 1


def main():
    a = args()
    db = DB(a)
    os.makedirs(a.out, exist_ok=True)
    items = []

    def add(code, title, status, finding, fix, cols=None, rows=None):
        if cols is not None:
            with open(os.path.join(a.out, f"{code}.csv"), "w", newline="") as fh:
                w = csv.writer(fh)
                w.writerow(cols)
                w.writerows([[v.isoformat() if hasattr(v, "isoformat") else v for v in r] for r in rows])
        items.append((code, title, status, finding, fix))

    # companies
    if a.company:
        _, comp = db.q("select c.id, c.name from res_company c where c.name ilike %(n)s", {"n": f"%{a.company}%"})
    else:
        _, comp = db.q("""select c.id, c.name from res_company c join res_partner p on p.id=c.partner_id
                          join res_country co on co.id=p.country_id where co.code='AE' order by c.id""")
    cids = [c[0] for c in comp] or [-1]

    # U01 modules
    _, mods = db.q("""select name, state from ir_module_module where name in
                      ('l10n_ae','account_edi_ubl_cii','account_peppol','l10n_ae_ubl_pint','l10n_ae_edi')""")
    m = dict(mods)
    pint = m.get("l10n_ae_ubl_pint") or m.get("l10n_ae_edi")
    status = "FAIL" if m.get("l10n_ae") != "installed" else ("WARN" if not pint or pint != "installed" else "PASS")
    add("U01", "UAE localisation & e-invoicing modules", status,
        f"l10n_ae={m.get('l10n_ae', 'absent')}, account_edi_ubl_cii={m.get('account_edi_ubl_cii', 'absent')}, "
        f"account_peppol={m.get('account_peppol', 'absent')}, UAE PINT format module={'present: ' + pint if pint else 'not available in this Odoo build'}.",
        "Install l10n_ae for UAE taxes and reports. Odoo 19.0 ships PINT formats for SG/MY/JP/ANZ but not yet for the UAE: "
        "plan a custom PINT AE generator or use the ASP's connector, and track Odoo releases for an official module.",
        ["module", "state"], mods)

    # U02 partner master data
    cols, rows = db.q("""
      with used as (
        select m.partner_id, bool_or(m.move_type in ('out_invoice','out_refund')) customer, bool_or(m.move_type in ('in_invoice','in_refund')) supplier,
               count(*) n, max(m.date) last_date
        from account_move m where m.state='posted' and m.move_type in ('out_invoice','out_refund','in_invoice','in_refund')
          and m.company_id = any(%(c)s) and m.date >= current_date - 365 group by 1)
      select p.id, p.name, coalesce(co.code,'') country, p.is_company, coalesce(p.vat,'') vat, coalesce(p.peppol_eas,'') eas,
             coalesce(p.peppol_endpoint,'') endpoint, u.customer, u.supplier, u.n invoices_12m, u.last_date
      from used u join res_partner p on p.id=u.partner_id left join res_country co on co.id=p.country_id
      where p.is_company and coalesce(co.code,'AE')='AE'""" if db.has_col("res_partner", "peppol_eas") else """
      select p.id, p.name, '' country, p.is_company, coalesce(p.vat,'') vat, '' eas, '' endpoint, true customer, false supplier, 0, null
      from res_partner p where false""", {"c": cids})
    out = []
    trn_seen = {}
    for r in rows:
        vat = re.sub(r"\D", "", r[4])
        flags = []
        if not vat:
            flags.append("no TRN (or TIN) recorded")
        elif not re.fullmatch(r"100\d{12}", vat):
            flags.append("TRN is not 15 digits starting 100")
        if vat:
            trn_seen.setdefault(vat, []).append(r[1])
        if r[7] and (r[5] != "0235" or (vat and r[6] != vat[:10])):
            flags.append("Peppol ID not set to 0235:<first 10 digits of TRN>")
        if flags:
            out.append((r[1], r[4], r[5], r[6], "customer" if r[7] else "supplier", r[9], "; ".join(flags)))
    dup = {k: v for k, v in trn_seen.items() if len(v) > 1}
    out += [(", ".join(v), k, "", "", "", "", "same TRN on several partners") for k, v in dup.items()]
    b2b = len(rows)
    no_trn = sum(1 for o in out if "no TRN" in o[6])
    add("U02", "Partner master data (TRN / Peppol ID)", "FAIL" if no_trn else ("WARN" if out else "PASS"),
        f"{b2b} UAE business partners invoiced in the last 12 months; {no_trn} without a TRN/TIN; "
        f"{sum(1 for o in out if '15 digits' in o[6])} with a malformed TRN; "
        f"{sum(1 for o in out if 'Peppol' in o[6])} customers without the Peppol ID; {len(dup)} TRNs shared by several partners.",
        "Clean master data first: most e-invoicing go-live failures are bad TRNs and Peppol IDs, not bad XML. Validate the "
        "15-digit TRN, record the verification date, set EAS 0235 and endpoint = first 10 digits of the TRN.",
        ["partner", "vat", "peppol_eas", "peppol_endpoint", "role", "invoices_12m", "issue"], out)

    # U03 invoices
    _, untaxed = db.q("""
      select m.name, c.name, m.invoice_date, rp.name, count(*) lines_without_tax, round(sum(l.price_subtotal),2) amount
      from account_move m join account_move_line l on l.move_id=m.id and l.display_type='product'
      join res_company c on c.id=m.company_id left join res_partner rp on rp.id=m.partner_id
      where m.state='posted' and m.move_type in ('out_invoice','out_refund') and m.company_id = any(%(c)s)
        and m.invoice_date >= current_date - 365
        and not exists (select 1 from account_move_line_account_tax_rel r where r.account_move_line_id=l.id)
      group by m.id, m.name, c.name, m.invoice_date, rp.name order by m.invoice_date""", {"c": cids})
    _, cn = db.q("""
      select m.name, c.name, m.invoice_date, rp.name, round(m.amount_total,2), left(coalesce(m.ref,''),80)
      from account_move m join res_company c on c.id=m.company_id left join res_partner rp on rp.id=m.partner_id
      where m.state='posted' and m.move_type='out_refund' and m.reversed_entry_id is null and m.company_id = any(%(c)s)
        and m.invoice_date >= current_date - 365 order by m.invoice_date""", {"c": cids})
    fx = db.one("""select count(*) from account_move m join res_company c on c.id=m.company_id
                   where m.state='posted' and m.move_type in ('out_invoice','out_refund') and m.currency_id<>c.currency_id
                     and m.company_id = any(%(c)s) and m.invoice_date >= current_date - 365""", {"c": cids})
    rows = [("untaxed lines",) + r for r in untaxed] + [("credit note without original invoice",) + r[:4] + (None, r[4]) for r in cn]
    add("U03", "Invoice and credit-note content", "FAIL" if untaxed else ("WARN" if cn else "PASS"),
        f"{len(untaxed)} posted customer invoices in 12 months have lines with no tax (every line needs exactly one treatment: "
        f"standard, zero, exempt or out of scope); {len(cn)} credit notes not linked to an original invoice; "
        f"{fx} foreign-currency invoices (must also show AED at the Central Bank rate).",
        "Force a tax code on every line (use explicit 0% zero-rated / exempt / out-of-scope codes, never blank). "
        "Create credit notes by reversing the original invoice so PINT AE can reference it.",
        ["issue", "document", "company", "date", "partner", "lines", "amount"], rows)

    # U04 revenue thresholds (income accounts, last 12 months, company currency)
    _, rev = db.q("""
      select c.name, round(-sum(l.balance)) revenue_12m
      from account_move_line l join account_account a on a.id=l.account_id join res_company c on c.id=l.company_id
      where l.parent_state='posted' and a.account_type in ('income','income_other') and l.company_id = any(%(c)s)
        and l.date >= current_date - 365 group by c.name order by 2 desc""", {"c": cids})
    rows = []
    for name, r in rev:
        r = float(r or 0)
        rows.append((name, r, "yes" if r > 375000 else "no", "over" if r > 3_000_000 else "under",
                     "wave 1 (1 Jan 2027)" if r >= 50_000_000 else "wave 2 (1 Jul 2027)", "required" if r >= 200_000_000 else "no"))
    add("U04", "Revenue thresholds per company", "INFO",
        "; ".join(f"{r[0]}: {r[1]:,.0f}" for r in rows) or "no revenue found",
        "Use these to plan: VAT registration > AED 375k; Small Business Relief only if revenue ≤ AED 3m in every period; "
        "e-invoicing wave and audited accounts at AED 50m; transfer-pricing master/local file at AED 200m (company). "
        "Revenue here is booked income, not the legal test: confirm with the tax adviser, especially for VAT groups.",
        ["company", "revenue_12m", "VAT registration threshold passed", "Small Business Relief (3m)", "e-invoicing", "TP file (200m)"], rows)

    # U05 tax lock
    q_end = dt.date(TODAY.year, ((TODAY.month - 1) // 3) * 3 + 1, 1) - dt.timedelta(days=1)
    due = q_end + dt.timedelta(days=28)
    last_filed_q = q_end if TODAY > due else (dt.date(q_end.year, ((q_end.month - 1) // 3) * 3 + 1, 1) - dt.timedelta(days=1))
    cols_ = ["name", "tax_lock_date", "fiscalyear_lock_date"] + (["hard_lock_date"] if db.has_col("res_company", "hard_lock_date") else [])
    _, locks = db.q(f"select {', '.join(cols_)} from res_company where id = any(%(c)s) order by name", {"c": cids})
    stale = [l for l in locks if not l[1] or l[1] < last_filed_q]
    add("U05", "VAT period locks", "FAIL" if stale else "PASS",
        f"{len(stale)} of {len(locks)} UAE companies have no tax lock date or one before {last_filed_q} "
        f"(the last quarter whose return was due by the 28th). Filed periods must not change except by voluntary disclosure.",
        "After filing each VAT return, set the Tax Return lock date to the period end (Accounting > Lock Dates). "
        "Monthly filers: lock monthly.", cols_, locks)

    # U06 employees
    if db.has_table("hr_employee"):
        id_col = "v.identification_id" if db.has_table("hr_version") and db.has_col("hr_version", "identification_id") else \
                 ("e.identification_id" if db.has_col("hr_employee", "identification_id") else "null")
        join_v = "left join hr_version v on v.id=e.current_version_id" if "v." in id_col and db.has_col("hr_employee", "current_version_id") else ""
        if "v." in id_col and not join_v:
            id_col = "null"
        bank_rel = "employee_bank_account_rel" if db.has_table("employee_bank_account_rel") else None
        bank_sql = (f"(select string_agg(b.acc_number, ' | ') from {bank_rel} r join res_partner_bank b on b.id=r.bank_account_id "
                    f"where r.employee_id=e.id)") if bank_rel else \
                   ("(select acc_number from res_partner_bank b where b.id=e.bank_account_id)" if db.has_col("hr_employee", "bank_account_id") else "null")
        exp_cols = [c for c in ("work_permit_expiration_date", "visa_expire") if db.has_col("hr_employee", c)]
        if bank_rel:
            bcols = [r[0] for r in db.q(f"select column_name from information_schema.columns where table_name='{bank_rel}'")[1]]
            ecol = next((c for c in bcols if 'employee' in c), None)
            bcol = next((c for c in bcols if 'bank' in c or 'partner' in c), None)
            bank_sql = (f"(select string_agg(b.acc_number, ' | ') from {bank_rel} r join res_partner_bank b on b.id=r.{bcol} "
                        f"where r.{ecol}=e.id)") if ecol and bcol else "null"
        # custom HR modules often keep Emirates ID / labour card in their own columns: use them when present
        for extra in ("emirates_id", "emirates_id_no", "eid_number"):
            if db.has_col("hr_employee", extra):
                id_col = f"coalesce(nullif(e.{extra},''), {id_col})"
                break
        permit_col = "e.permit_no"
        for extra in ("labour_card_no", "labor_card_no", "mol_personal_no", "wps_person_id"):
            if db.has_col("hr_employee", extra):
                permit_col = f"coalesce(nullif(e.{extra},''), e.permit_no)"
                break
        _, emps = db.q(f"""
          select e.id, e.name, c.name, {id_col} emirates_id, coalesce({permit_col},'') permit_no, {bank_sql} bank,
                 {', '.join('e.' + c for c in exp_cols) if exp_cols else 'null'}
          from hr_employee e join res_company c on c.id=e.company_id {join_v}
          where e.active and e.company_id = any(%(c)s) order by c.name, e.name""", {"c": cids})
        out = []
        for r in emps:
            flags = []
            accts = [x.strip() for x in (r[5] or "").split("|") if x.strip()]
            if not accts:
                flags.append("no bank account / salary card")
            elif not any(iban_ok(x) or re.fullmatch(r"\d{8,19}", re.sub(r"\s", "", x)) for x in accts):
                flags.append("bank account is not a valid UAE IBAN or card number")
            if not r[3]:
                flags.append("no Emirates ID")
            if not r[4]:
                flags.append("no work permit / labour card number")
            for name, d in zip(exp_cols, r[6:]):
                if d and d < TODAY:
                    flags.append(f"{name} expired {d}")
                elif d and d <= TODAY + dt.timedelta(days=60):
                    flags.append(f"{name} expires {d}")
            if flags:
                out.append((r[1], r[2], "; ".join(flags)))
        add("U06", "Employee data for WPS and HR", "FAIL" if any("no bank" in o[2] or "not a valid" in o[2] or "expired" in o[2] for o in out) else ("WARN" if out else "PASS"),
            f"{len(emps)} active employees in UAE companies; {len(out)} with gaps "
            f"({sum('no bank' in o[2] or 'not a valid' in o[2] for o in out)} bank, {sum('Emirates ID' in o[2] for o in out)} Emirates ID, "
            f"{sum('work permit' in o[2] for o in out)} permit number, {sum('expire' in o[2] for o in out)} expired/expiring documents).",
            "A WPS file is rejected for an invalid IBAN, invalid employee id or expired work permit, and salaries are due on the "
            "1st (Ministerial Resolution 340 of 2026). Fix master data before the run; require a second approval for IBAN changes. "
            "Custom HR modules may store Emirates ID / labour card in their own fields: map them before relying on this check.",
            ["employee", "company", "issues"], out)

    # U07 record keeping
    if db.has_col("res_company", "restrictive_audit_trail"):
        _, rat = db.q("select name, restrictive_audit_trail from res_company where id = any(%(c)s) order by name", {"c": cids})
        off = [r for r in rat if not r[1]]
        add("U07", "Audit trail and retention", "FAIL" if off else "PASS",
            f"{len(off)} of {len(rat)} UAE companies without the Restrictive Audit Trail. Retention: Corporate Tax 7 years, "
            f"VAT 5 years (+2 while a refund claim is pending), labour claims 2 years after exit: default to 7 years and never hard-delete.",
            "Enable Accounting > Settings > Restrictive Audit Trail; keep backups for 7 years; anonymise personal data at the end of "
            "retention instead of deleting accounting records.", ["company", "restrictive_audit_trail"], rat)

    lines = [f"# UAE compliance readiness: {a.db}", "",
             f"Run {dt.datetime.now():%Y-%m-%d %H:%M}. Companies: {', '.join(c[1] for c in comp) or 'none'}. Read-only.", "",
             "| # | Check | Status | Finding |", "|---|---|---|---|"]
    lines += [f"| {c} | {t} | **{s}** | {f} |" for c, t, s, f, _ in items]
    lines += ["", "## What to do", ""] + [f"- **{c} {t}**: {fix}" for c, t, s, f, fix in items if s in ("FAIL", "WARN", "INFO")]
    lines += ["", "Not legal or tax advice. Confirm each rule against the MoF, FTA and MOHRE texts or a licensed adviser."]
    open(os.path.join(a.out, "UAE_READINESS.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
