# GA4 verification checklist

Run it after the install, after any change to the tag, the banner or a form, and once a
quarter. Use the production site in a normal browser window, with ad blockers off.

## Tag

- [ ] Tag Assistant shows **one** Google tag with the right Measurement ID on each page type
  (home, service page, blog post, form page, thank-you page).
- [ ] No second GA4 path: no GTM container with GA4, no plugin, no hard-coded snippet.
- [ ] One `page_view` per route change on client-side navigation (watch Tag Assistant while
  you click three internal links).
- [ ] Preview and staging deployments send nothing to the production property.

## Consent

- [ ] In Tag Assistant, the **Consent** tab shows the default (`denied` where the banner
  asks) **before** the first hit.
- [ ] After **Accept**, the update shows `granted` for the accepted categories.
- [ ] After **Reject**, nothing changes to `granted`, and in basic mode no GA4 request leaves
  the browser (DevTools, Network, filter `collect`).
- [ ] A return visit applies the stored choice without asking again.

## Events

For each key event, perform the real action once on production:

- [ ] `generate_lead`: submit the form with a test name. The event appears once in DebugView
  after the success message, never after a failed submit.
- [ ] `call_click`: tap each `tel:` link (header, sticky bar, footer). One event per tap.
- [ ] `book_appointment`: complete a test booking. One event per booking.
- [ ] `purchase`: complete a test payment. One event, with `transaction_id`, `value`,
  `currency`. Refresh the thank-you page: no second event.
- [ ] Each key event is marked as a key event in Admin.
- [ ] The test leads, bookings and payments are deleted or marked as tests afterwards.

## Privacy

- [ ] No event parameter, page path or page title in DebugView contains a name, email, phone
  or address.
- [ ] Forms use `POST`. No personal data appears in any URL after submit.
- [ ] Data redaction is on for email and the query parameters the site uses.

## Admin

- [ ] Data retention is 14 months.
- [ ] Internal traffic filter is **Active**, not Testing.
- [ ] Unwanted referrals list the payment and booking domains.
- [ ] Google Ads link exists, auto-tagging is on, and each result has one primary conversion
  source in Google Ads.
- [ ] Search Console link exists.
- [ ] The owner's account is an Administrator. Ex-staff and old agencies are removed.

## Report

Write the result as a table: check, pass or fail, and the fix. Attach the DebugView or Tag
Assistant notes for each event.
