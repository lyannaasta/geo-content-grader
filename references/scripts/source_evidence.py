#!/usr/bin/env python3
"""
Mainland source evidence collector.

Fetches a public URL, assigns a rough mainland source-authority tier, and extracts
lightweight entity claims. This is intentionally conservative: fetched public
pages can support evidence rows, but only official/S/A-tier records should verify
high-risk factual claims.
"""

import argparse
import datetime as dt
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import Any, Optional


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            text = data.strip()
            if text:
                self.parts.append(text)

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def fetch_url(url: str, timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 GEO-Content-Grader/1.0"},
        method="GET",
    )
    captured_at = now_iso()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            body = response.read(1_500_000).decode("utf-8", errors="ignore")
            status = response.status
            final_url = response.geturl()
    except (urllib.error.URLError, TimeoutError) as exc:
        return {
            "url": url,
            "captured_at": captured_at,
            "status": "limited",
            "evidence_state": "Limited",
            "confidence": "Low",
            "notes": f"Fetch failed: {exc}",
        }

    parser = TextExtractor()
    parser.feed(body)
    text = parser.text()
    tier = classify_source(final_url)
    return {
        "url": final_url,
        "captured_at": captured_at,
        "http_status": status,
        "content_type": content_type,
        "source_tier": tier,
        "evidence_state": "Verified" if tier in {"S", "A"} else "Observed",
        "confidence": "High" if tier in {"S", "A"} else "Medium",
        "title": extract_title(body),
        "snippet": text[:600],
        "extracted_claims": extract_cn_claims(text),
        "notes": source_note(tier),
    }


def extract_title(html: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1)).strip()


def classify_source(url: str) -> str:
    host = urllib.parse.urlparse(url).netloc.lower()
    if host.endswith(".gov.cn") or "court.gov.cn" in host:
        return "S"
    if any(token in host for token in ["samr.gov.cn", "cac.gov.cn", "miit.gov.cn", "pbc.gov.cn", "csrc.gov.cn"]):
        return "S"
    if any(token in host for token in ["sse.com.cn", "szse.cn", "bse.cn"]):
        return "S"
    if any(token in host for token in ["edu.cn", "ac.cn", "nhc.gov.cn"]):
        return "A"
    if any(token in host for token in ["people.com.cn", "xinhuanet.com", "cctv.com", "chinanews.com.cn"]):
        return "A"
    if any(token in host for token in ["baike.baidu.com", "thepaper.cn", "caixin.com", "yicai.com"]):
        return "B"
    if any(token in host for token in ["zhihu.com", "xiaohongshu.com", "bilibili.com", "douyin.com"]):
        return "C"
    if any(token in host for token in ["sohu.com", "163.com", "toutiao.com"]):
        return "B"
    return "B"


def source_note(tier: str) -> str:
    notes = {
        "S": "Highest factual authority for applicable mainland claims.",
        "A": "Strong factual support; suitable for most non-conflicting claims.",
        "B": "Useful public support; corroborate high-risk claims with S/A sources.",
        "C": "Use for user language, sentiment, or scenarios, not high-risk factual verification.",
        "D": "Weak or non-supportive source.",
    }
    return notes.get(tier, "Unclassified source; use cautiously.")


def extract_cn_claims(text: str) -> dict[str, Any]:
    claims: dict[str, Any] = {}
    company_names = sorted(set(re.findall(r"[\u4e00-\u9fff]{2,}(?:有限责任公司|股份有限公司|有限公司|集团)", text)))
    domains = sorted(set(re.findall(r"(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.(?:com|cn|net|org|io|ai)", text)))
    icp = sorted(set(re.findall(r"[\u4e00-\u9fff]ICP备\s*\d+号(?:-\d+)?", text)))
    credit_codes = sorted(set(re.findall(r"\b[0-9A-Z]{18}\b", text)))
    licenses = sorted(set(re.findall(r"(?:许可证编号|许可证号|备案号)[：:\s]*[A-Za-z0-9\u4e00-\u9fff\-]+", text)))
    if company_names:
        claims["company_names"] = company_names[:10]
    if domains:
        claims["domains"] = domains[:10]
    if icp:
        claims["icp_filings"] = icp[:10]
    if credit_codes:
        claims["unified_social_credit_codes"] = credit_codes[:10]
    if licenses:
        claims["licenses"] = licenses[:10]
    return claims


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and classify mainland source evidence.")
    parser.add_argument("url", nargs="+", help="Public URL(s) to fetch.")
    args = parser.parse_args()
    print(json.dumps([fetch_url(url) for url in args.url], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
