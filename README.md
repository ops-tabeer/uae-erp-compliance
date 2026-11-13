# UAE ERP compliance skill for Claude

A [Claude skill](https://docs.claude.com/en/docs/claude-code/skills) that explains what UAE law requires of ERP, HR and
payroll software. It also provides tools to check an Odoo system against those rules. It covers:

| Regime | Highlights |
|---|---|
| **PDPL** (Federal Decree-Law 45 of 2021) | In force, Executive Regulations still awaited; consent, data-subject rights, breach handling, cross-border transfers, field classification and masking |
| **Labour Law** (FDL 33 of 2021) | Contracts, probation and notice, overtime, leave, **end-of-service gratuity**, the 14-day final settlement, Emiratisation, ILOE |
| **WPS** (Ministerial Resolution 340 of 2026) | Salaries due by the **1st**, 85% threshold, exclusions, the **SIF** salary file and why banks reject it |
| **VAT** (FDL 8 of 2017 as amended) | TRN, the four treatments, travel **agent vs principal**, tax invoices, 28-day returns, the 5-year credit limit, 2026 penalties |
| **Corporate Tax** (FDL 47 of 2022) | 9% rate, Small Business Relief, adjustments, related parties and transfer pricing, 7-year records |
| **E-invoicing** (Peppol PINT AE) | ASPs, **1 Jan 2027** (≥ AED 50m) and **1 Jul 2027** go-live, scope for travel agencies, Cabinet Decision 173 of 2026 penalties, ERP architecture |

## Tools

```bash
# Gratuity and final settlement (21/30-day rule, unpaid leave, 24-month cap, Savings Scheme)
python uae-erp-compliance/scripts/gratuity.py --basic 6000 --start 2019-01-01 --end 2026-03-31 --leave-days 12

# Build or validate a WPS Salary Information File (IBAN check digits, ids, dates, totals, file name)
python uae-erp-compliance/scripts/wps_sif.py validate 1234567890123261028093000.sif
python uae-erp-compliance/scripts/wps_sif.py build --employees staff.csv --employer-id 1234567890123 \
    --routing 808610001 --month 2026-10

# Read-only Odoo 17-19 readiness check for UAE companies (TRN/Peppol IDs, untaxed lines, VAT locks,
# revenue thresholds, employee WPS data, audit trail)
python uae-erp-compliance/scripts/uae_readiness_check.py --db my_odoo_copy --out ./uae
```

`gratuity.py` and `wps_sif.py` need only Python 3. `uae_readiness_check.py` also needs `psycopg2`, and opens a
**read-only** database connection. Run `gratuity.py --self-test` and `wps_sif.py self-test` to check them.

## Install

```bash
git clone https://github.com/ops-tabeer/uae-erp-compliance.git
mkdir -p ~/.claude/skills && cp -R uae-erp-compliance/uae-erp-compliance ~/.claude/skills/
```

Restart Claude Code. The skill triggers on questions about WPS, SIF files, gratuity, TRNs, UAE VAT, e-invoicing or the
PDPL, or you can ask for it by name. It pairs well with
[erp-audit-skills](https://github.com/ops-tabeer/erp-audit-skills), which covers fraud forensics, controls and security hardening.

## Important

- **Not legal or tax advice.** Content reflects public sources as of 14 November 2026. Several 2026 instruments are new.
  `references/status-and-sources.md` lists what was independently confirmed and what still needs checking against the
  official MoF, FTA and MOHRE texts (for example the e-invoicing penalty cap and the WPS escalation days).
- No UAE PINT AE format module ships with Odoo 19.0 core. The e-invoicing reference explains the options.
- Account codes are never hard-coded. Accounts are identified by type and settings.

## Licence

MIT, see [LICENSE](LICENSE).
