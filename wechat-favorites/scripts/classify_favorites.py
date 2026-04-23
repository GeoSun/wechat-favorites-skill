# -*- coding: utf-8 -*-
"""
微信收藏智能分类脚本
从 favorites_all.csv 读取，按关键词多标签分类
"""
import csv, os, re
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "exported_favorites")

# 分类关键词体系（多标签）
CATEGORIES = {
    "生物医药": ["创新药", "ADC", "CAR-T", "mRNA", "临床试验", "靶点", "抗体", "疫苗", "基因治疗", "细胞治疗", "PD-1", "肿瘤", "癌症", "新药", "FDA", "NMPA", "CDE", "IND", "NDA", "生物药", "小分子", "大分子", "GLP-1", "减肥药", "阿尔茨海默", "帕金森", "罕见病"],
    "AI科技": ["GPT", "大模型", "LLM", "Agent", "RAG", "AI", "人工智能", "机器学习", "深度学习", "神经网络", "Transformer", "芯片", "GPU", "NVIDIA", "OpenAI", "Claude", "Gemini", "算力", "训练", "推理", "多模态", "AIGC", "ChatGPT"],
    "投资金融": ["IPO", "上市", "融资", "估值", "科创板", "创业板", "基金", "投资", "VC", "PE", "募资", "退出", "并购", "M&A", "市值", "股票", "二级市场", "一级市场", "投资机构", "LP", "GP"],
    "科学研究": ["Nature", "Science", "Cell", "论文", "研究", "发现", "突破", "神经科学", "生物学", "物理学", "化学", "材料", "量子", "实验", "学术", "博士后", "教授", "实验室"],
    "商业财经": ["企业", "公司", "战略", "行业", "市场", "商业模式", "盈利", "营收", "增长", "竞争", "垄断", "监管", "政策", "经济", "宏观", "GDP", "消费", "零售"],
    "生活方式": ["健康", "运动", "饮食", "睡眠", "心理", "旅行", "美食", "读书", "电影", "音乐", "游戏", "咖啡", "茶", "养生"],
    "媒体资讯": ["新闻", "热点", "事件", "评论", "观点", "分析", "报道", "记者", "媒体", "舆论", "热搜"],
    "政治国际": ["国际", "外交", "地缘", "政治", "政府", "政策", "中美", "欧盟", "俄罗斯", "战争", "冲突", "制裁"],
}

def classify_text(title, description=""):
    """返回文本命中的分类列表"""
    text = f"{title} {description}".lower()
    tags = []
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw.lower() in text:
                tags.append(cat)
                break
    return tags if tags else ["未分类"]


def main():
    print("=" * 60)
    print("  微信收藏智能分类")
    print("=" * 60)

    input_path = os.path.join(OUTPUT_DIR, "favorites_all.csv")
    output_path = os.path.join(OUTPUT_DIR, "articles_final.csv")

    if not os.path.exists(input_path):
        print(f"[ERROR] 请先运行 export_favorites.py 生成 {input_path}")
        return

    records = []
    cat_counts = defaultdict(int)
    cat_files = {cat: [] for cat in list(CATEGORIES.keys()) + ["未分类"]}

    with open(input_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title", "")
            desc = row.get("description", "")
            tags = classify_text(title, desc)
            row["categories"] = "|".join(tags)
            records.append(row)

            for t in tags:
                cat_counts[t] += 1
                cat_files[t].append(row)

    # 写带标签的完整 CSV
    fieldnames = list(records[0].keys()) if records else []
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"已分类: {output_path} ({len(records)} 条)\n")

    # 打印统计
    print("分类统计:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        pct = 100 * count / len(records) if records else 0
        print(f"  {cat}: {count} ({pct:.1f}%)")

    # 导出各分类 CSV
    for cat, rows in cat_files.items():
        if rows:
            cat_path = os.path.join(OUTPUT_DIR, f"cat_{cat.replace('/', '_')}.csv")
            with open(cat_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)

    print(f"\n各分类文件: {os.path.join(OUTPUT_DIR, 'cat_*.csv')}")


if __name__ == "__main__":
    main()
