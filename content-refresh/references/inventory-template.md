# Inventory Template

## Search Console steps

1. Performance > Search results. Date: last 3 months; compare to the previous 3 months (or
   the same 3 months last year for seasonal businesses).
2. Pages tab. Filter Page "contains" `/blog/`. Export.
3. For each post that matters, click the page, then the Queries tab: note the top 3 queries
   and any question the post does not answer.
4. Indexing > Pages: note any post that is "Crawled - currently not indexed" or "Duplicate
   without user-selected canonical". These are candidates to merge or improve.

## Leads and calls by post

- Leads: count leads whose stored landing page or UTM data points to the post. If leads do
  not store the landing page yet, add it next to `utm` in the lead record
  (`launch-lead-capture`, section 8) and start counting from that date.
- Calls: count `Call Clicked` events with the post's path (`vercel-marketing-analytics`).
- Channel posts: leads with `utm_campaign` equal to the post slug, or with `utm_campaign=gbp`
  and `utm_content` equal to the post slug (Google Business Profile posts), came from
  repurposed posts (`content-repurpose`).

## Sheet

```csv
"slug","title","hub","published","updated","leads","calls","clicks","clicks_prev","impressions","position","top_queries","ai_cited","stale_facts","decision","notes"
"water-heater-leaking-from-bottom","Water heater leaking from the bottom?","/services/water-heaters","2026-03-04","2026-03-04","5","8","410","300","9800","6.1","water heater leaking from bottom; leaking water heater repair","perplexity","none","keep",""
"tankless-vs-tank","Tankless vs tank water heater","/services/water-heaters","2025-02-10","2025-02-10","1","2","120","260","7400","14.3","tankless vs tank cost","none","2025 prices","refresh","Add 2026 price guide and a Summerville job"
```

## Decision guide

| Signal | Likely decision |
|---|---|
| Leads or calls > 0 | Keep or refresh, never remove. This row wins over every other row. |
| Clicks down > 30 % and position down | Refresh |
| Two posts share their top query | Merge into the one with more leads |
| Not indexed, no leads, no calls, no links, 12+ months old | Remove with a redirect |
| Facts out of date (prices, years, models, rules) | Refresh, whatever the traffic |
