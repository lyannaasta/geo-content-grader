---
name: geo-cn-citability
description: Chinese mainland AI citability rubric for zh-CN content under the cn_mainland profile.
---

# GEO CN Citability

Use this rubric only when `GEO Profile: cn_mainland` is selected or auto-detected.

The original citability dimensions remain unchanged:

| Dimension | Weight |
|---|---:|
| Answer Block Quality | 30% |
| Passage Self-Containment | 25% |
| Structural Readability | 20% |
| Statistical Density | 15% |
| Uniqueness & Original Data | 10% |

## Mainland Chinese Adaptation

Do not score Chinese article passages by English word-count thresholds. Score them
by Chinese character length, sentence count, entity explicitness, source traceability,
and extractable answer structure.

### Passage Length

| Level | Chinese Character Length |
|---|---:|
| Optimal | 120-350 Chinese characters |
| Acceptable | 80-500 Chinese characters |
| Weak | under 80 or over 500 Chinese characters |

Characters mean CJK characters plus full-width punctuation. Numbers, Latin brand
names, and policy codes are preserved as evidence signals but do not drive the
length threshold alone.

### Answer-First Patterns

High-scoring sections open with 1-2 sentences that directly answer the heading:

- `X 是...`
- `X 指...`
- `X 适用于...`
- `X 和 Y 的区别在于...`
- `判断 X 是否合规，关键看...`
- `选择 X 时，应优先看...`

### Self-Containment

A Chinese paragraph is self-contained when it names the subject explicitly and can
be quoted without nearby context. Penalize heavy use of:

- `它`
- `这个`
- `该平台`
- `上述`
- `这些`
- `相关`

These are not always wrong, but high-citability paragraphs should repeat the
important entity name when the passage may be extracted alone.

### Statistical Density

Count mainland-relevant factual markers:

- RMB amounts: `199 元`, `3.5 万元`, `¥999`
- Dates and years: `2026 年 6 月 24 日`, `2024 年`
- Percentages and ratios
- Mainland locations: province, city, district
- Policy names and issuing bodies
- Standard numbers: `GB/T`, `GB`, `JR/T`, `YY/T`
- Registration and filing identifiers: `ICP备`, `统一社会信用代码`, `许可证编号`
- Named authorities: ministries, regulators, courts, exchanges, standards bodies

### Structure

Prefer:

- Question headings
- Definition paragraphs
- Tables for comparisons
- Ordered lists for steps
- Unordered lists for options
- FAQ blocks for real user questions
- `适用 / 不适用 / 风险 / 证据` style matrices

## Output Requirements

For cn_mainland reports, include:

- `Chinese AI Citability Score: XX/100`
- `Profile: cn_mainland`
- strongest extractable Chinese passages
- weakest passages and concrete rewrite suggestions
- confidence and evidence availability
