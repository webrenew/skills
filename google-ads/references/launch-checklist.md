# Google Ads launch checklist

Every item passes, or the owner accepts the risk in writing, before the first campaign is
enabled.

## Account and access

- [ ] The owner's Google account is an admin of the Google Ads account and holds the billing.
- [ ] The agency manager account is linked with the access level the owner approved.
- [ ] Advertiser verification is complete, or started, if Google asks for it.
- [ ] Auto-applied recommendations are off.

## Tracking

- [ ] GA4 is linked, auto-tagging is on (`google-analytics`, step 6).
- [ ] Each result (lead, booking, purchase, call from ads) has one primary conversion action,
  with a value where the owner gave one.
- [ ] A test lead from an ad-style URL (`?gclid=test`) is stored with its `gclid`
  (`launch-lead-capture`), then deleted.
- [ ] Enhanced conversions are on if consent allows it.
- [ ] Consent mode is in place for regions that need it.

## Campaign settings

- [ ] Networks: Search only. Search Partners off, Display off.
- [ ] Locations: the service area. Option: presence only. Exclusions added.
- [ ] Languages: the languages the business answers in.
- [ ] Ad schedule matches answered hours for call-heavy campaigns.
- [ ] Budget matches the owner's approved monthly number / 30.4.
- [ ] Bid strategy: Maximize clicks with a CPC limit, or Manual CPC, at the start.

## Keywords and ads

- [ ] Each ad group has one theme and its own landing page.
- [ ] Phrase and exact match at the start. No broad match without Smart Bidding.
- [ ] Account-level negative list attached.
- [ ] One or two responsive search ads per ad group, with the town, the proof, the offer and
  the action. Every claim is true and on the landing page.
- [ ] Assets: call, location, 4+ sitelinks, 4+ callouts, structured snippet, name and logo.

## Landing pages

- [ ] Each page loads fast on a phone and passes `launch-landing-page`'s audit.
- [ ] The headline matches the ad group's theme.
- [ ] Phone number and form work on production.

## Approval

- [ ] The owner approved the plan: campaigns, budgets, bid strategy, keywords, ads and
  locations. The approval is stored with the date.
- [ ] A daily spend alert is set (Google Ads rules or a scheduled job).
