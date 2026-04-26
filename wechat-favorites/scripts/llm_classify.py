# -*- coding: utf-8 -*-
"""
LLM 二次分类模块
用大模型对关键词分类置信度低的收藏进行二次分类

配置项（环境变量，无硬编码密钥）：
- LLM_API_KEY: API 密钥（必填）
- LLM_API_URL: API 地址（默认 OpenRouter）
- LLM_MODEL: 模型名称（默认 deepseek/deepseek-chat）
- LLM_BATCH_SIZE: 每批处理数量（默认 10）
- LLM_CONCURRENCY: 最大并发数（默认 5）
- LLM_TEMPERATURE: 温度参数（默认 0.1）
"""

import os, json, urllib.request, urllib.error
from typing import List, Dict, Any, Optional

# ===== 安全模式：完全禁用网络功能 =====
SAFE_MODE = os.environ.get("SAFE_MODE", "").lower() in ("1", "true", "yes")
if SAFE_MODE:
    print("[SAFE_MODE] 网络功能已禁用，LLM 分类不可用")

# ===== 配置 =====

LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_API_URL = os.environ.get("LLM_API_URL", "https://openrouter.ai/api/v1/chat/completions")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek/deepseek-chat")
LLM_BATCH_SIZE = int(os.environ.get("LLM_BATCH_SIZE", "10"))
LLM_CONCURRENCY = int(os.environ.get("LLM_CONCURRENCY", "5"))
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.1"))

# 分类标签定义（与 classify_favorites.py 保持一致）
CATEGORY_TAGS = [
    "生物医药", "AI科技", "投资金融", "科学研究",
    "商业财经", "生活方式", "媒体资讯", "政治国际"
]

# 二级分类标签（与 classify_favorites.py 保持一致）
SUBCATEGORY_TAGS = {
    "生物医药": ["临床", "神经", "创新药", "肿瘤", "抗体", "基因治疗", "CAR-T", "ADC", "靶点", "mRNA", "PD-1/PD-L1", "罕见病", "GLP-1", "中药"],
    "AI科技": ["AI应用", "大模型/LLM", "AI医疗", "芯片/算力", "机器人", "Agent", "AIGC", "多模态", "RAG"],
    "投资金融": ["VC/PE", "二级市场", "IPO/上市", "并购", "宏观", "估值"],
    "科学研究": ["神经科学", "生物", "物理", "化学", "材料", "天文"],
    "商业财经": ["宏观经济", "行业分析", "企业战略", "互联网", "监管政策"],
    "生活方式": ["读书", "健康", "音乐", "影视", "旅行", "运动", "美食"],
}

# 跨领域标签
CROSS_DOMAIN_TAGS = [
    "生物医药+投资", "AI+医疗", "AI+投资", "生物医药+AI",
    "科学+政策", "商业+政治",
]


def build_classify_prompt(article: Dict[str, Any]) -> str:
    """构建分类 prompt（含二级分类和跨领域标签）"""
    title = article.get("title", "").strip()
    source = article.get("source_account", "").strip()
    url = article.get("url", "").strip()

    # 动态构建二级分类列表
    subcat_lines = []
    for cat, subs in SUBCATEGORY_TAGS.items():
        subcat_lines.append(f"- {cat}：{'、'.join(subs)}")
    subcat_text = "\n".join(subcat_lines)
    cross_text = "、".join(CROSS_DOMAIN_TAGS)

    return f"""你是一个专业的文章分类助手。请根据以下信息对文章进行分类。

文章标题：{title}
来源公众号：{source}
文章链接：{url}

一级分类（可多选）：
生物医药、AI科技、投资金融、科学研究、商业财经、生活方式、媒体资讯、政治国际

二级分类（选填，根据一级分类选对应的子标签）：
{subcat_text}

跨领域标签（选填，文章同时涉及两个领域时标注）：
{cross_text}

请以 JSON 格式输出：
{{"tags": ["一级标签1", "一级标签2"], "subcategories": ["二级标签1", "二级标签2"], "cross_domain": ["跨领域标签"], "reason": "分类理由（一句话）", "confidence": 0.0~1.0}}
只输出 JSON，不要有其他内容。"""


def parse_llm_response(text: str) -> Optional[Dict[str, Any]]:
    """解析 LLM 返回的 JSON"""
    try:
        text = text.strip()
        # 尝试提取 JSON 块
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()

        result = json.loads(text)
        # 过滤无效一级标签
        if "tags" in result:
            result["tags"] = [t for t in result["tags"] if t in CATEGORY_TAGS]
            if not result["tags"]:
                return None
        # 过滤无效二级标签
        if "subcategories" in result:
            valid_subs = []
            for sub in result["subcategories"]:
                for subs in SUBCATEGORY_TAGS.values():
                    if sub in subs:
                        valid_subs.append(sub)
                        break
            result["subcategories"] = valid_subs
        # 过滤无效跨领域标签
        if "cross_domain" in result:
            result["cross_domain"] = [t for t in result["cross_domain"] if t in CROSS_DOMAIN_TAGS]
        return result
    except Exception:
        return None


def _call_llm_sync(article: Dict[str, Any]) -> Dict[str, Any]:
    """同步单次 LLM 调用"""
    if SAFE_MODE:
        return {
            "local_id": article.get("local_id", ""),
            "tags": [],
            "reason": "SAFE_MODE enabled - network disabled",
            "confidence": 0.0
        }
    if not LLM_API_KEY:
        return {
            "local_id": article.get("local_id", ""),
            "tags": [],
            "reason": "LLM_API_KEY not set",
            "confidence": 0.0
        }

    prompt = build_classify_prompt(article)

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": LLM_TEMPERATURE,
        "max_tokens": 256,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            LLM_API_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {LLM_API_KEY}",
                "HTTP-Referer": "https://github.com/qclaw/wechat-favorites",
                "X-Title": "QClaw Favorites Classification"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status != 200:
                return {
                    "local_id": article.get("local_id", ""),
                    "tags": [],
                    "reason": f"API error: {resp.status}",
                    "confidence": 0.0
                }
            result = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {
            "local_id": article.get("local_id", ""),
            "tags": [],
            "reason": f"Error: {e}",
            "confidence": 0.0
        }

    try:
        content = result["choices"][0]["message"]["content"]
        parsed = parse_llm_response(content)
        if parsed:
            return {
                "local_id": article.get("local_id", ""),
                "tags": parsed.get("tags", []),
                "subcategories": parsed.get("subcategories", []),
                "cross_domain": parsed.get("cross_domain", []),
                "reason": parsed.get("reason", ""),
                "confidence": parsed.get("confidence", 0.5)
            }
    except (KeyError, IndexError):
        pass

    return {
        "local_id": article.get("local_id", ""),
        "tags": [],
        "subcategories": [],
        "cross_domain": [],
        "reason": "LLM 解析失败",
        "confidence": 0.0
    }


def classify(
    articles: List[Dict[str, Any]],
    show_progress: bool = True
) -> List[Dict[str, Any]]:
    """
    批量调用 LLM 进行分类（同步并发）

    Args:
        articles: 收藏记录列表，每条包含 local_id, title, source_account, url
        show_progress: 是否打印进度

    Returns:
        LLM 分类结果列表，每条包含 local_id, tags, reason, confidence
    """
    if not articles:
        return []

    if not LLM_API_KEY:
        print("[ERROR] LLM_API_KEY 环境变量未设置，跳过 LLM 分类")
        return []

    from concurrent.futures import ThreadPoolExecutor, as_completed

    if show_progress:
        total_batches = (len(articles) + LLM_BATCH_SIZE - 1) // LLM_BATCH_SIZE
        print(f"[LLM 二次分类] 共 {len(articles)} 条，批次大小 {LLM_BATCH_SIZE}，并发 {LLM_CONCURRENCY}")

    all_results = []

    for i in range(0, len(articles), LLM_BATCH_SIZE):
        batch = articles[i:i + LLM_BATCH_SIZE]

        if show_progress:
            batch_num = i // LLM_BATCH_SIZE + 1
            total_batches = (len(articles) + LLM_BATCH_SIZE - 1) // LLM_BATCH_SIZE
            print(f"  批次 {batch_num}/{total_batches} ({len(batch)} 条)...")

        # 并发执行当前批次
        with ThreadPoolExecutor(max_workers=LLM_CONCURRENCY) as executor:
            futures = {executor.submit(_call_llm_sync, a): a for a in batch}
            for future in as_completed(futures):
                try:
                    all_results.append(future.result())
                except Exception as e:
                    all_results.append({"tags": [], "reason": f"Error: {e}", "confidence": 0.0})

    if show_progress:
        success = sum(1 for r in all_results if r.get("tags"))
        print(f"[LLM 二次分类] 完成，共处理 {len(all_results)} 条，成功 {success} 条")

    return all_results
