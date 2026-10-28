---
name: launch-site-checklist
description: >
  Run a go-live check on a small business website before launch or after a redesign, and
  report what passes, what fails and what the owner must do. Use this skill when the user
  says launch, go live, ship the site, cut over DNS, replace the old site, pre-launch
  checklist, or "is the site ready". Covers domain and HTTPS, redirects from the old site,
  forms that deliver, analytics and consent, search basics, speed, accessibility, legal pages
  and account ownership.
---

# Launch Checklist: Go Live Without Losing Leads or Rankings

**RULE: Test every path a customer uses to reach the business, on the production domain,
after DNS points at the new site. A check run on a preview URL proves nothing about launch.**

The most expensive launch bugs are silent: a form that sends to nowhere, a `noindex` left
from staging, old URLs that now return 404. Each one costs leads for weeks before anyone
notices. This checklist finds them on day one.

## How to run it

1. Work through the sections in order. Run the commands where shown.
2. Mark each item **PASS**, **FAIL** (with the fix) or **OWNER** (needs the owner's access or
   decision).
3. Fix every FAIL before you call the launch done. Send the OWNER list to the owner.

Set the domain once:

```bash
SITE=example.com
```

## 1. Domain and HTTPS

```bash
curl -sI "http://$SITE"       | grep -iE '^(HTTP|location)'
curl -sI "http://www.$SITE"   | grep -iE '^(HTTP|location)'
curl -sI "https://www.$SITE"  | grep -iE '^(HTTP|location)'
curl -sI "https://$SITE"      | grep -iE '^(HTTP|strict-transport-security)'
```

- [ ] Every variant reaches **one** canonical origin (apex or www) with one 301/308 hop.
- [ ] HTTPS works on both apex and www, and the certificate is valid.
- [ ] `Strict-Transport-Security` is set on the canonical origin.
- [ ] Email still works after the DNS change: MX, SPF, DKIM and DMARC records are unchanged
  or deliberately moved. A DNS cut-over that drops MX records stops the owner's email.

## 2. Redirects from the old site

Old URLs carry the rankings and the links that other sites point at.

- [ ] Get the old URL list: the old `sitemap.xml`, Search Console's indexed pages, and the top
  landing pages in analytics for the last 12 months.
- [ ] Map each old URL to the closest new page with a permanent redirect. Send a URL to the
  home page only when no equivalent exists.
- [ ] Check the map:

```bash
while read -r path; do
  first=$(curl -s -o /dev/null -w '%{http_code}' "https://$SITE$path")
  final=$(curl -sL -o /dev/null -w '%{num_redirects} %{http_code} %{url_effective}' "https://$SITE$path")
  echo "$path  first=$first  hops/final=$final"
done < old-paths.txt
```

Every line must show `first=301` or `308`, exactly **1** hop, and a final `200`. More than
one hop is a chain; fix it to point straight at the final URL.

## 3. Every contact path delivers

- [ ] Submit each form on production with a real entry, using an inbox you control. Confirm
  that the lead is stored, that the owner gets the alert, and that the confirmation arrives.
  Then set `isTest = true` on that lead so it stays out of every count and report.
- [ ] Every phone number is a `tel:` link and dials the right number on a phone.
- [ ] Booking and payment links open the live (not test) calendar or checkout.
- [ ] The confirmation message says what happens next and when.

See `launch-lead-capture` for how forms should store and deliver leads.

## 4. Search basics

```bash
curl -s "https://$SITE/robots.txt"
curl -s "https://$SITE/" | grep -ioE '<meta[^>]+name="robots"[^>]*>|<link[^>]+rel="canonical"[^>]*>|<title>[^<]*'
curl -sI "https://$SITE/" | grep -i '^x-robots-tag'      # a header can say noindex too
curl -s "https://$SITE/sitemap.xml" | head -20
```

- [ ] **No `noindex`** on production pages, in the robots meta tag **or** the `X-Robots-Tag`
  header, and `robots.txt` does not `Disallow: /`. This is
  the most common launch bug: a staging setting that ships.
- [ ] Each page has a unique title and meta description.
- [ ] Canonical URLs point at the canonical origin from section 1.
- [ ] `sitemap.xml` lists the live pages. Submit it in Search Console.
- [ ] Social share preview works (Open Graph title, description and image).
- [ ] Favicon and app icons load.
- [ ] Local business details are correct (see `launch-local-seo`).

## 5. Analytics and consent

- [ ] Analytics records a page view on production, from a real browser.
- [ ] The key conversion events fire once, only after success: lead submitted, booking made,
  call link clicked, purchase.
- [ ] A consent banner appears where the law needs one (for example EU, UK, California for
  some trackers), and declining blocks the trackers it covers.
- [ ] Search Console is verified for the canonical origin.

## 6. Speed on a phone

Run PageSpeed Insights (mobile) on the home page and the main landing page.

- [ ] Core Web Vitals targets at the 75th percentile: **LCP under 2.5 s, INP under 200 ms, CLS
  under 0.1**. Lab scores are a guide; field data arrives after about 28 days of traffic.
- [ ] Hero images are sized and compressed. No autoplay carousel above the fold.

Use `website-speed-optimization` for fixes.

## 7. Accessibility quick pass

- [ ] You can reach and use every link, button and form field with the keyboard only, and
  focus is always visible.
- [ ] Images that carry meaning have alt text; decorative images have `alt=""`.
- [ ] Each form field has a visible label.
- [ ] Text contrast meets WCAG AA (4.5:1 for body text).

Use `accessibility-audit` for a full audit.

## 8. Legal pages

- [ ] A privacy policy that names the tools the site actually uses (analytics, forms, chat,
  ad pixels) and how to contact the business.
- [ ] Terms, refund or cancellation policy where the site takes payments or bookings.
- [ ] Business name and contact details are easy to find.

## 9. The owner owns the accounts

Agencies and freelancers leave. The owner must keep access.

- [ ] **OWNER** has admin access to: domain registrar, DNS, hosting, analytics, Search Console,
  Google Business Profile, the form or CRM tool, email sending, and payment accounts.
- [ ] Login details are in the owner's password manager, not only in a contractor's.
- [ ] Renewal dates for the domain and paid tools are known, with auto-renew on.

## 10. After launch

- [ ] Uptime monitoring and an alert when a form fails (see `launch-site-health-report`).
- [ ] Re-check Search Console for crawl errors and 404s after 7 days and after 28 days.
- [ ] Keep the old site's content export for at least 90 days.

## Output

```
## Launch report for example.com: 41 PASS, 3 FAIL, 4 OWNER

### Fix before launch
| Item | Problem | Fix |

### Owner actions
1. Plain-language step, with the link to where they do it.

### Passed
Short list grouped by section.
```
