---
name: geo-cn-source-authority
description: Mainland China source authority tiers for GEO scoring.
---

# GEO CN Source Authority

Use this source ladder under `GEO Profile: cn_mainland`.

| Tier | Source Types | Use |
|---|---|---|
| S | State Council, ministries, regulators, courts, national standards, exchanges | Highest factual authority |
| A | Official site, listed-company disclosure, university, research institute, tier-3 hospital, industry association, central state media | Strong factual support |
| B | Mainstream media, verified WeChat official account, Baidu Baike, company whitepaper, leading industry media | Useful public support |
| C | Zhihu, Xiaohongshu, Bilibili, Douyin, forums, community discussion | User questions, sentiment, use cases |
| D | Scraper sites, rewritten article farms, anonymous soft ads, low-quality AI aggregates | Weak or non-supportive |

## Scoring Rules

- High-risk claims should use S/A sources.
- B sources can support general background but should not override official records.
- C sources can reveal user language, objections, and scenarios, but should not
  prove medical, financial, legal, registration, or qualification facts.
- D sources do not improve trust and may reduce confidence.
- When sources conflict, preserve the conflict in the report instead of averaging
  it away.

## Evidence States

| State | Meaning |
|---|---|
| Verified | Confirmed by S/A or official source |
| Observed | Seen in public or platform sources but not authoritative |
| Conflicting | Sources disagree |
| Limited | Not enough accessible evidence |
