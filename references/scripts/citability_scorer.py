#!/usr/bin/env python3
"""
Citability Scorer - analyzes content blocks for AI citation readiness.

Profiles:
- global_default: original global/English scoring using word-count thresholds.
- cn_mainland: Mainland Chinese scoring using Chinese character thresholds,
  Chinese answer patterns, mainland factual markers, and entity explicitness.
"""

import json
import re
import sys
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None


SUPPORTED_PROFILES = {"global_default", "cn_mainland"}


def count_cjk_chars(text: str) -> int:
    """Count CJK ideographs and common full-width punctuation."""
    return len(re.findall(r"[\u4e00-\u9fff，。！？；：、（）《》“”‘’]", text))


def split_sentences(text: str) -> list[str]:
    """Split English or Chinese text into rough sentence units."""
    return [s.strip() for s in re.split(r"[.!?。！？]+", text) if s.strip()]


def normalize_profile(profile: Optional[str], text: str = "") -> str:
    """Return a supported scoring profile, auto-detecting Chinese when omitted."""
    if profile:
        profile = profile.strip()
    if profile in SUPPORTED_PROFILES:
        return profile
    if count_cjk_chars(text) >= 80:
        return "cn_mainland"
    return "global_default"


def score_passage(text: str, heading: Optional[str] = None, profile: Optional[str] = None) -> dict:
    """Score a single passage for AI citability (0-100)."""
    active_profile = normalize_profile(profile, text)
    if active_profile == "cn_mainland":
        return score_cn_mainland_passage(text, heading)
    return score_global_default_passage(text, heading)


def score_global_default_passage(text: str, heading: Optional[str] = None) -> dict:
    """Score one passage using the original global/default rubric."""
    words = text.split()
    word_count = len(words)
    sentences = split_sentences(text)

    scores = {
        "answer_block_quality": 0,
        "self_containment": 0,
        "structural_readability": 0,
        "statistical_density": 0,
        "uniqueness_signals": 0,
    }

    abq_score = 0
    definition_patterns = [
        r"\b\w+\s+is\s+(?:a|an|the)\s",
        r"\b\w+\s+refers?\s+to\s",
        r"\b\w+\s+means?\s",
        r"\b\w+\s+(?:can be |are )?defined\s+as\s",
        r"\bin\s+(?:simple|other)\s+(?:terms|words)\s*,",
    ]
    if any(re.search(pattern, text, re.IGNORECASE) for pattern in definition_patterns):
        abq_score += 15

    first_60_words = " ".join(words[:60])
    if any(
        re.search(pattern, first_60_words, re.IGNORECASE)
        for pattern in [
            r"\b(?:is|are|was|were|means?|refers?)\b",
            r"\d+%",
            r"\$[\d,]+",
            r"\d+\s+(?:million|billion|thousand)",
        ]
    ):
        abq_score += 15

    if heading and heading.endswith("?"):
        abq_score += 10

    if sentences:
        short_clear_sentences = sum(1 for s in sentences if 5 <= len(s.split()) <= 25)
        abq_score += int((short_clear_sentences / len(sentences)) * 10)

    if re.search(
        r"(?:according to|research shows|studies? (?:show|indicate|suggest|found)|data (?:shows|indicates|suggests))",
        text,
        re.IGNORECASE,
    ):
        abq_score += 10

    scores["answer_block_quality"] = min(abq_score, 30)

    sc_score = 0
    if 134 <= word_count <= 167:
        sc_score += 10
    elif 100 <= word_count <= 200:
        sc_score += 7
    elif 80 <= word_count <= 250:
        sc_score += 4
    elif word_count < 30 or word_count > 400:
        sc_score += 0
    else:
        sc_score += 2

    pronoun_count = len(
        re.findall(
            r"\b(?:it|they|them|their|this|that|these|those|he|she|his|her)\b",
            text,
            re.IGNORECASE,
        )
    )
    if word_count > 0:
        pronoun_ratio = pronoun_count / word_count
        if pronoun_ratio < 0.02:
            sc_score += 8
        elif pronoun_ratio < 0.04:
            sc_score += 5
        elif pronoun_ratio < 0.06:
            sc_score += 3

    proper_nouns = len(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text))
    if proper_nouns >= 3:
        sc_score += 7
    elif proper_nouns >= 1:
        sc_score += 4

    scores["self_containment"] = min(sc_score, 25)

    sr_score = 0
    if sentences:
        avg_sentence_length = word_count / len(sentences)
        if 10 <= avg_sentence_length <= 20:
            sr_score += 8
        elif 8 <= avg_sentence_length <= 25:
            sr_score += 5
        else:
            sr_score += 2

    if re.search(r"(?:first|second|third|finally|additionally|moreover|furthermore)", text, re.IGNORECASE):
        sr_score += 4
    if re.search(r"(?:\d+[\.\)]\s|\b(?:step|tip|point)\s+\d+)", text, re.IGNORECASE):
        sr_score += 4
    if "\n" in text:
        sr_score += 4

    scores["structural_readability"] = min(sr_score, 20)

    sd_score = 0
    sd_score += min(len(re.findall(r"\d+(?:\.\d+)?%", text)) * 3, 6)
    sd_score += min(len(re.findall(r"\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B|K))?", text)) * 3, 5)
    sd_score += min(
        len(
            re.findall(
                r"\b\d+(?:,\d{3})*(?:\.\d+)?\s+(?:users|customers|pages|sites|companies|businesses|people|percent|times|x\b)",
                text,
                re.IGNORECASE,
            )
        )
        * 2,
        4,
    )
    if re.search(r"\b20(?:2[3-6]|1\d)\b", text):
        sd_score += 2

    source_patterns = [
        r"(?:according to|per|from|by)\s+[A-Z]",
        r"(?:Gartner|Forrester|McKinsey|Harvard|Stanford|MIT|Google|Microsoft|OpenAI|Anthropic)",
        r"\([A-Z][a-z]+(?:\s+\d{4})?\)",
    ]
    for pattern in source_patterns:
        if re.search(pattern, text):
            sd_score += 2

    scores["statistical_density"] = min(sd_score, 15)

    us_score = 0
    if re.search(
        r"(?:our (?:research|study|data|analysis|survey|findings)|we (?:found|discovered|analyzed|surveyed|measured))",
        text,
        re.IGNORECASE,
    ):
        us_score += 5
    if re.search(r"(?:case study|for example|for instance|in practice|real-world|hands-on)", text, re.IGNORECASE):
        us_score += 3
    if re.search(r"(?:using|with|via|through)\s+[A-Z][a-z]+", text):
        us_score += 2

    scores["uniqueness_signals"] = min(us_score, 10)
    return build_passage_result("global_default", text, heading, sum(scores.values()), scores, word_count=word_count)


def score_cn_mainland_passage(text: str, heading: Optional[str] = None) -> dict:
    """Score one Chinese passage using the cn_mainland rubric."""
    cjk_count = count_cjk_chars(text)
    sentences = split_sentences(text)

    scores = {
        "answer_block_quality": 0,
        "self_containment": 0,
        "structural_readability": 0,
        "statistical_density": 0,
        "uniqueness_signals": 0,
    }

    abq_score = 0
    answer_patterns = [
        r"[\u4e00-\u9fffA-Za-z0-9]+是",
        r"[\u4e00-\u9fffA-Za-z0-9]+指",
        r"[\u4e00-\u9fffA-Za-z0-9]+适用于",
        r"区别在于",
        r"关键看",
        r"应优先",
        r"核心是",
    ]
    if any(re.search(pattern, text) for pattern in answer_patterns):
        abq_score += 15

    first_two_sentences = "。".join(sentences[:2])
    if first_two_sentences and any(re.search(pattern, first_two_sentences) for pattern in answer_patterns):
        abq_score += 10

    if heading and re.search(r"[？?]$|^(什么是|如何|怎么|为什么|是否|哪些|哪种)", heading):
        abq_score += 5

    if re.search(r"(根据|据|显示|发布|规定|要求|数据|报告|公告|标准)", first_two_sentences):
        abq_score += 5

    if sentences:
        concise_sentences = sum(1 for sentence in sentences if 15 <= count_cjk_chars(sentence) <= 90)
        abq_score += min(int((concise_sentences / len(sentences)) * 8), 8)

    scores["answer_block_quality"] = min(abq_score, 30)

    sc_score = 0
    if 120 <= cjk_count <= 350:
        sc_score += 10
    elif 80 <= cjk_count <= 500:
        sc_score += 7
    elif cjk_count < 50 or cjk_count > 700:
        sc_score += 0
    else:
        sc_score += 3

    weak_refs = len(re.findall(r"(它|这个|该平台|上述|这些|相关|其|该)", text))
    if cjk_count > 0:
        ref_ratio = weak_refs / cjk_count
        if ref_ratio < 0.005:
            sc_score += 7
        elif ref_ratio < 0.015:
            sc_score += 5
        elif ref_ratio < 0.025:
            sc_score += 2

    entity_patterns = [
        r"[\u4e00-\u9fff]{2,}(?:公司|集团|平台|系统|模型|标准|办法|规定|通知|方案)",
        r"(?:DeepSeek|豆包|千问|通义千问|文心一言|文心|百度|阿里|腾讯|字节)",
        r"(?:国务院|国家[\u4e00-\u9fff]{1,8}局|工信部|网信办|证监会|交易所)",
    ]
    entity_count = sum(len(re.findall(pattern, text)) for pattern in entity_patterns)
    if entity_count >= 3:
        sc_score += 8
    elif entity_count >= 1:
        sc_score += 5

    scores["self_containment"] = min(sc_score, 25)

    sr_score = 0
    if sentences:
        avg_chars = cjk_count / len(sentences)
        if 25 <= avg_chars <= 80:
            sr_score += 8
        elif 15 <= avg_chars <= 110:
            sr_score += 5
        else:
            sr_score += 2

    if re.search(r"(第一|第二|第三|首先|其次|最后|一是|二是|三是)", text):
        sr_score += 4
    if re.search(r"(\d+[\.、)]|[一二三四五六七八九十]+[、.])", text):
        sr_score += 4
    if "\n" in text or re.search(r"(适用|不适用|风险|证据|来源|建议|步骤|对比)", text):
        sr_score += 4

    scores["structural_readability"] = min(sr_score, 20)

    sd_score = 0
    sd_score += min(len(re.findall(r"\d+(?:\.\d+)?%", text)) * 3, 5)
    sd_score += min(len(re.findall(r"(?:¥|￥)?\d+(?:\.\d+)?\s*(?:元|万元|亿元)", text)) * 3, 5)
    sd_score += min(len(re.findall(r"\b20\d{2}\s*年(?:\s*\d{1,2}\s*月(?:\s*\d{1,2}\s*日)?)?", text)) * 2, 4)
    sd_score += min(len(re.findall(r"(?:GB/T|GB|JR/T|YY/T)\s*[\d\-]+", text)) * 3, 4)
    sd_score += min(len(re.findall(r"(?:ICP备|统一社会信用代码|许可证编号|备案号)", text)) * 3, 4)
    if re.search(r"(国务院|工信部|国家网信办|市场监管总局|人民法院|证监会|银保监|交易所)", text):
        sd_score += 3

    scores["statistical_density"] = min(sd_score, 15)

    us_score = 0
    if re.search(r"(我们(?:测试|调研|统计|分析|发现)|本次(?:测试|调研|统计)|样本|访谈|问卷)", text):
        us_score += 5
    if re.search(r"(案例|实测|复盘|客户|项目|落地|实践)", text):
        us_score += 3
    if re.search(r"(方法论|框架|模型|指标体系|评分规则)", text):
        us_score += 2

    scores["uniqueness_signals"] = min(us_score, 10)
    return build_passage_result(
        "cn_mainland",
        text,
        heading,
        sum(scores.values()),
        scores,
        character_count=cjk_count,
        sentence_count=len(sentences),
    )


def build_passage_result(
    profile: str,
    text: str,
    heading: Optional[str],
    total: int,
    scores: dict,
    word_count: Optional[int] = None,
    character_count: Optional[int] = None,
    sentence_count: Optional[int] = None,
) -> dict:
    """Build a normalized passage result payload."""
    if total >= 80:
        grade = "A"
        label = "Highly Citable"
    elif total >= 65:
        grade = "B"
        label = "Good Citability"
    elif total >= 50:
        grade = "C"
        label = "Moderate Citability"
    elif total >= 35:
        grade = "D"
        label = "Low Citability"
    else:
        grade = "F"
        label = "Poor Citability"

    if profile == "cn_mainland":
        compact = re.sub(r"\s+", "", text)
        preview = compact[:80] + ("..." if len(compact) > 80 else "")
    else:
        words = text.split()
        preview = " ".join(words[:30]) + ("..." if len(words) > 30 else "")

    result = {
        "heading": heading,
        "profile": profile,
        "total_score": total,
        "grade": grade,
        "label": label,
        "breakdown": scores,
        "preview": preview,
    }
    if word_count is not None:
        result["word_count"] = word_count
    if character_count is not None:
        result["character_count"] = character_count
    if sentence_count is not None:
        result["sentence_count"] = sentence_count
    return result


def analyze_page_citability(url: str, profile: Optional[str] = None) -> dict:
    """Analyze all content blocks on a page for citability."""
    if requests is None or BeautifulSoup is None:
        return {
            "error": "Page fetching requires optional packages: requests beautifulsoup4 lxml",
            "profile": normalize_profile(profile),
        }

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            },
            timeout=30,
        )
        response.raise_for_status()
    except Exception as exc:
        return {"error": f"Failed to fetch page: {str(exc)}"}

    soup = BeautifulSoup(response.text, "lxml")

    for element in soup.find_all(["script", "style", "nav", "footer", "header", "aside", "form"]):
        element.decompose()

    blocks = []
    current_heading = "Introduction"
    current_paragraphs = []

    for element in soup.find_all(["h1", "h2", "h3", "h4", "p", "ul", "ol", "table"]):
        if element.name.startswith("h"):
            if current_paragraphs:
                combined = " ".join(current_paragraphs)
                if len(combined.split()) >= 20 or count_cjk_chars(combined) >= 80:
                    blocks.append({"heading": current_heading, "content": combined})
            current_heading = element.get_text(strip=True)
            current_paragraphs = []
        else:
            text = element.get_text(strip=True)
            if text and (len(text.split()) >= 5 or count_cjk_chars(text) >= 20):
                current_paragraphs.append(text)

    if current_paragraphs:
        combined = " ".join(current_paragraphs)
        if len(combined.split()) >= 20 or count_cjk_chars(combined) >= 80:
            blocks.append({"heading": current_heading, "content": combined})

    active_profile = normalize_profile(profile, " ".join(block["content"] for block in blocks))
    scored_blocks = [score_passage(block["content"], block["heading"], active_profile) for block in blocks]

    if scored_blocks:
        avg_score = sum(block["total_score"] for block in scored_blocks) / len(scored_blocks)
        top_blocks = sorted(scored_blocks, key=lambda x: x["total_score"], reverse=True)[:5]
        bottom_blocks = sorted(scored_blocks, key=lambda x: x["total_score"])[:5]
        if active_profile == "cn_mainland":
            optimal_count = sum(1 for block in scored_blocks if 120 <= block.get("character_count", 0) <= 350)
        else:
            optimal_count = sum(1 for block in scored_blocks if 134 <= block.get("word_count", 0) <= 167)
    else:
        avg_score = 0
        top_blocks = []
        bottom_blocks = []
        optimal_count = 0

    grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for block in scored_blocks:
        grade_dist[block["grade"]] += 1

    return {
        "url": url,
        "profile": active_profile,
        "total_blocks_analyzed": len(scored_blocks),
        "average_citability_score": round(avg_score, 1),
        "optimal_length_passages": optimal_count,
        "grade_distribution": grade_dist,
        "top_5_citable": top_blocks,
        "bottom_5_citable": bottom_blocks,
        "all_blocks": scored_blocks,
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python citability_scorer.py <url> [--profile global_default|cn_mainland]")
        print("Returns JSON with citability analysis for all content blocks.")
        sys.exit(1)

    cli_url = sys.argv[1]
    cli_profile = None
    if "--profile" in sys.argv:
        idx = sys.argv.index("--profile")
        if idx + 1 < len(sys.argv):
            cli_profile = sys.argv[idx + 1]
    result = analyze_page_citability(cli_url, cli_profile)
    print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
