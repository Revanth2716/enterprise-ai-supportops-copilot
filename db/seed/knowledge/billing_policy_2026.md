# Enterprise Global Billing Policy (2026 Edition)

## 1. Overview and Invoicing Cycles
All enterprise contracts are invoiced on the first calendar day of each billing period. Invoices are dispatched electronically with net-30 terms unless an automated credit card or SEPA direct debit arrangement is active.

## 2. Automated Charge Processing and Retries
When credit card auto-billing is enabled, our payment gateway attempts payment authorization up to two times in the event of upstream network timeouts. If a gateway timeout occurs, the system logs a secondary attempt. In rare cases of webhook delivery latency, a duplicate authorization record may be created.

## 3. Duplicate Charge Detection and Automatic Resolution
Under Section 3.1 of the Enterprise Agreement, if a customer account displays multiple charges for identical invoice identifiers within a 48-hour window:
1. Support engineers are authorized to immediately confirm the duplicate transaction reference.
2. The excess charge qualifies for an expedited credit adjustment or immediate card reversal without managerial re-authorization.
3. The customer must be issued a resolution notification detailing the primary transaction reference (`TXN-88102-PRIMARY`) and the voided duplicate reference.

## 4. Disputed Invoices and Escalations
If an invoice dispute relates to usage overages rather than duplicate billing, the support engineer must request meter logs from the telemetry service and escalate to Level 2 Operations within 4 business hours.
