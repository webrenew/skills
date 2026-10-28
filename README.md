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
| [vercel-marketing-analytics](./vercel-marketing-analytics) | Vercel Analytics event strategy — user journeys, funnels, CTA tracking, lead generation, and conversion measurement |
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
