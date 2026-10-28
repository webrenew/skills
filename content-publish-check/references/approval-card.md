# Owner Approval Card

The owner approves on a phone, in under a minute. Show only what the owner must decide.

```
APPROVE A POST · Harbor Plumbing
"Water heater leaking from the bottom? What it means"
Draft v3 · 1,040 words · 3 photos · by Sam Harbor
Read it: https://docs.google.com/document/d/<shared-draft-id> (the full text, v3)

Please confirm (only you know these):
1. "Most repairs are done in one visit." True for water heaters?
2. Photo 2 shows the customer's garage. Is the written consent from 15 Sep enough?

Verdict: READY AFTER OWNER CONFIRMS

[Approve and publish]   [Edit]   [Reject]
```

## Rules

- **The "Read it" link** shows the exact draft: the blog's own preview URL if it has one, a
  shared document, or the full text on the card. On a Launch site the post is saved with
  `write_post` only after approval, so link a shared document or put the text on the card.
  Never link a URL that nothing creates.

- One card per item. Never ask the owner to approve a batch with one tap.
- List at most five confirmations. More than five means the draft is not ready: fix it first.
- Each confirmation is a yes-or-no question about one claim, in plain words.
- **Approve** publishes the exact version on the card. **Edit** opens the text; the edited
  text goes through the check again. **Reject** asks for a reason from a short list: wrong
  facts, wrong tone, not our topic, too long, other.
- No answer means no publish. Send one reminder after two business days.

## Approval log

Store one row per decision, kept for as long as the post is live:

| Field | Example |
|---|---|
| item | `post:water-heater-leaking-from-bottom`, or `channel:facebook:water-heater-leaking-from-bottom` for a repurposed post |
| version | draft id or SHA-256 of the final text |
| decision | approved / edited / rejected |
| approver | Sam Harbor |
| at | 2026-11-03T14:12:00Z |
| confirmed | claim numbers 1 and 2 |
| reason | (for reject) |

The log answers "who approved this, and what did it say then?" in under a minute.
