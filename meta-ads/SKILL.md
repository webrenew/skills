---
name: meta-ads
description: >
  Plan, build, audit or run Facebook and Instagram ads (Meta Ads) for a small business on a
  small budget, with tracking that respects consent and with the owner approving every change
  that spends money. Use this skill for the Meta Pixel and Conversions API (CAPI), event
  mapping and deduplication, Events Manager, campaign objectives (Leads, Sales), instant forms
  versus website leads, local radius and lookalike audiences, customer lists, ad creative from
  real jobs, special ad categories (housing, employment, financial products), frequency and
  budget, a weekly check, and when the user says "Facebook ads", "Instagram ads", "boost a
  post", "Meta pixel", "CAPI", "cost per lead on Facebook" or "our Facebook leads are junk".
---

# Meta Ads: Real Work, Real Customers, Spend the Owner Approved

**RULE: Track only with consent, show only real work and real words from real customers, and
change nothing that spends money without the owner's written yes.**

On Facebook and Instagram, people are not searching for a plumber. The ad must stop the
scroll with something true and local (a real job, a real face, a real review) and make the
next step easy. Meta's delivery system then finds more people like the ones who acted, so
the events you send decide who sees the ads.

## 1. Prerequisites

- Conversion tracking in GA4 works (`google-analytics`), and the site's consent banner works.
- The landing page or instant form is ready (`launch-landing-page`, `launch-lead-capture`),
  and someone replies within minutes (`launch-speed-to-lead`).
- The **owner's** Meta business portfolio owns the Facebook Page, the Instagram account, the
  ad account, the dataset (Pixel) and the payment method. The agency gets partner access.
  Never run ads from the agency's ad account: the owner loses the data when the agency leaves.
- Verify the website domain in the business portfolio (Brand safety, Domains).
- The owner gives a written monthly budget, the service area, the offer, and photos or videos
  of real work that they have the right to use.

## 2. Pixel plus Conversions API, with consent

Send each result from the browser (Pixel) **and** the server (Conversions API, CAPI), with
the same `event_id`, so Meta counts it once and still sees results that browsers block.

1. **Consent first.** Call `fbq("consent", "revoke")` before `fbq("init", ...)` where the
   banner asks for consent, and `fbq("consent", "grant")` when the visitor accepts ad or
   marketing cookies. Use the same banner choice as Google consent mode (`google-analytics`,
   step 3). Store the choice with the lead.
2. **Server events only for consented visitors.** CAPI does not read the banner. The server
   must check the stored consent before it sends.
3. **Hash the identifiers.** Email and phone are normalized (trimmed, lowercase, phone in
   digits with the country code) and hashed with SHA-256 before they leave the server.
   `fbp` and `fbc` cookies, IP address and user agent are sent unhashed, as Meta requires.
4. **Deduplicate.** The browser event and the server event share `event_name` and
   `event_id` (use the lead id or order id).
5. Check Events Manager: the event match quality score, the deduplication rate, and the
   Diagnostics tab.

Code for the Pixel, the shared `track` helper and the CAPI call is in
[references/conversions-api.md](references/conversions-api.md).

## 3. Map events to the same results as GA4

| Site event | GA4 (`google-analytics`) | Meta standard event | Optimize for it |
|---|---|---|---|
| `Lead Submitted` | `generate_lead` | `Lead` | Yes, for lead campaigns |
| `Call Clicked` | `call_click` | `Contact` | Only if calls are the main action |
| `Booking Completed` | `book_appointment` | `Schedule` | Yes, for booking businesses |
| `Checkout Started` | `begin_checkout` | `InitiateCheckout` | No |
| `Purchase Completed` | `purchase` | `Purchase` (with `value`, `currency`) | Yes, for sales |

Send `value` and `currency` where the owner gave a lead value. Never send personal data in
custom parameters (`content_name`, `content_category` and similar): no names, emails, phone
numbers or form answers.

## 4. Campaign objective and lead path

- **Objective: Leads** for enquiries and bookings, **Sales** for online purchases. Avoid
  Traffic and Engagement for a lead goal: they find people who click and like, not people who
  hire.
- Conversion location options for Leads:

| | Website | Instant form | Calls |
|---|---|---|---|
| Lead volume | Lower | Higher | Lowest |
| Lead quality | Higher: the visitor read the page | Lower: two taps, prefilled | High, if someone answers |
| Needs | A fast page and the Pixel and CAPI | A webhook or CRM sync into the lead store | Answered hours |
| Use when | The page converts well and the offer needs explaining | Volume matters and the follow-up is fast | Urgent services |

- For instant forms, use the **Higher intent** form type (a review step before submit), ask
  one qualifying question (service, town, timing), add the privacy policy link, and sync each
  lead into the lead store within minutes (Meta's lead webhook, or the CRM's integration).
  A form lead that sits in Meta's Leads Center for a day is lost.
- Send lead status back if possible (Conversions API for CRM: "qualified", "won"), so Meta
  learns which leads became customers.

## 5. Audiences for a local business

- **Location:** people living in the service area, as a radius or a list of towns. Check the
  map: a 25-mile radius around a coastal town is half ocean.
- **Advantage+ audience** (Meta's default) usually beats hand-picked interests on small
  budgets. Add age only if the service truly needs it (for example, 65+ for a Medicare
  service) and the category allows it.
- **Customer lists and lookalikes:** only from customers who agreed to marketing, as stored
  with the lead (`launch-lead-capture`, section 7). Meta hashes the list on upload; upload
  through Ads Manager or the API, never a shared spreadsheet. A lookalike needs at least 100
  people from one country; a few hundred works better.
- **Retargeting** site visitors and video viewers from the last 30 to 90 days, with a
  reminder offer. Exclude people who already became leads.
- **Exclusions:** current customers for new-customer offers, and staff.

## 6. Special ad categories

Ads about **housing, employment, financial products and services (credit), or social issues,
elections or politics** must declare the category. Meta then limits targeting (for example
no age, gender or ZIP-code targeting, a minimum radius, no lookalikes).

- Declare it at the campaign level when the ad offers or promotes any of these, even a little:
  a property manager's rentals, a "we're hiring" ad, financing for a roof.
- Not declaring leads to rejected ads and account restrictions.
- Rules change. Read Meta's current special ad category rules before each new campaign in
  these areas. Full list and checks in
  [references/ad-policy-checklist.md](references/ad-policy-checklist.md).

## 7. Creative from real jobs

- Show the real team and real work: before and after, a 15-second phone video of the job, the
  owner talking to the camera. Real beats polished on these feeds.
- **Vertical video and images (4:5 for feed, 9:16 for Stories and Reels)**, with captions,
  because most people watch without sound.
- First line: the outcome and the town. "Same-day water heater replacement in Mount
  Pleasant." Then proof, then one action.
- Make 3 or 4 ads per ad set with different hooks (a before-and-after, a review, an offer, the
  owner). Replace the weakest every 2 to 4 weeks.
- **No fake testimonials or reviews.** The US FTC rule on fake reviews and testimonials bans
  invented reviews, reviews by people who did not use the service, reviews written by AI as
  if from customers, and hiding that an endorser was paid or is staff. Use real customer
  words with their permission, and keep the proof. Photos of a customer's home need the
  customer's permission.
- Every claim (price, rating, license, "same-day") must be true and shown on the landing page.

## 8. Budget, frequency and learning

- Start with **one campaign, one ad set, 3 or 4 ads.** Splitting a small budget into many
  ad sets means none of them learns.
- Meta's learning phase needs about **50 optimization events per ad set in 7 days**. Most
  small budgets do not reach it ("Learning limited"). That is acceptable. Do not edit the ad
  set every few days to "fix" it: each significant edit restarts learning.
- In a small local area, watch **frequency**. Above about 3 per week, people see the same ad
  too often: refresh the creative or widen the area before raising the budget.
- Daily budget = the owner's approved monthly budget / 30. Raise it by no more than about 20%
  at a time, with approval, and wait a week.
- **Boosted posts** are fine for a reach goal, but use Ads Manager with the Leads objective
  for leads.

## 9. Weekly check

Spend against budget; leads and cost per lead **from the lead store** (Meta's own count of
"results" is generous); lead quality from the owner; frequency; link click-through rate; ad
rejections; event match quality and Diagnostics in Events Manager; and the ad comments.
Hide spam, answer real questions within a day, and never delete honest complaints. Use
[references/weekly-check.md](references/weekly-check.md).

## 10. Guardrails for agents

Follow `launch-agent-guardrails`. For Meta in particular:

- The agent may read Ads Manager reports and Insights, and draft campaigns, ads, audiences
  and replies.
- **Always owner approval** for: publishing or turning on a campaign, ad set or ad; any
  budget or bid change; new audiences or customer list uploads; new creative and ad copy; and
  any special ad category decision. Store each approval with the change.
- Comment replies are customer-facing: draft them for approval (`launch-agent-guardrails`,
  section 1).
- Never accept Meta's terms, add payment methods, or change business portfolio access for
  the owner.
- Alert the owner and the agency when daily spend is above 150% of the expected day, an ad is
  rejected, or the ad account is restricted.

## Output

**For a new setup:** tracking plan (Pixel, CAPI, consent, event map) with code and the
Events Manager checks; a campaign plan the owner approves before anything spends (objective,
lead path, audience, special ad category decision, budget, 3 or 4 ads with copy and the
source of each photo or video); and the instant form or landing page checklist.

**For an audit:** each finding with impact, evidence and the change request:

| Finding | Impact | Evidence | Change request |
|---|---|---|---|
| Pixel fires before consent | Legal risk in the EU and UK | Network tab: `fbevents.js` before banner choice | Add `fbq("consent", "revoke")` before `init` |
| Traffic objective for a lead goal | High cost per lead | 1,900 clicks, 4 leads | New Leads campaign, website conversion location |
| Frequency 6.2 in 7 days | Ad fatigue | Delivery report | Two new ads from this month's jobs |

## Related skills

- `google-analytics`: the same results as GA4 key events, and the consent setup.
- `google-ads`: the search channel, with the same conversions.
- `launch-landing-page`: the page behind each ad.
- `launch-lead-capture`: stores website and instant-form leads, with consent and UTMs.
- `launch-speed-to-lead`: answers each lead within minutes.
- `launch-agent-guardrails`: approval rules for anything that spends or posts.
- `content-voice-and-proof`: the proof bank of real jobs, photos and approved quotes for ads.
- `content-case-study`: customer consent and the FTC testimonial rules for job stories.
