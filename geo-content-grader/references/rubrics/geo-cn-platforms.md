---
name: geo-cn-platforms
description: Mainland platform fit rubric for DeepSeek, Doubao, Qwen, and Wenxin.
---

# GEO CN Platform Fit

Use this rubric only under `GEO Profile: cn_mainland`.

Platform scoring must not be a name-swapped checklist. Each platform score has two
parts:

| Component | Meaning |
|---|---|
| Content Fit | Does the article itself fit the platform's answer style? |
| Platform Verification | Can live or configured platform queries recognize the topic/entity consistently? |

If platform verification cannot run, mark it `Limited` and do not fabricate
platform evidence.

## Platform Weights

| Platform | Weight |
|---|---:|
| DeepSeek | 30% |
| Qwen / Tongyi Qianwen | 25% |
| Wenxin / ERNIE Bot | 25% |
| Doubao | 20% |

## DeepSeek

DeepSeek fit emphasizes reasoning, research-style synthesis, evidence chains, and
clear handling of uncertainty.

| Criterion | Points |
|---|---:|
| Clear thesis and conclusion | 20 |
| Source chain and attribution | 20 |
| Complex question coverage | 20 |
| Data and factual density | 15 |
| Transparent reasoning | 15 |
| Counterexamples, boundaries, limitations | 10 |

## Doubao

Doubao fit emphasizes plain-language explanations, practical scenarios, and short
answers that can be safely transformed into creator, customer-support, or daily
workflow outputs.

| Criterion | Points |
|---|---:|
| Plain Chinese explanation | 25 |
| Scenario-based framing | 20 |
| Short answer extractability | 20 |
| Actionable steps | 15 |
| Rewrite/creation friendliness | 10 |
| Conversational but accurate tone | 10 |

## Qwen / Tongyi Qianwen

Qwen fit emphasizes workplace reuse, structured summaries, table/list extraction,
documents, PPT outlines, and enterprise context.

| Criterion | Points |
|---|---:|
| Structure and hierarchy | 25 |
| Workplace reuse value | 20 |
| Summary friendliness | 15 |
| Tables, lists, frameworks | 15 |
| Multimodal expansion potential | 10 |
| Enterprise/industry context accuracy | 15 |

## Wenxin / ERNIE Bot

Wenxin fit emphasizes Chinese knowledge QA, Baidu ecosystem discoverability,
encyclopedic expression, source authority, freshness, and entity clarity.

| Criterion | Points |
|---|---:|
| Chinese knowledge QA fit | 25 |
| Baidu/encyclopedic expression | 20 |
| Authoritative source and freshness | 20 |
| Entity clarity | 15 |
| Chinese writing standard | 10 |
| Multimodal support | 10 |

## Evidence Rules

Platform verification evidence must include:

- platform
- query
- capture timestamp
- response status
- source references, internal evidence records, or cited URLs when available
- extracted entity claims
- confidence: `High / Medium / Low`

For mainland article scoring, raw URLs do not need to be visible in the published
article body. Missing source/evidence/capture timestamp means the result is not
factual evidence and may be reported only as model interpretation.
