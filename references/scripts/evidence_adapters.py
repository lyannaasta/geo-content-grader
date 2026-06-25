#!/usr/bin/env python3
"""
Evidence adapters for profile-aware GEO verification.

The adapters intentionally separate model/platform interpretation from factual
evidence. A platform response without source URLs is reported as Observed, not
Verified. Missing credentials or unavailable endpoints return Limited instead of
fabricating evidence.
"""

import argparse
import datetime as dt
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional


PLATFORM_ENV = {
    "deepseek": {
        "api_key": "DEEPSEEK_API_KEY",
        "base_url": "DEEPSEEK_BASE_URL",
        "default_base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    "doubao": {
        "api_key": "ARK_API_KEY",
        "base_url": "ARK_BASE_URL",
        "default_base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model_env": "DOUBAO_MODEL",
    },
    "qwen": {
        "api_key": "DASHSCOPE_API_KEY",
        "base_url": "DASHSCOPE_BASE_URL",
        "default_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    "wenxin": {
        "api_key": "QIANFAN_API_KEY",
        "base_url": "QIANFAN_BASE_URL",
        "default_base_url": "https://qianfan.baidubce.com/v2",
        "model_env": "WENXIN_MODEL",
    },
}


SOURCE_URL_PATTERN = re.compile(r"https?://[^\s)\]\"'<>]+")


@dataclass
class EvidenceResult:
    platform: str
    query: str
    captured_at: str
    status: str
    urls: list[str] = field(default_factory=list)
    snippets: list[str] = field(default_factory=list)
    extracted_claims: dict[str, Any] = field(default_factory=dict)
    confidence: str = "Low"
    evidence_state: str = "Limited"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform,
            "query": self.query,
            "captured_at": self.captured_at,
            "status": self.status,
            "urls": self.urls,
            "snippets": self.snippets,
            "extracted_claims": self.extracted_claims,
            "confidence": self.confidence,
            "evidence_state": self.evidence_state,
            "notes": self.notes,
        }


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def limited(platform: str, query: str, notes: str) -> EvidenceResult:
    return EvidenceResult(
        platform=platform,
        query=query,
        captured_at=now_iso(),
        status="limited",
        confidence="Low",
        evidence_state="Limited",
        notes=notes,
    )


def observed_or_verified(platform: str, query: str, text: str) -> EvidenceResult:
    urls = sorted(set(SOURCE_URL_PATTERN.findall(text)))
    snippets = [line.strip() for line in text.splitlines() if line.strip()][:8]
    state = "Observed"
    confidence = "Medium"
    if urls:
        state = "Observed"
        confidence = "Medium"
    return EvidenceResult(
        platform=platform,
        query=query,
        captured_at=now_iso(),
        status="ok",
        urls=urls,
        snippets=snippets,
        extracted_claims=extract_cn_entity_claims(text),
        confidence=confidence,
        evidence_state=state,
        notes="Platform response is model/platform interpretation unless corroborated by authoritative sources.",
    )


def extract_cn_entity_claims(text: str) -> dict[str, Any]:
    """Extract lightweight mainland entity hints from response text."""
    claims: dict[str, Any] = {}
    company_names = sorted(set(re.findall(r"[\u4e00-\u9fff]{2,}(?:有限责任公司|股份有限公司|有限公司|集团)", text)))
    product_names = sorted(set(re.findall(r"(?:产品|应用|App|平台|模型)[：:]\s*([^\n，。；;]{2,40})", text)))
    domains = sorted(set(re.findall(r"(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.(?:com|cn|net|org|io|ai)", text)))
    icp = sorted(set(re.findall(r"[\u4e00-\u9fff]ICP备\s*\d+号(?:-\d+)?", text)))
    if company_names:
        claims["company_names"] = company_names
    if product_names:
        claims["product_names"] = product_names
    if domains:
        claims["domains"] = domains
    if icp:
        claims["icp_filings"] = icp
    return claims


def chat_completion(platform: str, query: str, timeout: int = 45) -> EvidenceResult:
    """Run a configured OpenAI-compatible chat completion for a platform."""
    config = PLATFORM_ENV.get(platform)
    if not config:
        return limited(platform, query, f"Unsupported platform adapter: {platform}")

    api_key = os.environ.get(config["api_key"])
    if not api_key:
        return limited(platform, query, f"Missing credential: {config['api_key']}")

    base_url = os.environ.get(config["base_url"], config["default_base_url"]).rstrip("/")
    model = os.environ.get(config.get("model_env", ""), config.get("model", ""))
    if not model:
        return limited(platform, query, f"Missing model env for {platform}")

    prompt = (
        "你是 GEO 品牌实体一致性验证器。请回答用户查询，并尽量列出可核验来源 URL。"
        "如果无法确认事实，请明确说明不确定。不要编造备案、主体、创始人、官网或资质。"
    )
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        "temperature": 0,
    }

    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return limited(platform, query, f"Platform query failed: {exc}")

    try:
        content = data["choices"][0]["message"]["content"]
    except Exception:
        return limited(platform, query, "Platform response did not include choices[0].message.content")
    return observed_or_verified(platform, query, content)


def run_platform_queries(platforms: list[str], queries: list[str]) -> list[dict[str, Any]]:
    results = []
    for platform in platforms:
        for query in queries:
            results.append(chat_completion(platform, query).to_dict())
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Run cn_mainland GEO evidence adapters.")
    parser.add_argument("--platform", action="append", choices=sorted(PLATFORM_ENV), help="Platform to query. Repeatable.")
    parser.add_argument("--query", action="append", required=True, help="Query to run. Repeatable.")
    args = parser.parse_args()

    platforms = args.platform or sorted(PLATFORM_ENV)
    print(json.dumps(run_platform_queries(platforms, args.query), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
