# Marketing Funnel Patterns

Common event tracking patterns for different marketing site archetypes.

## SaaS Landing Page

**Goal**: Free trial signup or demo booking

```
TOFU: Page Viewed → Hero CTA Clicked → Nav Link Clicked
MOFU: Section Viewed (features) → Pricing Plan Viewed → Demo Requested
BOFU: Form Started → Form Submitted → Signup Completed
```

**Key funnels to measure:**
- Hero CTA → Signup (direct conversion rate)
- Pricing viewed → Plan selected → Signup (pricing effectiveness)
- Demo Requested → Demo Completed → Signup (sales-assisted conversion)

## Lead Generation Site

**Goal**: Contact form submission or consultation booking

```
TOFU: Campaign Visit → Page Viewed → Hero CTA Clicked
MOFU: Section Viewed (services) → Testimonial Viewed → FAQ Expanded
BOFU: Form Started → Form Submitted → Lead Qualified (server-side)
```

**Key funnels to measure:**
- Campaign Visit → Form Submitted (campaign ROI by utm_source)
- Form Started → Form Submitted (form completion rate)
- Page sections viewed → Form Started (content that drives action)

## E-commerce / Product Launch

**Goal**: Purchase or pre-order

```
TOFU: Campaign Visit → Page Viewed → Hero CTA Clicked
MOFU: Section Viewed (product details) → Video Played → Feature Compared
BOFU: Add to Cart → Checkout Started → Purchase Completed
```

**Key funnels to measure:**
- Video Played → Purchase (video influence on conversion)
- Feature Compared → Purchase (comparison shopping behavior)
- Add to Cart → Purchase (checkout drop-off)

## Content / Blog-Driven

**Goal**: Newsletter signup or content-to-product conversion

```
TOFU: Blog Post Viewed → Campaign Visit → Nav Link Clicked
MOFU: Section Viewed (related posts) → Outbound Link Clicked
BOFU: Form Started (newsletter) → Form Submitted → Signup Completed
```

**Key funnels to measure:**
- Blog Post Viewed → Newsletter Signup (content conversion)
- Blog → Product Page → Signup (content-to-product pipeline)
- Category breakdown of converting posts

## Event Mapping Checklist

For any marketing site, ensure you track:

- [ ] At least one TOFU event (how users arrive)
- [ ] At least two MOFU events (what users engage with)
- [ ] Form Started + Form Submitted (form funnel)
- [ ] Server-side conversion event (ad-blocker-proof)
- [ ] UTM parameter capture (campaign attribution)
- [ ] CTA clicks with section context (highest-converting areas)
