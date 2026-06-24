# geo-content-grader skill package

Packaged on: 2026-06-23

This package contains the current local `geo-content-grader` skill entrypoint and
the referenced scoring materials it depends on from the local
`geo-seo-claude` repository.

## Contents

- `geo-content-grader/SKILL.md` - Codex-native article scoring entrypoint.
- `references/skills/geo-citability/SKILL.md` - AI citability rubric.
- `references/skills/geo-content/SKILL.md` - E-E-A-T and content quality rubric.
- `references/skills/geo-platform-optimizer/SKILL.md` - platform optimization rubric.
- `references/skills/geo-brand-mentions/SKILL.md` - brand/entity reference rubric.
- `references/scripts/citability_scorer.py` - reusable citability scoring script from the source repo.

## Source Provenance

- Entrypoint: `/Users/amber/.agents/skills/geo-content-grader/SKILL.md`
- Reference repo: `/Users/amber/Documents/AI Content/geo-seo-claude`
- Reference repo remote: `https://github.com/zubair-trabzada/geo-seo-claude.git`
- Reference repo commit: `9eec32f5f700a1e6c3cb1cb735a56ee5ec49a964`

## Scope

This is an article-first GEO scoring package. It keeps citability,
Content/E-E-A-T, platform content fit, and brand/entity consistency separate.
It intentionally excludes full-site audit, technical SEO, crawler access,
llms.txt, and full schema scoring unless those signals are visible from the
article itself.

## Output

The grader preserves the existing Markdown report structure and now writes the
completed analysis directly to a `.md` file. By default it saves
`GEO-CONTENT-GRADER-ANALYSIS.md` in the current working directory, using a
timestamped filename when that file already exists.

Reports use a Chinese-first style: scoring dimensions, platform names, and
technical labels may stay in English, while findings, deductions, fixes, and
overall judgment are written primarily in Chinese.
