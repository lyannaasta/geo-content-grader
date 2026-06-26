# geo-content-grader skill package

Packaged on: 2026-06-23

This package contains the current local `geo-content-grader` skill entrypoint and
the referenced scoring materials it depends on. The grader is now profile-aware:
one shared article-first pipeline can load either the original global rules or a
China mainland localization profile.

Install or copy the `geo-content-grader/` directory itself as the skill.

## Contents

- `geo-content-grader/SKILL.md` - Codex-native article scoring entrypoint.
- `geo-content-grader/profiles/global_default.yaml` - original global scoring profile.
- `geo-content-grader/profiles/cn_mainland.yaml` - China mainland scoring profile.
- `geo-content-grader/references/rubrics/geo-citability.md` - AI citability rubric.
- `geo-content-grader/references/rubrics/geo-content.md` - E-E-A-T and content quality rubric.
- `geo-content-grader/references/rubrics/geo-platform-optimizer.md` - platform optimization rubric.
- `geo-content-grader/references/rubrics/geo-brand-mentions.md` - brand/entity reference rubric.
- `geo-content-grader/references/rubrics/geo-cn-citability.md` - Chinese mainland citability rubric.
- `geo-content-grader/references/rubrics/geo-cn-eeatc.md` - mainland E-E-A-T-C rubric.
- `geo-content-grader/references/rubrics/geo-cn-platforms.md` - DeepSeek, Doubao, Qwen, and Wenxin platform fit rubric.
- `geo-content-grader/references/rubrics/geo-cn-source-authority.md` - mainland source authority tiers.
- `geo-content-grader/references/rubrics/geo-cn-entity.md` - mainland brand/entity consistency rubric.
- `geo-content-grader/references/scripts/citability_scorer.py` - reusable citability scoring script from the source repo.
- `geo-content-grader/references/scripts/evidence_adapters.py` - platform evidence adapter entrypoint with Limited fallback.
- `geo-content-grader/references/scripts/source_evidence.py` - public source fetcher, source-tier classifier, and lightweight entity extractor.

## Source Provenance

- Entrypoint: `/Users/amber/.agents/skills/geo-content-grader/SKILL.md`
- Reference repo: `/Users/amber/Documents/AI Content/geo-seo-claude`
- Reference repo remote: `https://github.com/zubair-trabzada/geo-seo-claude.git`
- Reference repo commit: `9eec32f5f700a1e6c3cb1cb735a56ee5ec49a964`

## Scope

This is an article-first GEO scoring package. It keeps citability,
Content/E-E-A-T or E-E-A-T-C, platform content fit, source/compliance evidence,
and brand/entity consistency separate.
It intentionally excludes full-site audit, technical SEO, crawler access,
llms.txt, and full schema scoring unless those signals are visible from the
article itself.

## Profiles

| Profile | Use |
|---|---|
| `global_default` | Original global/default GEO logic with Google AI Overviews, ChatGPT Search, Perplexity, Gemini, and Bing Copilot. |
| `cn_mainland` | Mainland China logic with Chinese character thresholds, E-E-A-T-C, DeepSeek, Doubao, Qwen/Tongyi Qianwen, Wenxin/ERNIE Bot, mainland source authority, and mainland entity verification. |

Use `cn_mainland` when the article is simplified Chinese, discusses mainland
companies/products/policies, uses RMB, ICP/filing/licensing signals, mainland
cities/provinces, or mainland regulatory context. The profile can also be
specified explicitly in the user request.

## Runtime Scripts

The citability script supports profile selection:

```bash
python geo-content-grader/references/scripts/citability_scorer.py "https://example.com/article" --profile cn_mainland
```

The evidence adapter script runs configured platform probes and returns
structured evidence. Missing credentials or failed platform access returns
`Limited` instead of fabricated evidence:

```bash
python geo-content-grader/references/scripts/evidence_adapters.py \
  --platform deepseek \
  --query "某品牌 是什么公司 官网 产品 创始人"
```

The source evidence script fetches public URLs and classifies them into the
mainland source ladder used by `cn_mainland`:

```bash
python geo-content-grader/references/scripts/source_evidence.py "https://www.example.com/about"
```

Supported credential environment variables include:

| Platform | Required key |
|---|---|
| DeepSeek | `DEEPSEEK_API_KEY` |
| Doubao | `ARK_API_KEY` and optionally `DOUBAO_MODEL` |
| Qwen / Tongyi Qianwen | `DASHSCOPE_API_KEY` |
| Wenxin / ERNIE Bot | `QIANFAN_API_KEY` and optionally `WENXIN_MODEL` |

## Output

The grader preserves the existing Markdown report structure and now writes the
completed analysis directly to a `.md` file. By default it saves
`GEO-CONTENT-GRADER-ANALYSIS.md` in the current working directory, using a
timestamped filename when that file already exists.

Reports use a Chinese-first style: scoring dimensions, platform names, and
technical labels may stay in English, while findings, deductions, fixes, and
overall judgment are written primarily in Chinese. Reports should also state
`GEO Profile`, `Profile Reason`, `Evidence Mode`, confidence, evidence
availability, and `Verified / Observed / Conflicting / Limited` evidence states
where applicable.
