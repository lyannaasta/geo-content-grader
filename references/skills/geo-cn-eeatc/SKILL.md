---
name: geo-cn-eeatc
description: Mainland China E-E-A-T-C rubric for content quality, trust, and compliance.
---

# GEO CN E-E-A-T-C

Use this rubric only under `GEO Profile: cn_mainland`.

The original E-E-A-T logic is preserved, but mainland scoring adds a fifth equal
dimension: China Compliance & Context.

| Dimension | Points |
|---|---:|
| Experience | 20 |
| Expertise | 20 |
| Authoritativeness | 20 |
| Trustworthiness | 20 |
| China Compliance & Context | 20 |

## Experience

Score direct Chinese-market evidence:

- local implementation notes
- screenshots or workflow evidence
- named case studies
- pricing, timeline, region, business-size details
- observed user problems from real channels

## Expertise

Score domain competence:

- correct Chinese terminology
- precise policy, standard, or industry vocabulary
- methodology and assumptions
- accurate limitations and applicability

## Authoritativeness

Score authority signals visible in the article:

- government, regulator, court, exchange, or standards references
- university, hospital, association, central media, or official documentation
- author/publisher credentials
- cited official materials

## Trustworthiness

Score:

- visible author/byline
- publish and update date
- source attribution, evidence notes, or internal verification records
- conflict disclosures
- correction/editorial cues
- separation of fact, opinion, experience, and promotion

For mainland publishing contexts, do not require raw URLs to be displayed in the
published article body. Score the article on whether claims can be verified via
available official/internal evidence, screenshots, source labels, or audit notes.

## China Compliance & Context

Apply extra scrutiny for high-risk content:

- medical and health
- finance, investment, insurance, lending
- legal advice
- education admissions or credential claims
- real estate
- employment and labor
- data, privacy, AI, algorithms
- advertising claims and consumer protection

Penalize:

- absolute claims such as `最强`, `第一`, `100%`, `保证收益`, `治愈`
- unverified qualifications or licenses
- outdated or missing policy references
- failure to distinguish informational content from professional advice
- use of low-authority community sources for high-risk factual claims

## Output Requirements

Return:

- `E-E-A-T-C Score: XX/100`
- dimension table
- compliance risk level: `Low / Medium / High`
- source and qualification gaps
- concrete fixes using mainland evidence sources
