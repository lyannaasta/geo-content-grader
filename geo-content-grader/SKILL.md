---
name: geo-content-grader
description: Use when scoring, auditing, or improving an article for GEO, AI search visibility, AI citation readiness, LLM answer extraction, ChatGPT/Claude/Perplexity/Gemini/DeepSeek/Doubao/Qwen/Wenxin discoverability, article GEO content scoring, or "文章 GEO 打分". Runs an article-first GEO scorecard with selectable global_default and cn_mainland profiles while keeping citability, content, platform, source/compliance, and brand/entity checks separate.
---

# GEO Content Grader

Use this skill when the user wants to score an article, draft, page, or content brief for Generative Engine Optimization (GEO): the likelihood that AI search systems can understand, extract, trust, cite, and recommend the article.

This is a Codex-native article scoring entrypoint around this skill package. It supports two scoring profiles:

| GEO Profile | Use |
|---|---|
| `global_default` | Original global/English-oriented GEO logic with Google AI Overviews, ChatGPT Search, Perplexity, Gemini, and Bing Copilot. |
| `cn_mainland` | Mainland China logic with Chinese citability thresholds, E-E-A-T-C, DeepSeek, Doubao, Qwen/Tongyi Qianwen, Wenxin/ERNIE Bot, mainland source authority, and mainland entity verification. |

If the user specifies a profile, use that profile. If not specified, auto-detect:

- Use `cn_mainland` when the article is primarily simplified Chinese, discusses mainland companies/products/policies, uses RMB, ICP/filing/licensing signals, mainland cities/provinces, or mainland regulatory context.
- Use `global_default` for English/global content unless the user asks otherwise.

Reference the local scoring materials first:

- `profiles/global_default.yaml`
- `profiles/cn_mainland.yaml`
- `references/rubrics/geo-citability.md`
- `references/rubrics/geo-content.md`
- `references/rubrics/geo-platform-optimizer.md`
- `references/rubrics/geo-brand-mentions.md`
- `references/rubrics/geo-cn-citability.md`
- `references/rubrics/geo-cn-eeatc.md`
- `references/rubrics/geo-cn-platforms.md`
- `references/rubrics/geo-cn-source-authority.md`
- `references/rubrics/geo-cn-entity.md`
- `references/scripts/citability_scorer.py`
- `references/scripts/evidence_adapters.py`
- `references/scripts/source_evidence.py`

Do not require Claude Code or `~/.claude`. Do not use Claude slash commands. Treat the files above as local references and reusable scoring logic.

## Scope

This skill scores the article itself. It intentionally excludes full-site GEO infrastructure unless the signal can be evaluated from the article or the article page.

Include:

| Source Module | Include? | Article-First Scope |
|---|---:|---|
| `/geo citability` | Yes | Keep as an independent AI Citability scorecard. |
| `/geo content` | Yes | Keep as an independent E-E-A-T scorecard for `global_default`; use E-E-A-T-C for `cn_mainland`. Fold only article-visible Article/Author/Date schema-equivalent signals here. |
| `/geo platforms` | Partial | Keep as an independent AI Platform Fit scorecard. Load the platform set from the selected profile. |
| `/geo brand-mentions` | Partial | Keep as an independent Brand Entity Consistency scorecard. Under `cn_mainland`, use mainland public-source verification states and evidence availability. |

Exclude:

| Source Module | Reason |
|---|---|
| `/geo audit` | Too broad; whole-site orchestration. |
| `/geo technical` | Technical crawl/render/performance checks are not article content scoring. |
| `/geo crawlers` | AI crawler access is site infrastructure. |
| `/geo llmstxt` | `llms.txt` is site-level AI navigation. |
| Full `/geo schema` | JSON-LD/template markup is not article text. Use only article-visible equivalents inside `/geo content`: author, credentials, publish date, updated date, FAQ/HowTo-like content, sources, and entity clarity. |

## Required Entrypoint Behavior

When the user provides one URL, local file, pasted draft, or article brief, run the article through these branches in order:

1. **Resolve GEO Profile**: explicit user choice first, otherwise auto-detect `global_default` or `cn_mainland`.
2. **Citability Branch**: use `/geo citability` for `global_default`; use `/geo-cn-citability` for `cn_mainland`.
3. **Content / E-E-A-T Branch**: use `/geo content` for `global_default`; use `/geo-cn-eeatc` for `cn_mainland`.
4. **Platform Content Fit Branch**: load the platform matrix from the selected profile.
5. **Source / Compliance Evidence Branch**: for `cn_mainland`, apply `/geo-cn-source-authority` and compliance evidence rules.
6. **Brand Entity Consistency Branch**: use `/geo brand-mentions` for `global_default`; use `/geo-cn-entity` and evidence states for `cn_mainland`.
7. **Final Article GEO Summary** combining the independent branch scores.

Keep the branch logic separate. Do not mix citability findings into the E-E-A-T score, do not mix platform preferences into the citability score, and do not let off-page brand authority dominate the article score.

## Evidence Gate

For `cn_mainland`, platform and entity verification must be evidence-based:

- Platform verification should use configured adapters when credentials exist: `references/scripts/evidence_adapters.py`.
- Public-source verification should fetch and classify source URLs when available: `references/scripts/source_evidence.py`.
- Mainland published articles do not need to display raw URLs in the body. For `cn_mainland`, do not penalize missing visible article URLs when official/internal evidence records, screenshots, source labels, or audit notes are available to support the claim.
- Missing credentials, blocked access, or failed platform calls must be marked `Limited`; do not infer platform visibility from model memory.
- AI platform answers are `Observed` unless backed by source references/evidence records or corroborated by authoritative sources.
- Brand/entity facts should prefer official websites, ICP/app filing records, enterprise credit records or licensed commercial APIs, official app stores, verified WeChat official accounts, regulatory/association/government pages, then Baidu Baike/mainstream media.
- Preserve conflicts as `Conflicting`; do not average contradictory sources away.

Evidence rows must include `platform/source`, `query`, `captured_at`, `status`, source reference or evidence record where available, `extracted_claims`, `confidence`, and `evidence_state`.

## Input Handling

1. Determine whether the input is a URL, markdown/text file, pasted article, outline, or draft.
2. If it is a URL and fetching is appropriate, fetch the main article content and preserve title, headings, paragraphs, lists, tables, visible author, visible dates, image alt text, and visible source links.
3. If it is a local file, read it directly.
4. If it is pasted text, score only what is present and mark any URL/page-level checks as limited.
5. Segment the article by H2/H3 headings. If there are no headings, segment by logical paragraphs or sections.
6. If the article discusses a named brand/entity, extract entity facts from the article before running the brand branch.

## Branch 1: AI Citability

Use the selected profile's citability rubric. The dimension weights stay stable:

| Citability Dimension | Weight |
|---|---:|
| Answer Block Quality | 30% |
| Passage Self-Containment | 25% |
| Structural Readability | 20% |
| Statistical Density | 15% |
| Uniqueness & Original Data | 10% |

Evaluate for `global_default`:

- Whether each major section opens with a 1-2 sentence direct answer.
- Whether passages can be extracted and understood without surrounding context.
- Whether the topic/entity is explicitly named instead of relying on pronouns.
- Whether paragraphs are 50-200 words where possible, with 2-4 sentences.
- Whether headings, lists, and tables make the article easy to segment.
- Whether statistics, dates, named entities, and sources are present.
- Whether the article contains original data, case studies, or unique examples.

Evaluate additionally for `cn_mainland`:

- Chinese passage length by character count, not English words: optimal 120-350 CJK characters, acceptable 80-500.
- Whether H2/H3 sections open with Chinese answer patterns such as `X 是...`, `X 指...`, `X 适用于...`, `区别在于...`, `关键看...`.
- Whether extracted passages repeat important Chinese entity names instead of relying on `它`, `这个`, `该平台`, `上述`, or `这些`.
- Whether factual density includes RMB amounts, dates, mainland locations, policy names, standard numbers, ICP/filing identifiers, licenses, named regulators, courts, exchanges, and official bodies.
- Whether the content uses Chinese extractable structures: question headings, definition paragraphs, tables, steps, FAQ, and `适用 / 不适用 / 风险 / 证据` matrices.

Output for this branch:

- `AI Citability Score: XX/100`
- score table with the five original dimensions
- top 3 strongest citable passages
- bottom 3 weakest passages
- citability coverage: percentage of blocks scoring above 70
- rewrite suggestions for blocks below 60

## Branch 2: Content / E-E-A-T

Use the original `/geo content` E-E-A-T logic as a separate branch for `global_default`. Keep the four E-E-A-T dimensions independent:

| Content Dimension | Max Points |
|---|---:|
| Experience | 25 |
| Expertise | 25 |
| Authoritativeness | 25 |
| Trustworthiness | 25 |

Evaluate article-visible signals:

- First-hand experience: testing, implementation, screenshots, process notes, examples, case studies.
- Expertise: author credentials, topical depth, accurate terminology, methodology, data-backed claims.
- Authoritativeness: cited sources, external validation mentioned in the article, recognized entities, author/publisher credibility when visible.
- Trustworthiness: visible author, publish/update dates, source attribution or evidence notes, disclosures, transparent claims, corrections/editorial cues when present. For `cn_mainland`, do not require raw URLs to be shown in the published article body.
- Freshness: visible publish date and last updated date, especially for time-sensitive claims.
- Low-quality AI content patterns: generic phrasing, filler, shallow sections, repeated conclusions, unsupported claims.
- Article-visible schema-equivalent signals: author/byline, author qualifications, `datePublished`, `dateModified`, FAQ-like sections, HowTo-like steps, citations/sources, and clearly stated article topic/entity.

Do not require actual JSON-LD for this branch. If schema or metadata cannot be seen from the article text, do not penalize heavily unless the article page itself is being audited and the user asked for page-level scoring.

For `cn_mainland`, use E-E-A-T-C instead:

| Dimension | Max Points |
|---|---:|
| Experience | 20 |
| Expertise | 20 |
| Authoritativeness | 20 |
| Trustworthiness | 20 |
| China Compliance & Context | 20 |

The compliance dimension must check high-risk mainland contexts such as medical/health, finance/investment/insurance/lending, legal advice, education credentials/admissions, real estate, employment/labor, data/privacy/AI/algorithms, advertising claims, and consumer protection. Penalize unsupported absolute claims, unverified licenses, outdated policy references, missing disclaimers where needed, and failure to distinguish facts from opinion or promotion.

Output for this branch:

- `Content / E-E-A-T Score: XX/100`
- E-E-A-T score table
- strongest trust signals
- weakest trust gaps
- freshness assessment
- article-visible schema-equivalent notes
- low-quality AI content concerns, if any

## Branch 3: Platform Content Fit

Use only the article-content portions of the platform rubric unless the selected profile enables platform verification evidence. Do not include unrelated whole-site infrastructure in an article-first score.

For `global_default`, score platform fit as an independent branch:

| Platform Content Subscore | Weight |
|---|---:|
| Google AI Overviews Content Fit | 30% |
| ChatGPT Search Content Fit | 25% |
| Perplexity Content Fit | 25% |
| Gemini / Multimodal Content Fit | 10% |
| Bing Copilot Content Fit | 10% |

Evaluate content-only platform signals:

Google AI Overviews:

- Question-based H2/H3 headings.
- Direct answer immediately after question headings.
- Tables for comparisons, pricing, specs, or feature differences.
- Ordered lists for processes and unordered lists for options/features.
- FAQ section with real questions.
- Clear definitions and glossary-style explanations.
- Statistics with named sources.
- Visible publish/update dates and author byline.

ChatGPT Search:

- Comprehensive article depth.
- Clear entity descriptions and canonical explanations.
- Strong attribution and source clarity.
- Article reads like an authoritative answer page rather than a thin post.
- Coverage of likely follow-up questions.

Perplexity:

- Freshness and recent update signals.
- Original research, benchmarks, case studies, or datasets.
- Direct, standalone paragraphs.
- Claims supported by multiple or named sources.
- Discussion-worthy or comparison-worthy insights.

Gemini:

- Useful image/table/chart references when present.
- Descriptive image alt text if available.
- Multi-modal support from diagrams, screenshots, videos, or charts.
- Strong E-E-A-T content signals visible in the article.

Bing Copilot:

- Literal target phrase coverage in title/headings/body.
- Clear meta-style summary or intro paragraph.
- Descriptive headings.
- Concise, structured answers.

For `cn_mainland`, score platform fit with this matrix:

| Platform Content Subscore | Weight |
|---|---:|
| DeepSeek Content Fit | 30% |
| Qwen / Tongyi Qianwen Content Fit | 25% |
| Wenxin / ERNIE Bot Content Fit | 25% |
| Doubao Content Fit | 20% |

DeepSeek:

- Clear thesis and conclusion.
- Source chain and attribution.
- Complex question coverage.
- Data and factual density.
- Transparent reasoning.
- Counterexamples, boundaries, and limitations.

Qwen / Tongyi Qianwen:

- Structure and hierarchy.
- Workplace reuse value.
- Summary friendliness.
- Tables, lists, frameworks.
- Multimodal expansion potential.
- Enterprise/industry context accuracy.

Wenxin / ERNIE Bot:

- Chinese knowledge QA fit.
- Baidu/encyclopedic expression.
- Authoritative source and freshness.
- Entity clarity.
- Chinese writing standard.
- Multimodal support.

Doubao:

- Plain Chinese explanation.
- Scenario-based framing.
- Short answer extractability.
- Actionable steps.
- Rewrite/creation friendliness.
- Conversational but accurate tone.

When platform verification is possible, include a second column for verification state: `Verified / Observed / Conflicting / Limited`.

Output for this branch:

- `Platform Content Fit Score: XX/100`
- per-platform content-only score table
- platform-specific gaps that can be fixed in the article text
- cross-platform quick wins

## Branch 4: Brand Entity Consistency

Use `/geo brand-mentions` only for article-relevant brand/entity consistency. Do not run a full brand authority score unless the user explicitly asks.

If the article does not discuss a brand, company, product, founder, or named organization, mark this branch `N/A` and exclude it from the final weighted score.

If the article does discuss brand entities, evaluate:

| Brand Entity Dimension | Weight |
|---|---:|
| Entity Extraction Clarity | 25% |
| On-Article Fact Consistency | 25% |
| Public-Domain Consistency | 35% |
| Citation / Attribution Support | 15% |

Entity Extraction Clarity:

- Brand/entity name is explicit and consistently spelled.
- Official domain, product names, parent company, founders, leadership, location, category, and dates are clearly stated when relevant.
- The article distinguishes similar entities, subsidiaries, product lines, or regional brands.

On-Article Fact Consistency:

- The article does not contradict itself on company name, founding date, headquarters, license/registration status, product names, prices, availability, or leadership.
- Acronyms, abbreviations, and legal names are introduced clearly.

Public-Domain Consistency:

- Compare article claims against the official domain and credible public domains when available, such as LinkedIn, Wikipedia/Wikidata, Crunchbase, app stores, regulatory pages, trusted news, product documentation, and official social profiles.
- Check whether core entity facts match: official spelling, domain, company description, leadership/founders, location, launch/founding dates, product names, and stated business category.
- If browsing/search is not available or the input lacks enough entity context, mark this subscore as `Limited` instead of inventing verification.

Citation / Attribution Support:

- Claims about brands/entities are attributed to credible sources or supported by internal evidence records. For `cn_mainland`, raw URLs do not need to be visible in the published article body.
- The article separates verified facts from interpretation or opinion.

For `cn_mainland`, evaluate these entity facts when relevant:

- Chinese full legal name.
- English name, pinyin name, or abbreviation.
- Brand name, product names, and versions.
- Official domain.
- Unified social credit code.
- ICP filing subject.
- App developer or publisher.
- Mini-program or WeChat official account verification subject.
- Legal representative, founder, or leadership when relevant.
- Headquarters or operating region.
- License, permit, certification, or filing number.
- Founding, launch, publication, or update dates.

Use evidence states:

| State | Meaning |
|---|---|
| `Verified` | Confirmed by official, S/A-tier, or equivalent authoritative source. |
| `Observed` | Seen in public/platform sources but not authoritative enough to verify. |
| `Conflicting` | Sources disagree. |
| `Limited` | Not enough accessible evidence. |

Output for this branch:

- `Brand Entity Consistency Score: XX/100` or `N/A`
- extracted entities and key facts
- consistency table: `Article Claim | Public Source | Match? | Notes`
- contradictions or uncertain claims
- recommended wording fixes for inconsistent entity descriptions

## Final Article GEO Score

After scoring the independent branches, calculate a final score. Preserve branch independence in the report.

Default `global_default` weights when a brand/entity branch applies:

| Branch | Weight |
|---|---:|
| AI Citability | 40% |
| Content / E-E-A-T | 30% |
| Platform Content Fit | 20% |
| Brand Entity Consistency | 10% |

Default `global_default` weights when the brand/entity branch is `N/A`:

| Branch | Weight |
|---|---:|
| AI Citability | 45% |
| Content / E-E-A-T | 35% |
| Platform Content Fit | 20% |

Formula when brand applies:

```text
Article GEO Score =
AI Citability * 0.40
+ Content/E-E-A-T * 0.30
+ Platform Content Fit * 0.20
+ Brand Entity Consistency * 0.10
```

Formula when brand is N/A:

```text
Article GEO Score =
AI Citability * 0.45
+ Content/E-E-A-T * 0.35
+ Platform Content Fit * 0.20
```

Default `cn_mainland` weights when a brand/entity branch applies:

| Branch | Weight |
|---|---:|
| Chinese AI Citability | 30% |
| Content / E-E-A-T-C | 25% |
| Mainland Platform Content Fit | 25% |
| Source / Compliance Evidence | 10% |
| Brand Entity Consistency | 10% |

Default `cn_mainland` weights when the brand/entity branch is `N/A`:

| Branch | Weight |
|---|---:|
| Chinese AI Citability | 35% |
| Content / E-E-A-T-C | 30% |
| Mainland Platform Content Fit | 25% |
| Source / Compliance Evidence | 10% |

## Report File Output

Always save the completed analysis as a Markdown file. Preserve the report
structure exactly as defined in the Output Format section; only change the
delivery method from an inline answer to a `.md` file.

- If the user provides an output path or filename, write the report there.
- Otherwise write the report to the current working directory as
  `GEO-CONTENT-GRADER-ANALYSIS.md`.
- If that filename already exists, create a timestamped filename such as
  `GEO-CONTENT-GRADER-ANALYSIS-YYYYMMDD-HHMM.md` instead of overwriting unless
  the user explicitly asks to replace it.
- The final chat response should be brief: include the saved file path and the
  final Article GEO Score. Do not duplicate the full report inline unless the
  user asks for it.

## Output Format

Use this Chinese-first structure unless the user asks otherwise. Keep English
only where it helps identify stable metric names, platform names, filenames,
quoted headings, source labels, or technical terms. Write findings, status,
strengths, deductions, fixes, and the overall judgment primarily in Chinese.

```markdown
## Article GEO Score: XX/100

**GEO Profile:** global_default 或 cn_mainland
**Profile Reason:** 用户指定 / 自动识别
**Evidence Mode:** live_platform_queries / limited / content_only

| Branch | Score | Weight | Weighted | Status |
|---|---:|---:|---:|---|
| AI Citability | XX/100 | 按 profile | XX | 强/中等/弱 |
| Content / E-E-A-T 或 E-E-A-T-C | XX/100 | 按 profile | XX | 强/中等/弱 |
| Platform Content Fit | XX/100 | 按 profile | XX | 强/中等/弱 |
| Source / Compliance Evidence | XX/100 或 N/A | 按 profile | XX | 强/中等/弱/不适用 |
| Brand Entity Consistency | XX/100 或 N/A | 按 profile | XX | 强/中等/弱/不适用 |

**文件：** [输入文章文件名或 URL]

### 1. AI Citability: XX/100

| Dimension | Score | Weight | Weighted |
|---|---:|---:|---:|
| Answer Block Quality | XX/100 | 30% | XX |
| Passage Self-Containment | XX/100 | 25% | XX |
| Structural Readability | XX/100 | 20% | XX |
| Statistical / Factual Density | XX/100 | 15% | XX |
| Uniqueness & Original Data | XX/100 | 10% | XX |

**强项：** 用中文概括 1-3 个最有利于 AI 摘取/引用的结构或段落，例如问题式标题、直接答案、FAQ、Key Facts、对比表、实体关系表等。

**主要扣分：** 用中文说明 1-3 个影响可引用性的缺口，例如原创数据不足、段落不够自包含、统计/事实密度偏低、缺少可验证来源等。

### 2. Content / E-E-A-T: XX/100

global_default 使用 E-E-A-T；cn_mainland 使用 E-E-A-T-C。

| Dimension | Score | Max | Finding |
|---|---:|---:|---|
| Experience | XX | 25 或 20 | 中文说明一手经验、实测、案例、方法论是否充分 |
| Expertise | XX | 25 或 20 | 中文说明实体关系、术语、边界解释、专业深度 |
| Authoritativeness | XX | 25 或 20 | 中文说明官方、监管、公告、权威来源支撑 |
| Trustworthiness | XX | 25 或 20 | 中文说明作者、发布时间、更新时间、披露、来源列表 |
| China Compliance & Context | XX 或 N/A | 20 | cn_mainland 时说明大陆合规、资质、政策、广告/高风险行业风险 |

用中文写一段简短判断，说明这篇文章在经验、专业性、权威性和可信度上的整体表现。保留必要的英文术语或页面栏目名，例如 `Key Facts`、`Deployment note`、`llms.txt entry`。

### 3. Platform Content Fit: XX/100

global_default:

| Platform | Content-Only Score | Main Gap |
|---|---:|---|
| Google AI Overviews | XX/100 | 中文说明主要优势或缺口 |
| ChatGPT Search | XX/100 | 中文说明主要优势或缺口 |
| Perplexity | XX/100 | 中文说明主要优势或缺口 |
| Gemini | XX/100 | 中文说明主要优势或缺口 |
| Bing Copilot | XX/100 | 中文说明主要优势或缺口 |

cn_mainland:

| Platform | Content Fit Score | Verification State | Main Evidence / Gap |
|---|---:|---|---|
| DeepSeek | XX/100 | Verified/Observed/Conflicting/Limited | 中文说明推理、来源链、实体识别或验证缺口 |
| Qwen / 通义千问 | XX/100 | Verified/Observed/Conflicting/Limited | 中文说明办公总结、结构化、企业语境或验证缺口 |
| Wenxin / 文心一言 | XX/100 | Verified/Observed/Conflicting/Limited | 中文说明百科式表达、权威来源、时效或验证缺口 |
| Doubao / 豆包 | XX/100 | Verified/Observed/Conflicting/Limited | 中文说明通俗解释、场景化、短答案或验证缺口 |

**最值得补的是：** 用中文提出一个最能提升多平台适配度的内容补强点，例如实体关系图、流程图、图片 alt、原创数据、FAQ、摘要式开头等。

### 4. Source / Compliance Evidence: XX/100 或 N/A

cn_mainland 必须输出；global_default 可在有限场景标 N/A。

| Claim Type | Best Source Tier | Evidence State | Notes |
|---|---|---|---|
| 政策/监管/标准 | S/A/B/C/D 或 N/A | Verified/Observed/Conflicting/Limited | 中文说明证据是否足够 |
| 资质/备案/主体 | S/A/B/C/D 或 N/A | Verified/Observed/Conflicting/Limited | 中文说明证据是否足够 |
| 用户场景/口碑 | S/A/B/C/D 或 N/A | Verified/Observed/Conflicting/Limited | 中文说明证据是否足够 |

### 5. Brand Entity Consistency: XX/100 或 N/A

核心实体关系整体一致/存在以下风险：

| Entity | Article Claim | Public Evidence | Evidence State | Match |
|---|---|---|---|---|
| 实体名 | 文章中的主张或描述 | 官方来源、监管页面、公告或可信公开证据 | Verified/Observed/Conflicting/Limited | Yes/No/Limited |

用中文补充说明是否存在实体名称、母子公司、品牌/产品、牌照、创始人、地区、发行方、收购关系等方面的不一致或需要澄清处。

### Priority Fixes
1. 用中文写最优先修改项。
2. 用中文写第二优先修改项。
3. 用中文写第三优先修改项。
4. 如有必要，继续列出 4-5 条，但避免过长。

### 总体判断

用中文写 1 段总评：说明这篇文章是否已经适合 AI 搜索理解、摘取和引用；最主要的提升空间是什么。避免泛泛而谈，要点名具体内容结构或事实支撑缺口。
```

## Interpretation

- 85-100: Excellent. Strong citation-ready article with trustworthy, platform-friendly content.
- 70-84: Good. AI-readable with clear optimization opportunities.
- 55-69: Fair. Some useful passages, but weak extractability, trust, platform fit, or entity consistency.
- 40-54: Poor. AI systems may understand the topic but have little reason to cite or trust it.
- 0-39: Critical. Mostly invisible or unsuitable for AI citation.

## Important Notes

- Be explicit when a score is estimated because only pasted text was available.
- Do not invent sources, statistics, author credentials, dates, rankings, or public-domain entity facts.
- Keep the branch scores separate; the final score is only a weighted summary.
- Treat technical/site modules as optional follow-up, not part of article content scoring.
- If browsing is needed to verify public-domain brand consistency, use credible public sources and cite them in the report. If verification cannot be completed, mark the relevant rows as `Limited`.
