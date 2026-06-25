---
name: geo-cn-entity
description: Mainland brand and entity consistency rubric.
---

# GEO CN Brand Entity Consistency

Use this rubric under `GEO Profile: cn_mainland` when the article discusses a
brand, company, product, founder, organization, app, account, or institution.

## Dimensions

| Dimension | Weight |
|---|---:|
| Entity Extraction Clarity | 25% |
| On-Article Fact Consistency | 25% |
| Mainland Public-Source Consistency | 35% |
| Citation / Attribution Support | 15% |

## Entity Facts To Extract

- Chinese full legal name
- English name, pinyin name, or abbreviation
- brand name
- product names and versions
- official domain
- unified social credit code
- ICP filing subject
- app developer or publisher
- mini-program or WeChat official account verification subject
- legal representative, founder, or leadership when relevant
- headquarters or operating region
- license, permit, certification, or filing number
- founding, launch, publication, or update dates

## Mainland Source Priority

Prefer:

1. Official website
2. ICP filing or app filing records
3. National enterprise credit records or licensed commercial APIs
4. Official app stores and developer pages
5. Verified WeChat official accounts
6. Regulatory, association, exchange, or government pages
7. Baidu Baike and mainstream media as public secondary sources
8. Community platforms only as observed public perception

## Output Requirements

Report:

- extracted entities and claims
- evidence table: `Claim | Article | Source | State | Notes`
- data availability: `High / Medium / Low`
- conflicts and unresolved facts
- recommended wording fixes

Never invent unavailable mainland records. Mark them `Limited`.
