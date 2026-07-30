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
| [cms-integration](./cms-integration) | Headless CMS integration patterns — Sanity, Contentful, Payload, draft mode, ISR webhooks, TypeScript codegen |
| [vercel-marketing-analytics](./vercel-marketing-analytics) | Vercel Analytics event strategy — user journeys, funnels, CTA tracking, lead generation, and conversion measurement |
| [asd-ste100-writing](./asd-ste100-writing) | Clear product copy with ASD-STE100 Simplified Technical English and benefit-first framing |

## Skill Structure

Each skill starts with a `SKILL.md` file. Some packages also contain:

- **`AGENTS.md`** — Full guides, patterns, and checklists
- **`references/`** — Supporting rules and examples
- **`scripts/`** — Tools that support the skill

## Usage

Install one skill:

```bash
npx skills add https://github.com/webrenew/skills --skill cms-integration
```

Install all Webrenew skills:

```bash
npx skills add https://github.com/webrenew/skills --all
```

## License

Proprietary. Copyright Webrenew LLC. All rights reserved.
