---
name: geo-content-grader
description: Use when scoring, auditing, or improving an article for GEO, AI search visibility, AI citation readiness, LLM answer extraction, ChatGPT/Claude/Perplexity/Gemini discoverability, article GEO content scoring, or "文章 GEO 打分". Runs an article-first GEO scorecard using the local geo-seo-claude methodology while keeping citability, content, platform, and brand/entity checks separate.
---

# GEO Content Grader

Use this skill when the user wants to score an article, draft, page, or content brief for Generative Engine Optimization (GEO): the likelihood that AI search systems can understand, extract, trust, cite, and recommend the article.

This is a Codex-native article scoring entrypoint around the local repository:

`/Users/amber/Documents/AI Content/geo-seo-claude`

Reference the repo's scoring materials first:

- `/Users/amber/Documents/AI Content/geo-seo-claude/skills/geo-citability/SKILL.md`
- `/Users/amber/Documents/AI Content/geo-seo-claude/skills/geo-content/SKILL.md`
- `/Users/amber/Documents/AI Content/geo-seo-claude/skills/geo-platform-optimizer/SKILL.md`
- `/Users/amber/Documents/AI Content/geo-seo-claude/skills/geo-brand-mentions/SKILL.md`
- `/Users/amber/Documents/AI Content/geo-seo-claude/scripts/citability_scorer.py`

Do not require Claude Code or `~/.claude`. Do not use Claude slash commands. Treat the files above as local references and reusable scoring logic.

## Scope

This skill scores the article itself. It intentionally excludes full-site GEO infrastructure unless the signal can be evaluated from the article or the article page.

Include:

| Source Module | Include? | Article-First Scope |
|---|---:|---|
| `/geo citability` | Yes | Keep as an independent AI Citability scorecard. |
| `/geo content` | Yes | Keep as an independent E-E-A-T, content quality, freshness, and originality scorecard. Fold only article-visible Article/Author/Date schema-equivalent signals here. |
| `/geo platforms` | Partial | Keep as an independent AI Platform Fit scorecard using only content-pattern preferences from AIO, ChatGPT, Perplexity, Gemini, and Copilot. |
| `/geo brand-mentions` | Partial | Keep as an independent Brand Entity Consistency scorecard. Do not run a full brand authority scan unless asked. |

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

1. **Citability Branch** from `/geo citability`
2. **Content / E-E-A-T Branch** from `/geo content`
3. **Platform Content Fit Branch** from the content-related parts of `/geo platforms`
4. **Brand Entity Consistency Branch** from the article-relevant parts of `/geo brand-mentions`
5. **Final Article GEO Summary** combining the independent branch scores

Keep the branch logic separate. Do not mix citability findings into the E-E-A-T score, do not mix platform preferences into the citability score, and do not let off-page brand authority dominate the article score.

## Input Handling

1. Determine whether the input is a URL, markdown/text file, pasted article, outline, or draft.
2. If it is a URL and fetching is appropriate, fetch the main article content and preserve title, headings, paragraphs, lists, tables, visible author, visible dates, image alt text, and visible source links.
3. If it is a local file, read it directly.
4. If it is pasted text, score only what is present and mark any URL/page-level checks as limited.
5. Segment the article by H2/H3 headings. If there are no headings, segment by logical paragraphs or sections.
6. If the article discusses a named brand/entity, extract entity facts from the article before running the brand branch.

## Branch 1: AI Citability

Use the original `/geo citability` rubric without changing its weights:

| Citability Dimension | Weight |
|---|---:|
| Answer Block Quality | 30% |
| Passage Self-Containment | 25% |
| Structural Readability | 20% |
| Statistical Density | 15% |
| Uniqueness & Original Data | 10% |

Evaluate:

- Whether each major section opens with a 1-2 sentence direct answer.
- Whether passages can be extracted and understood without surrounding context.
- Whether the topic/entity is explicitly named instead of relying on pronouns.
- Whether paragraphs are 50-200 words where possible, with 2-4 sentences.
- Whether headings, lists, and tables make the article easy to segment.
- Whether statistics, dates, named entities, and sources are present.
- Whether the article contains original data, case studies, or unique examples.

Output for this branch:

- `AI Citability Score: XX/100`
- score table with the five original dimensions
- top 3 strongest citable passages
- bottom 3 weakest passages
- citability coverage: percentage of blocks scoring above 70
- rewrite suggestions for blocks below 60

## Branch 2: Content / E-E-A-T

Use the original `/geo content` E-E-A-T logic as a separate branch. Keep the four E-E-A-T dimensions independent:

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
- Trustworthiness: visible author, publish/update dates, source links, disclosures, transparent claims, corrections/editorial cues when present.
- Freshness: visible publish date and last updated date, especially for time-sensitive claims.
- Low-quality AI content patterns: generic phrasing, filler, shallow sections, repeated conclusions, unsupported claims.
- Article-visible schema-equivalent signals: author/byline, author qualifications, `datePublished`, `dateModified`, FAQ-like sections, HowTo-like steps, citations/sources, and clearly stated article topic/entity.

Do not require actual JSON-LD for this branch. If schema or metadata cannot be seen from the article text, do not penalize heavily unless the article page itself is being audited and the user asked for page-level scoring.

Output for this branch:

- `Content / E-E-A-T Score: XX/100`
- E-E-A-T score table
- strongest trust signals
- weakest trust gaps
- freshness assessment
- article-visible schema-equivalent notes
- low-quality AI content concerns, if any

## Branch 3: Platform Content Fit

Use only the article-content portions of `/geo platforms`. Do not include platform presence, webmaster tools, crawler/index setup, page speed, IndexNow, Google Business Profile, YouTube channel ownership, Reddit account activity, or full Knowledge Graph work.

Score platform fit as an independent branch:

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

- Claims about brands/entities are linked to or attributed to credible sources.
- The article separates verified facts from interpretation or opinion.

Output for this branch:

- `Brand Entity Consistency Score: XX/100` or `N/A`
- extracted entities and key facts
- consistency table: `Article Claim | Public Source | Match? | Notes`
- contradictions or uncertain claims
- recommended wording fixes for inconsistent entity descriptions

## Final Article GEO Score

After scoring the independent branches, calculate a final score. Preserve branch independence in the report.

Default weights when a brand/entity branch applies:

| Branch | Weight |
|---|---:|
| AI Citability | 40% |
| Content / E-E-A-T | 30% |
| Platform Content Fit | 20% |
| Brand Entity Consistency | 10% |

Default weights when the brand/entity branch is `N/A`:

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

## Output Format

Use this structure unless the user asks otherwise:

```markdown
## Article GEO Score: XX/100

| Branch | Score | Weight | Weighted | Status |
|---|---:|---:|---:|---|
| AI Citability | XX/100 | 40% | XX | ... |
| Content / E-E-A-T | XX/100 | 30% | XX | ... |
| Platform Content Fit | XX/100 | 20% | XX | ... |
| Brand Entity Consistency | XX/100 | 10% | XX | ... |

### 1. AI Citability
| Dimension | Score | Weight | Weighted |
|---|---:|---:|---:|
| Answer Block Quality | XX/100 | 30% | XX |
| Passage Self-Containment | XX/100 | 25% | XX |
| Structural Readability | XX/100 | 20% | XX |
| Statistical Density | XX/100 | 15% | XX |
| Uniqueness & Original Data | XX/100 | 10% | XX |

Strongest passages:
- ...

Weakest passages:
- ...

### 2. Content / E-E-A-T
| Dimension | Score | Max | Finding |
|---|---:|---:|---|
| Experience | XX | 25 | ... |
| Expertise | XX | 25 | ... |
| Authoritativeness | XX | 25 | ... |
| Trustworthiness | XX | 25 | ... |

Article-visible schema-equivalent notes:
- ...

### 3. Platform Content Fit
| Platform | Content-Only Score | Main Gap |
|---|---:|---|
| Google AI Overviews | XX/100 | ... |
| ChatGPT Search | XX/100 | ... |
| Perplexity | XX/100 | ... |
| Gemini | XX/100 | ... |
| Bing Copilot | XX/100 | ... |

### 4. Brand Entity Consistency
| Entity | Article Claim | Public Source / Evidence | Match | Notes |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

### Priority Fixes
1. ...
2. ...
3. ...

### Branch Reports
- Citability: ...
- Content / E-E-A-T: ...
- Platform Content Fit: ...
- Brand Entity Consistency: ...
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
