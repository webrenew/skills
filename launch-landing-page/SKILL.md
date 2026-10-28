---
name: launch-landing-page
description: >
  Plan, write, build or audit a landing page or home page that turns a small business's
  visitors into calls, bookings and leads. Use this skill for landing pages, home pages,
  service pages, ad landing pages and offer pages, and when the user mentions conversion rate,
  "the site gets traffic but no leads", hero section, call to action, social proof, message
  match, or page structure.
---

# Landing Page: One Page, One Offer, One Action

**RULE: Each page has one main action. Every section either moves the visitor toward that
action or answers a reason not to take it. Cut everything else.**

Small business visitors arrive with a job to get done ("fix my leak", "book a cleaning").
They decide in seconds whether this business can do it, nearby, soon, at a fair price. The
page must answer those questions before it says anything about the business itself.

## 1. Decide before you write

Write these down first. If the owner cannot answer, the page cannot convert.

| Question | Example |
|---|---|
| Who is the visitor? | A homeowner in Charleston with a leaking water heater |
| Where do they come from? | Google search, the Business Profile, a Facebook ad |
| What is the one action? | Call now, or request a quote |
| What do they get? | A plumber at the door today, with a fixed price before work starts |
| Why this business? | Licensed, 4.9 stars from 380 reviews, 2-hour arrival window |
| What stops them? | Price uncertainty, trust, availability |

**Message match:** the headline repeats the promise of the ad, search or post that sent the
visitor. A visitor who clicked "same-day water heater repair" and lands on "Welcome to Harbor
Plumbing" leaves.

## 2. Structure

Above the fold, on a phone, the visitor sees:

1. **Headline:** the outcome, for whom, where. "Same-day water heater repair in Charleston."
   Under about 10 words.
2. **Subhead:** how, and the strongest proof. "Licensed plumbers, fixed price before we start,
   4.9 stars from 380 neighbors."
3. **Primary action** (button) and the **phone number** as a `tel:` link.
4. **Trust strip:** rating and review count, license or certification, years in business.

Then, in this order, keeping only the sections the business can support with real content:

5. **The problem and the outcome,** in the customer's words.
6. **How it works,** in 3 steps (book, we arrive, it's fixed).
7. **Proof:** reviews with first names, towns and dates; photos of real jobs; before and after.
8. **Offer details and price guidance:** "From $X" or what affects the price. Silence on
   price makes people assume it is high.
9. **FAQ** that answers the real objections (cost, timing, warranty, area served).
10. **Final call to action,** repeating the main action.

## 3. Copy rules

- Lead with the customer's outcome, not the business's history. "You" more than "we".
- Use numbers that the owner can prove: arrival time, years, review count, warranty length.
- **Put copy above the call to action, never beside it.** Stack the reassurance line, then the
  buttons.
- Use the same action verb everywhere: if the button says "Get my quote", the final button
  says it too.
- One idea per sentence. Short paragraphs. No "solutions", "world-class" or "cutting-edge".
- On mobile, keep a sticky bar with "Call" and the main action, and make sure it does not
  cover form fields or content.

## 4. Design rules

- Real photos of the team and work beat stock photos. Show faces.
- No carousels or sliders above the fold. They hide the message and slow the page.
- High contrast for the main button. One primary button style per page.
- The hero image is compressed and sized for phones, and it loads first (see
  `website-speed-optimization`). Every second before the headline shows costs visitors who
  leave before they read it.

## 5. Measure, then change one thing

- Define the conversion events: `Lead Submitted`, `Booking Completed`, `Call Clicked`
  (Title Case, as in `vercel-marketing-analytics`). Keep UTM parameters with each lead.
- Most small business pages do not get enough traffic for a valid A/B test. A rough guide is
  that each version needs at least a few hundred conversions. Below that, make one change at
  a time and compare 2 to 4 weeks before and after, against the same season if you can.
- Change the things with the biggest effect first: headline and message match, the offer,
  proof near the top, the form length (see `launch-lead-capture`), then design details.

## Output

**For a new page:** a section-by-section outline with the final copy for each section, the
data the owner must supply (reviews, photos, prices), and the events to track.

**For an audit:** score each item **pass / weak / missing** with the reason and the exact
rewrite:

| Item | Status | Fix |
|---|---|---|
| Headline states outcome and place | weak | "Same-day water heater repair in Charleston" |
| Phone visible above the fold on mobile | missing | Add `tel:` link next to the main button |
| Reviews near the top | ... | ... |

## Related Launch skills

- `launch-lead-capture`: the form on the page.
- `launch-booking-payments`: when the action is "book" or "pay".
- `launch-local-seo`: brings local visitors to the page.
