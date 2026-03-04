# Event Taxonomy Template

Use these tables as a starting point for each project. Customize events based on the site's actual sections, CTAs, and conversion goals.

## Layer 1 — Awareness (Top of Funnel)

What brings users in and what do they first engage with?

| Event | When | Custom Data |
|---|---|---|
| `Page Viewed` | On route load | `{ page, referrer, utm_source, utm_medium, utm_campaign }` |
| `Hero CTA Clicked` | Primary hero button | `{ label, variant }` |
| `Nav Link Clicked` | Navigation interaction | `{ destination, label }` |
| `Blog Post Viewed` | Article pages | `{ title, category, read_time }` |
| `Campaign Visit` | UTM params present | `{ utm_source, utm_medium, utm_campaign }` |

## Layer 2 — Consideration (Mid Funnel)

Are users engaging deeply with the value proposition?

| Event | When | Custom Data |
|---|---|---|
| `Section Viewed` | Section scrolled into view | `{ section_name, position }` |
| `Pricing Plan Viewed` | Pricing section engagement | `{ plan_name }` |
| `Testimonial Viewed` | Social proof section | `{ index }` |
| `FAQ Expanded` | Accordion/FAQ opens | `{ question }` |
| `Video Played` | Explainer/demo video | `{ title, duration }` |
| `Demo Requested` | Demo CTA clicked | `{ source_section }` |
| `Feature Compared` | Toggle/tab on features | `{ feature_name, plan }` |

## Layer 3 — Conversion (Bottom of Funnel)

Did they convert? Where did they drop off?

| Event | When | Custom Data |
|---|---|---|
| `Form Started` | User focuses first field | `{ form_id, form_name }` |
| `Form Submitted` | Form submit fired | `{ form_id, form_name, field_count }` |
| `Form Error` | Validation/submit failure | `{ form_id, error_type }` |
| `Signup Completed` | Server confirms account | `{ plan, source }` |
| `Purchase Completed` | Server confirms order | `{ product, price, currency }` |
| `Outbound Link Clicked` | External link | `{ url, label, section }` |

## Blank Template

Copy this table and fill in project-specific events:

| Event | When | Custom Data |
|---|---|---|
| | | |
| | | |
| | | |
| | | |
