---
name: google-ads
description: >
  Plan, build, audit or run Google Ads search campaigns for a local service business
  (plumber, dentist, roofer, cleaner, lawyer, clinic) on a small budget, with the agent
  drafting and the owner approving every change that spends money. Use this skill for a new
  Google Ads account or campaign, keyword research from customer questions, match types,
  negative keywords, location targeting, responsive search ads and assets, landing page
  message match, conversion tracking from GA4 or the Google Ads tag, budgets and bidding,
  Local Services Ads, a weekly check, and when the user says "PPC", "Google Ads is not
  working", "too expensive per lead", "wasted ad spend", "search terms" or "should we run
  Google ads".
---

# Google Ads: Pay Only for Searches That Become Customers

**RULE: The agent drafts and recommends; the owner approves. No campaign launches, no budget
or bid strategy changes, and no new keywords go live without the owner's written yes.**

A local business with a few hundred to a few thousand dollars a month cannot buy data. Every
click must come from a person who needs the service, in the service area, now. Most wasted
spend comes from three settings: broad keywords without negatives, "presence or interest"
location targeting, and the Search Partners and Display networks left on.

## 1. Before you build: prerequisites

Stop and fix these first. An ad that sends visitors to a broken funnel buys nothing.

- Conversion tracking works and is verified (`google-analytics`, step 8): leads, calls and
  bookings fire once, after success.
- The landing page has one offer and one action (`launch-landing-page`), and the form stores
  leads first (`launch-lead-capture`).
- Someone replies to leads within minutes (`launch-speed-to-lead`). Paid leads cool fast.
- The **owner** owns the Google Ads account and the billing. The agency joins through its
  manager account, with Standard access for building and Read only access for an agent that
  only reports.
- The owner gives a written monthly budget, the service area, the services to advertise, the
  hours that the phone is answered, and the average job value and close rate.

## 2. Local Services Ads or Search?

| | Local Services Ads | Search campaigns |
|---|---|---|
| Pays for | A lead (call, message, booking) | A click |
| Shows | Above search ads, with the Google Screened or Google Guaranteed badge | In the ad slots |
| Needs | An eligible category and region, license and insurance checks, background checks | Any business that follows the ad policies |
| Control | Little: services, area, budget, hours. Dispute bad leads for credit | Full: keywords, ads, bids, schedule |
| Good for | Home services and some professional services, where eligible | Everything else, and extra volume next to LSA |

Start with LSA when the category is eligible and the business passes the checks. Add a
Search campaign when LSA volume is too low or the service is not an LSA category. Track LSA
leads in the lead store with source `google-lsa`.

## 3. Account structure for a small budget

Fewer campaigns learn faster. Split only when the budget, the area or the landing page is
different.

```
Account (owner's)
├── Search | Emergency repair | Charleston 25 mi     (own budget: high value, call-driven)
│   ├── Ad group: water heater repair   → /water-heater-repair
│   └── Ad group: burst pipe            → /emergency-plumber
└── Search | Planned services | Charleston 25 mi
    ├── Ad group: water heater installation → /water-heater-installation
    └── Ad group: drain cleaning            → /drain-cleaning
```

- One ad group per **keyword theme** that shares one landing page and one ad message.
- Name campaigns `Network | Service | Area` so the weekly report reads itself.
- Network settings for Search: **Search Partners off, Display Network off.** Turn Search
  Partners on later only if its leads cost the same.
- Leave Performance Max and Display out until Search has at least 30 conversions a month.
  They spend across many placements and hide where the money went.

## 4. Keyword themes from real customer questions

1. Collect the words customers use: call notes, form messages, Google Business Profile
   questions, reviews, the Search Console queries report, and the owner's list of jobs that
   make money.
2. Group them by job, not by word: "water heater leaking", "no hot water", "water heater
   repair near me" are one theme.
3. Keep intent to hire. "Repair", "service", "near me", "cost", "emergency", the town name.
   Drop research intent ("how to", "DIY", "parts", "symptoms of").
4. Check each theme in Keyword Planner for volume and top-of-page bid range in the service
   area. A theme where one click costs more than about a tenth of the job's profit needs a
   very good landing page to pay back.
5. Write the result as a table: theme, keywords, match types, landing page, est. CPC.

**Match types:**

| Type | Syntax | Use |
|---|---|---|
| Exact | `[water heater repair]` | The core, proven terms |
| Phrase | `"water heater repair"` | The main working type at the start |
| Broad | `water heater repair` | Only with Smart Bidding, steady conversions, and a weekly search terms review |

## 5. Negatives

Add the account-level negative list from
[references/negative-keywords.md](references/negative-keywords.md) before launch: jobs, DIY,
free, training, parts, wrong services, and areas outside the service area. Then read the
**search terms** report every week and add a negative for each search that will never become
a customer. This is the cheapest money a small account saves.

## 6. Location, schedule and conversions

- **Location option: "Presence: people in or regularly in your included locations".** The
  default "presence or interest" pays for people in other states who read about your city.
- Target a radius or the list of towns the business serves. Exclude areas the owner does not
  serve.
- **Ad schedule:** if calls are the main action, run call-heavy ads only in the hours that
  someone answers. A missed paid call is spend with no chance of a job.
- **Conversions:** in Goals, Conversions, choose **one primary source** for each result:
  imported GA4 key events (`google-analytics`) or the Google Ads tag. The other source stays
  secondary. Two primary sources double-count and teach the bidding wrong lessons.
  - Calls from ads: the call asset with a Google forwarding number, counted as a conversion
    after a set call length (60 seconds is the default; set it to the length of a real
    enquiry).
  - Leads: `generate_lead`, with a value. Bookings: `book_appointment`. Sales: `purchase`.
  - Calls from the site: `call_click` is a tap, not a call. Keep it secondary unless a call
    tracking number confirms real calls.
  - Turn on enhanced conversions when consent allows it (`google-analytics`, step 6).
- **Auto-applied recommendations: off.** They can add keywords, raise budgets and change bids
  without anyone asking. Review recommendations by hand in the weekly check.

## 7. Ads and assets

- **Responsive search ads:** one or two per ad group. Up to 15 headlines (30 characters) and
  4 descriptions (90 characters). Include the service and the town, the proof (rating,
  years, license), the offer (same-day, fixed price, free estimate if true), and the action
  ("Call now", "Book online"). Pin only the headline that must say the service.
- **Assets** (they make the ad bigger and cost nothing extra):
  - Call asset with the tracked number, scheduled to answered hours.
  - Location asset, from the linked Google Business Profile (`launch-local-seo`).
  - Sitelinks to the main service pages, reviews, and the booking page.
  - Callouts ("Licensed and insured", "Upfront pricing", "Same-day service").
  - Structured snippet for services. Business name and logo.
- Every claim in an ad must be true and provable on the landing page. No invented reviews,
  ratings or prices.
- **Message match:** the landing page headline repeats the ad's promise and the search's
  words (`launch-landing-page`). Send each ad group to its own page, never to the home page
  unless the home page is the offer.

## 8. Budget and bidding for small budgets

- Google can spend up to twice the daily budget on a busy day, but not more than about 30.4
  times the daily budget in a month. Set the daily budget from the monthly number the owner
  approved.
- A budget too small for 10 clicks a day on the main theme learns slowly. Cut themes or
  areas before you cut the daily budget below that.
- **Bid strategy path:**
  1. Start: **Maximize clicks with a max CPC limit**, or **Manual CPC**, to collect clean
     search terms and the first conversions.
  2. After about 15 to 30 conversions in 30 days: **Maximize conversions** (or Maximize
     conversion value when lead values are set).
  3. When cost per lead is steady: add a **target CPA** close to the real average, not a
     wish. A target far below the average stops delivery.
- Each bid strategy change restarts learning for one to two weeks. Change one thing at a
  time, and only with the owner's approval.

## 9. Weekly check (15 minutes)

Use [references/weekly-check.md](references/weekly-check.md). In short: spend against the
approved budget, leads and cost per lead from the lead store, the search terms report with
negatives to add, ads and assets disapproved, conversion tracking health, and the
recommendations list. The output is a short report plus **change requests** for the owner,
each with the reason, the cost, and the expected effect.

## 10. Common money-wasters

| Waste | Fix |
|---|---|
| Search Partners and Display on in a Search campaign | Turn both off |
| "Presence or interest" location option | Presence only |
| Broad match without Smart Bidding or negatives | Phrase and exact, plus the negative list |
| All ad groups send traffic to the home page | One landing page per theme |
| Two primary conversion sources, or page views counted as conversions | One primary source per result, only real results |
| Auto-applied recommendations on | Off; review by hand |
| Ads run when nobody answers the phone | Ad schedule for call assets |
| Leads not answered for hours | `launch-speed-to-lead` |
| Bidding on the business's own name when no competitor bids on it | Pause brand ads; keep them if competitors appear |
| Changing bids, budgets and ads every few days | One change at a time, then wait 1 to 2 weeks |

## 11. Guardrails for agents

Follow `launch-agent-guardrails`. For Google Ads in particular:

- The agent may read reports and draft changes. With API access, use a read-only login or
  the Google Ads API with read scopes for reporting.
- **Always owner approval** for: launching or enabling a campaign, any budget change, a bid
  strategy or target change, new keywords or match types, new ads, and location or schedule
  changes. Store each approval with the change it covers.
- Negatives from the search terms report may be added under a standing approval, if the
  owner gives one in writing. Report each one added.
- Never accept Google's terms, add payment methods, or change account access for the owner.
- A daily spend check alerts the owner and the agency when spend is above 150% of the
  expected day, or when an account is suspended or ads are disapproved.

## Output

**For a new account or campaign:** a plan the owner approves before anything spends:
structure, keyword themes table, negative list, location and schedule, ad copy for each ad
group, assets, conversion setup, budget and bid strategy, and the launch checklist in
[references/launch-checklist.md](references/launch-checklist.md).

**For an audit:** each finding with **impact (estimated monthly waste)**, the evidence (a
screenshot or the report numbers), and the fix as a change request:

| Finding | Monthly waste | Evidence | Change request |
|---|---|---|---|
| Search Partners on | ~$180 | 22% of spend, 0 leads in 60 days | Turn off Search Partners |
| "Presence or interest" | ~$95 | Clicks from 14 states | Presence only |

**For the weekly check:** the report and the change requests from step 9.

## Related skills

- `google-analytics`: the key events and the link that this skill imports conversions from.
- `meta-ads`: the other paid channel, with the same conversions.
- `launch-landing-page`: one landing page per ad group, with message match.
- `launch-lead-capture`: stores each paid lead with its `gclid` and UTMs.
- `launch-speed-to-lead`: answers paid leads within minutes.
- `launch-local-seo`: the Business Profile behind the location asset and LSA.
- `launch-agent-guardrails`: the approval rules this skill follows.
- `seo-technical`: crawl and page health for the landing pages.
- `content-topic-plan`: the real customer questions that keyword themes start from.
