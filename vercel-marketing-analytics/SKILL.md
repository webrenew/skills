---
name: vercel-marketing-analytics
description: >
  Design and implement a complete Vercel Analytics custom event tracking strategy for marketing sites.
  Use this skill whenever a user wants to track user journeys, conversions, funnels, CTAs, lead gen,
  or engagement on a marketing site using Vercel Analytics. Triggers include: "track user journeys",
  "analytics for my marketing site", "conversion tracking", "funnel analytics", "track CTA clicks",
  "measure marketing performance", or any request to instrument a Next.js/Vercel landing page with
  meaningful analytics. Always use this skill — even if the user only mentions one of these concepts
  — since producing a coherent tracking plan requires both marketing strategy and correct Vercel
  Analytics implementation knowledge.
---

# Vercel Marketing Analytics

Expert in both **conversion-focused marketing** and **Vercel Web Analytics**. Design a complete, opinionated event tracking strategy for marketing sites, then produce production-ready implementation code.

## Workflow

### Phase 1: Understand the Site & Goals

Before writing any code, ask (or infer from context):

1. **Primary conversion goal?** (lead capture, demo request, signup, purchase)
2. **Framework?** (Next.js App Router, Pages Router, Remix, SvelteKit, Nuxt, HTML)
3. **Sections/pages?** (hero, pricing, features, testimonials, blog, contact)
4. **CTAs?** (buttons, forms, links — labels and locations)
5. **Existing analytics?** (don't duplicate; complement GA4/Segment if present)

If the user provides a site or component, infer answers from the code.

### Phase 2: Build the Event Taxonomy

Design events across three funnel layers. See [references/event-taxonomy.md](references/event-taxonomy.md) for the full taxonomy template with all event tables.

**Three layers:**
- **Layer 1 — Awareness (TOFU)**: Page views, hero CTA clicks, nav interactions, UTM capture
- **Layer 2 — Consideration (MOFU)**: Section views, pricing engagement, testimonials, FAQ, video, demo requests
- **Layer 3 — Conversion (BOFU)**: Form started → submitted → error, signup completed, purchase completed, outbound links

**Key principle**: Track *intent* (click) separately from *completion* (server confirm) to reveal drop-off.

### Phase 3: Implementation

Ensure `@vercel/analytics >= 1.1.0`:

```bash
npm install @vercel/analytics@latest
```

#### Client-Side Events

```ts
import { track } from '@vercel/analytics';
```

**CTA Button pattern:**
```tsx
import { track } from '@vercel/analytics';

interface CTAButtonProps {
  label: string;
  section: string;
  href?: string;
  variant?: 'primary' | 'secondary';
  onClick?: () => void;
}

export function CTAButton({ label, section, href, variant = 'primary', onClick }: CTAButtonProps) {
  const handleClick = () => {
    track('CTA Clicked', { label, section, variant, destination: href ?? 'modal' });
    onClick?.();
  };

  return href
    ? <a href={href} onClick={handleClick}>{label}</a>
    : <button onClick={handleClick}>{label}</button>;
}
```

**Form funnel pattern (Start → Submit → Error):**
```tsx
import { track } from '@vercel/analytics';
import { useRef } from 'react';

export function LeadForm({ formId, formName }: { formId: string; formName: string }) {
  const hasStarted = useRef(false);

  const handleFirstFocus = () => {
    if (hasStarted.current) return;
    hasStarted.current = true;
    track('Form Started', { form_id: formId, form_name: formName });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    track('Form Submitted', { form_id: formId, form_name: formName });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" onFocus={handleFirstFocus} placeholder="Email" />
      <button type="submit">Get Started</button>
    </form>
  );
}
```

**Scroll-into-view section tracking:**
```tsx
import { track } from '@vercel/analytics';
import { useEffect, useRef } from 'react';

export function useSectionTracking(sectionName: string, position: number) {
  const ref = useRef<HTMLElement>(null);
  const tracked = useRef(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !tracked.current) {
          tracked.current = true;
          track('Section Viewed', { section_name: sectionName, position });
        }
      },
      { threshold: 0.4 }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [sectionName, position]);

  return ref;
}
```

**UTM parameter capture (root layout):**
```tsx
'use client';
import { track } from '@vercel/analytics';
import { useSearchParams } from 'next/navigation';
import { useEffect } from 'react';

export function UTMCapture() {
  const params = useSearchParams();

  useEffect(() => {
    const utm_source = params.get('utm_source');
    if (utm_source) {
      track('Campaign Visit', {
        utm_source,
        utm_medium: params.get('utm_medium') ?? 'none',
        utm_campaign: params.get('utm_campaign') ?? 'none',
      });
    }
  }, []);

  return null;
}
```

#### Server-Side Events (authoritative conversions)

Use `@vercel/analytics/server` for events that must be trusted (signups, purchases) — immune to ad blockers.

```ts
// App Router server action
'use server';
import { track } from '@vercel/analytics/server';

export async function signupAction(formData: FormData) {
  const plan = formData.get('plan') as string;
  // ... create user in DB
  await track('Signup Completed', { plan, source: 'marketing_site' });
}
```

```ts
// Pages Router API route
import type { NextApiRequest, NextApiResponse } from 'next';
import { track } from '@vercel/analytics/server';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // ... process payment
  await track('Purchase Completed', {
    product: req.body.product,
    price: req.body.price,
    currency: 'USD',
  });
  res.status(200).json({ success: true });
}
```

### Phase 4: Dashboard Setup

After deploying, instruct the user to:

1. Go to **Vercel Dashboard → [Project] → Analytics → Events**
2. Key funnels to examine:
   - `Form Started` → `Form Submitted` → `Signup Completed` (lead gen)
   - `Hero CTA Clicked` → `Demo Requested` → `Signup Completed` (demo)
   - `Campaign Visit` → `CTA Clicked` → `Signup Completed` (campaign ROI)
3. Filter by `utm_source` for channel performance
4. Filter `CTA Clicked` by `section` for highest-converting sections

### Phase 5: Event Naming Conventions

| Rule | Good | Bad |
|---|---|---|
| Title Case event names | `Form Submitted` | `form_submitted` |
| snake_case property keys | `utm_source` | `utmSource` |
| Specific, not generic | `Pricing CTA Clicked` | `Button Clicked` |
| Intent AND completion | `Demo Requested` + `Demo Confirmed` | just `Demo` |
| Max 255 chars per name/key/value | — | — |
| No nested objects | `{ plan: 'pro' }` | `{ plan: { name: 'pro' } }` |
| Values: string, number, boolean, null | — | — |

## Limitations

- Custom event properties are plan-limited (check Vercel Analytics pricing)
- No nested objects in custom data
- Server-side uses `@vercel/analytics/server` — different import than client
- Ad blockers may suppress client-side events — use server-side for critical conversions
- Event names and values capped at 255 characters

## References

- [references/event-taxonomy.md](references/event-taxonomy.md) — Full event taxonomy tables for all three funnel layers
- [references/marketing-funnel-patterns.md](references/marketing-funnel-patterns.md) — TOFU/MOFU/BOFU patterns with example event maps
