# Enterprise Account Security & Verification SOP

## 1. Customer Authentication Protocol
Before discussing customer invoicing records, changing payment methods, or disclosing order details, support engineers must verify the caller or submitter identity:
1. Verify customer account number (e.g. `ACC-ACME-901`).
2. Verify registered enterprise support PIN (e.g. `9812`).
3. Confirm that ticket submitter email matches the approved company domain.

## 2. Guardrails Against Social Engineering
Support engineers are strictly prohibited from:
- Releasing unredacted payment card details or API secrets under any circumstances.
- Overriding account multi-factor authentication (MFA) without secondary supervisor sign-off.
- Modifying subscription tiers via unverified phone calls.

## 3. Incident Logging
All authorization checks and data disclosures must be recorded with operator timestamp, ticket ID, and authenticated identity reference in the audit log.
