# Webrenew Skills

A curated collection of AI agent skills built by [Webrenew](https://webrenew.com), an enterprise design and development agency based in Greater Charleston, SC.

We partner with [Vercel](https://vercel.com), [Blackbox.ai](https://blackbox.ai), and others to deliver high-performance digital products at scale. These skills encode our team's expertise into reusable, agent-ready knowledge — enabling faster audits, better code, and consistent quality across projects.

## Skills

| Skill | Description |
|-------|-------------|
| [website-speed-optimization](./website-speed-optimization) | Next.js performance audit and optimization — Core Web Vitals, bundle analysis, caching, and rendering strategies |
| [seo-technical](./seo-technical) | Technical SEO implementation and audit — Metadata API, JSON-LD structured data, Open Graph, sitemaps, Core Web Vitals |
| [accessibility-audit](./accessibility-audit) | WCAG 2.2 AA compliance audit and implementation — ARIA patterns, keyboard navigation, screen readers, testing |
| [security-hardening](./security-hardening) | Security hardening and OWASP compliance — CSP, Auth.js, Server Action security, input validation, production checklist |
| [asd-ste100-writing](./asd-ste100-writing) | Clear product copy with ASD-STE100 Simplified Technical English and benefit-first framing |
| [dependabot-batch](./dependabot-batch) | Collapse many open Dependabot PRs into one branch and one PR — manifest edits, single lockfile regeneration, gates, held-back bumps |
| [overscroll-behavior](./overscroll-behavior) | Stop the desktop rubber-band bounce and keep mobile pull-to-refresh — `overscroll-behavior: none` gated behind `(pointer: fine)`, `contain` for nested scrollers |

## Launch pack

Nine skills that help a small business get found, turn visits into leads, and follow up
automatically, with a person in charge of anything an agent writes.

| Skill | What it gives the business |
|-------|----------------------------|
| [launch-local-seo](./launch-local-seo) | Found in local search and the map pack: one business identity, LocalBusiness schema, service pages, Google Business Profile, reviews |
| [launch-site-checklist](./launch-site-checklist) | A go-live check that catches the silent launch bugs: redirects, `noindex`, forms that deliver, analytics, ownership |
| [launch-landing-page](./launch-landing-page) | One page, one offer, one action: structure, copy and design that turn visitors into calls and leads |
| [launch-lead-capture](./launch-lead-capture) | Short forms that convert, spam protection without friction, and storage-first delivery so no lead is lost |
| [launch-speed-to-lead](./launch-speed-to-lead) | A reply within minutes and a follow-up sequence that stops when the lead replies, books or opts out |
| [launch-booking-payments](./launch-booking-payments) | Online booking (Cal.com) and payments (Stripe) with verified webhooks that keep leads in sync |
| [launch-lead-triage-agent](./launch-lead-triage-agent) | An AI agent that sorts each lead and drafts a reply for the owner to approve from a phone |
| [launch-site-health-report](./launch-site-health-report) | A weekly plain-English report and instant alerts when the site, form or certificate breaks |
| [launch-agent-guardrails](./launch-agent-guardrails) | Rules for any customer-facing agent: approval, grounding, injection safety, limits, kill switch, evals |

Install the pack:

```bash
npx skills add https://github.com/webrenew/skills --skill launch-local-seo launch-site-checklist launch-landing-page launch-lead-capture launch-speed-to-lead launch-booking-payments launch-lead-triage-agent launch-site-health-report launch-agent-guardrails
```

## Content skills

Seven skills that help a small business publish content that sounds like the owner, proves
it with real work, and brings leads. A person approves everything before it goes live.

| Skill | What it gives the business |
|-------|----------------------------|
| [content-voice-and-proof](./content-voice-and-proof) | Content that sounds like the owner: voice, readers, places served, a proof bank of real jobs, numbers, photos and approved quotes, and a real byline |
| [content-topic-plan](./content-topic-plan) | Know what to write next: real customer questions ranked by lead value, tied to service pages, in a calendar the owner can keep |
| [content-blog-post](./content-blog-post) | A post that answers one customer question better than anyone nearby, with an answer AI search can quote, ready for Launch or Markdown |
| [content-publish-check](./content-publish-check) | Nothing goes live that the owner cannot stand behind: a source for every claim, search checks, consent, and an approval card |
| [content-repurpose](./content-repurpose) | One post becomes two to three weeks of channel posts: Google Business Profile, social, video, FAQ and email, with UTM tags |
| [content-case-study](./content-case-study) | Finished jobs become proof that wins the next one: consent, a five-question interview, and the FTC testimonial rules |
| [content-refresh](./content-refresh) | Know which posts bring leads and fix the ones that slip, with a one-minute monthly report for the owner |

Start with `content-voice-and-proof`: the other six load its content kit. The skills reuse the
business identity and profile from `launch-local-seo` and `launch-lead-triage-agent`, and
check copy with `asd-ste100-writing`, so the command below installs those three as well. The
other Launch and web skills named in each skill's "Related skills" are optional companions.

Install the content skills:

```bash
npx skills add https://github.com/webrenew/skills --skill content-voice-and-proof content-topic-plan content-blog-post content-publish-check content-repurpose content-case-study content-refresh launch-local-seo launch-lead-triage-agent asd-ste100-writing
```

## PPC pack

Three skills that show a small business which ads and visits bring customers, so the owner
spends only on what works and approves every change.

| Skill | What it gives the business |
|-------|----------------------------|
| [google-analytics](./google-analytics) | GA4 that counts leads, calls, bookings and sales once, with consent mode v2, clean UTMs and a one-minute weekly report |
| [google-ads](./google-ads) | Search campaigns for local services that pay only for searches that can become customers: structure, keywords, negatives, assets, bidding, a weekly check |
| [meta-ads](./meta-ads) | Facebook and Instagram ads from real jobs, with Pixel and Conversions API behind consent, honest creative and the right special ad category |

Install the pack:

```bash
npx skills add https://github.com/webrenew/skills --skill google-analytics google-ads meta-ads
```

The three skills share one event map, so GA4, Google Ads and Meta count the same leads. Each
names its Launch companions (landing page, lead capture, speed to lead, agent guardrails)
under "Related skills"; they are optional and come with the Launch pack.

## Skill Structure

Each skill starts with a `SKILL.md` file. Some packages also contain:

- **`AGENTS.md`** — Full guides, patterns, and checklists
- **`references/`** — Supporting rules and examples
- **`scripts/`** — Tools that support the skill

## Usage

Install one skill:

```bash
npx skills add https://github.com/webrenew/skills --skill accessibility-audit
```

Install all Webrenew skills:

```bash
npx skills add https://github.com/webrenew/skills --all
```

## License

Proprietary. Copyright Webrenew LLC. All rights reserved.
