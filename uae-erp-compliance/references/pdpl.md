# Chapter 1: Personal data protection (PDPL)

The mainland data protection law, Federal Decree-Law 45 of 2021, has applied since 2 Jan 2022, but its
Executive Regulations have **not** been issued and the regulator is only now being formed. Build to its
principles now: the law is in force, and HR, CRM and travel systems hold exactly the data it protects.

## Legal landscape

| Regime | Covers | Regulator | Status (Nov 2026) |
|---|---|---|---|
| Federal Decree-Law 45 of 2021 (PDPL) | Mainland companies and most free zones, plus organisations abroad processing data of people in the UAE | UAE Data Office, being folded into the new Federal Authority for AI and Data | In force; Executive Regulations not yet issued |
| DIFC Data Protection Law 5 of 2020 | Companies in the DIFC | DIFC Commissioner of Data Protection | Actively enforced; amended July 2025 |
| ADGM Data Protection Regulations 2021 | Companies in ADGM | ADGM Commissioner | Actively enforced |
| Sector rules (health data law, Central Bank rules) | Healthcare and banking data | Sector regulators | Take priority over PDPL in their sectors |

Mainland businesses fall under the PDPL. A DIFC or ADGM client is subject to its own regime instead, which is stricter in practice.

## "In force but not enforced"

- The regulations were due within 6 months, so in early 2022. As of mid-2026, Chambers, Ashurst and Morgan Lewis
  all report they haven't been issued. They are meant to settle lawful bases, rights procedures, cross-border
  transfers and breach notification.
- On 14 Jun 2026 the UAE announced a Federal Authority for AI and Data, merging the AI Office, TDRA's digital
  government sector and the data office. It is expected to finish the regulations and start enforcement. No
  timeline has been set.
- **Expect a short runway.** Once the regulations are published there are 6 months to comply, extendable once by
  the Cabinet.
- **Don't quote fines.** Penalties are left to a Cabinet decision that hasn't been issued. Figures such as
  "AED 50,000-5 million" can't be traced to any instrument.

## Definitions

- **Personal data**: any information about an identified or identifiable person: name, ID numbers, location,
  online identifiers, and physical, economic, cultural or social identity.
- **Sensitive personal data**: family background, ethnicity, political or religious beliefs, criminal records,
  biometric and genetic data, health data and sex life. In HR and travel systems that means medical certificates,
  attendance-device fingerprints, religion fields, and passport or visa data that reveals nationality and family links.
- **Controller** decides why and how (e.g. the travel company for its staff and customers). **Processor**
  processes on the controller's behalf (e.g. the software house hosting or supporting a client's ERP).
- **Excluded**: government data, purely personal use, security and judicial processing, health data under the
  health law, banking and credit data under financial laws, and DIFC/ADGM entities.

## Lawful processing

Consent is the default. It must be specific, informed, clear and given by an affirmative act: no pre-ticked
boxes, and silence isn't consent. It can be withdrawn as easily as it was given, and the controller must be able
to prove it. Processing without consent is allowed to perform a contract (booking a trip), comply with UAE law
(VAT, labour, WPS records), meet employment and social-security obligations, protect vital interests, for legal
claims, and for data the person made public. HR processing rests mostly on contract and legal obligation, and
marketing on consent.

## Data subject rights (design for a 30-day response)

| Right | What the person can ask | Software must |
|---|---|---|
| Information and access | What you hold, why, recipients, retention | Export all records about one person from every module |
| Portability | Structured, machine-readable copy | JSON or CSV, not only PDF |
| Correction | Fix inaccurate data | Self-service edit or request workflow, logged |
| Erasure | Delete data no longer needed | Delete or anonymise, but block where law requires keeping it (tax records) |
| Restriction | Pause processing during a dispute | A "restricted" flag that stops use but keeps the record |
| Objection | Stop processing, esp. direct marketing | One-click opt-out honoured on all channels |
| Automated decisions | No significant machine-only decisions | Human review on lead scoring, CV screening, credit decisions |

## Duties

- **Security**: encryption, access control and pseudonymisation.
- **Record of processing**: what data, purpose, access, retention and destinations.
- **DPO** where processing is high-risk, involves systematic assessment of sensitive data (profiling, automated
  decisions), or covers sensitive data at scale. The DPO can be internal, external or outside the UAE.
- **DPIA** before high-risk processing.
- **Breach notification** "without delay" to the regulator and affected people. Treat **72 hours** as the target.
- **Processors** act only on documented instructions, keep data secure, delete or return it at contract end, and
  assist with rights requests and breaches.

## Cross-border transfers

Article 22 allows transfers to adequate countries. Article 23 allows others under a binding contract with
equivalent protection, with express consent, or where needed for a contract or legal claim. No adequacy list and
no standard clauses have been published (mid-2026). Sending a passenger's passport to an overseas hotel, airline or
visa centre is needed to perform the booking. Hosting HR data abroad, or sending CVs to a US AI service, needs a
contractual basis.

## Software requirements

**Data model**
1. Classify every field: public, internal, personal or sensitive. Passport, Emirates ID, visa copies, salary, IBAN,
   medical certificates, biometrics and religion are sensitive by default.
2. Tag each record with its lawful basis and purpose ("booking contract", "legal obligation (VAT)", "marketing consent").
3. Store consent as its own record: who, what, which wording version, when, channel, and withdrawal.

**Access and security**
1. Role-based access with field masking (a sales agent sees `P••••••42`).
2. Encrypt sensitive fields at rest beyond database encryption, and use TLS in transit.
3. Log every view, export and change of sensitive fields. Most systems log changes but not views.
4. Limit and log bulk exports, the most common leak.

**Rights and retention**
1. A data-subject-request workflow: intake, identity check, cross-module search, export/correct/erase, deadline tracker.
2. Retention rules per record type with automatic anonymisation. A legal hold overrides erasure: tax records are
   kept even if the customer asks for deletion.
3. Anonymise instead of hard-deleting where records feed financial reports.

**Operations**
1. A breach register and incident workflow with a 72-hour clock.
2. Hosting location chosen and recorded per client; list sub-processors (email, SMS, WhatsApp, AI services).
3. A data processing agreement with every hosted or supported client.
4. Human review on automated decisions (lead scoring, CV ranking, fraud flags).

## Odoo notes

Use `groups=` on sensitive fields, keep them out of `tracking`, never make ID scans public attachments, restrict
`base.group_allow_export`, and neutralise and mask non-production copies. View logging isn't native: a custom
`read` override or a reverse-proxy log is needed.
