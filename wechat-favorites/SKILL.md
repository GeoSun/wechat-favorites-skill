---
name: wechat-favorites
description: 微信收藏夹导出、分类与知识库管理。当用户提到微信收藏、收藏夹导出、收藏文章分类、IMA知识库导入、收藏整理时触发。支持从解密后的 favorite.db 导出收藏记录、智能分类（生物医药/AI/投资等）、批量导入IMA知识库、生成分类报告。
---

# WeChat Favorites Skill

微信收藏夹导出与智能分类工具。

## 核心能力

1. **收藏导出** — 从解密后的 `favorite.db` 导出全部收藏记录
2. **智能分类** — 多标签分类（生物医药、AI、投资、科学、商业等）
3. **IMA导入** — 批量导入到 IMA 知识库（支持断点续传）
4. **报告生成** — 分类统计、年度趋势、热门话题

## 前置条件

- 已完成 `wechat-decrypt` 解密，`decrypted/favorite/favorite.db` 存在
- Python 3.10+
- 依赖：`pip install zstandard pycryptodome`

### IMA 导入配置（可选）

IMA 知识库导入为可选功能，需要配置凭证。

**方式一：配置文件（推荐）**

创建 `~/.config/ima/config.json`：
```json
{
    "client_id": "your_client_id",
    "api_key": "your_api_key",
    "kb_id": "your_knowledge_base_id"
}
```

**方式二：环境变量**
```bash
export IMA_CLIENT_ID="your_client_id"
export IMA_API_KEY="your_api_key"
export IMA_KB_ID="your_knowledge_base_id"
```

**方式三：命令行参数**
```bash
python ima_batch_import.py --kb-id YOUR_KB_ID
```

## 工作目录

所有操作在 `wechat-decrypt/` 项目目录下执行（替换为你的本地路径）：
```bash
cd /path/to/your/wechat-decrypt
```

## 核心工作流

### 1. 导出收藏记录

```python
import sqlite3, csv, zstandard
conn = sqlite3.connect('decrypted/favorite/favorite.db')
rows = conn.execute("SELECT * FROM fav_db_item").fetchall()
# 解析 XML content 字段，提取标题、URL、来源
# WCDB_CT_content=4 时需 zstd 解压
```

输出：`exported_favorites/favorites_all.csv`

### 2. 智能分类

分类体系（多标签）：
- **生物医药** — 创新药、临床试验、靶点、ADC、CAR-T、mRNA
- **AI/科技** — GPT、大模型、Agent、芯片、RAG
- **投资/金融** — IPO、融资、估值、科创板、基金
- **科学/研究** — 神经科学、生物学、物理学、论文
- **商业/财经** — 企业战略、行业分析、宏观经济
- **生活方式** — 健康、文化、旅行、读书
- **媒体/资讯** — 新闻评论、社会热点
- **政治/国际** — 国际关系、地缘政治

输出：`exported_favorites/articles_final.csv`（含分类标签）

### 3. IMA 知识库导入

```bash
# 基本用法（使用配置文件中的凭证）
python ima_batch_import.py

# 指定 CSV 路径和知识库
python ima_batch_import.py --csv path/to/articles.csv --kb-id YOUR_KB_ID

# 指定状态文件和日志路径
python ima_batch_import.py --state my_state.json --log my_import.log
```

- 每批 10 条 URL，自动限速（3秒/批）
- 断点续传：`ima_import_state.json` 记录进度
- 日志：`ima_import.log`

### 4. 生成分类报告

分类报告包含：
- 各分类文章数量与占比
- 年度趋势（按年份统计）
- 热门话题 TOP 10
- 各分类 TOP 来源公众号

## 数据文件

| 文件 | 内容 |
|------|------|
| `favorites_all.csv` | 全部收藏记录 |
| `articles_final.csv` | 带分类标签的文章 |
| `cat_biomed.csv` | 生物医药分类 |
| `cat_ai.csv` | AI/科技分类 |
| `cat_invest.csv` | 投资/金融分类 |
| `classification_report.md` | 分类统计报告 |
| `kb_overview.md` | 知识库总览 |

## favorite.db 表结构

```sql
CREATE TABLE fav_db_item (
    local_id INTEGER PRIMARY KEY,
    fav_local_type INTEGER,      -- 类型：1=文章, 3=图片, 等
    status INTEGER,
    create_time INTEGER,         -- 收藏时间戳
    source_id TEXT,              -- 来源 wxid
    source_type INTEGER,
    content BLOB,                -- XML 内容
    WCDB_CT_content INTEGER      -- 压缩类型标记
);
```

content 字段为 XML，解析提取：
- `<title>` 标题
- `<url>` 链接
- `<source>` 来源公众号

## 常见问题

**Q: 收藏数据不完整？**
A: 检查 `favorite.db` 最后修改时间，微信可能未同步最新数据。

**Q: IMA 导入被限流？**
A: API 限流约 200 次/小时，脚本已内置 3 秒/批的限速。可设置 cron 每 30 分钟续跑。

**Q: 如何新增分类？**
A: 修改分类脚本中的 `CATEGORY_KEYWORDS` 字典，添加关键词。

## 参考资料

- [references/schema.md](references/schema.md) — 数据库结构详解
- [references/classification.md](references/classification.md) — 分类算法说明