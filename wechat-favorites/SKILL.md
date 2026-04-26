---
name: wechat-favorites
description: 微信收藏夹导出、智能分类与知识库管理。支持从解析后的 favorite.db 导出收藏记录、三级分类体系（一级9类 + 二级57标签 + 跨领域6类）、LLM 智能增强（可选）、批量导入 IMA 知识库（可选）。核心功能支持离线使用，网络功能默认关闭。
metadata:
  version: 1.1.4
  display_name: 微信收藏知识库
---

# 微信收藏知识库

Decrypt, categorize and organize wechat favorites (Official Account collection) into knowledge base

收藏夹导出 · 智能分类 · 知识库导入

**快速上手：** 解析收藏夹 → 导出记录 → 智能分类 → 导入 IMA 知识库

> 💡 **试试这样说：** "帮我整理微信收藏" / "导出收藏夹并分类" / "把微信收藏导入知识库" / "解析 favorite.db 导出文章"

---

**触发词：** 微信收藏（WeChat Favorites）、收藏夹导出（favorites export）、收藏文章分类（favorites classification）、IMA 知识库导入（knowledge base import）、收藏整理（favorites organizer）、微信公众号收藏、公众号文章整理

---

## 为什么用这个工具？

微信收藏夹积累了大量文章：随手打的标签越来越复杂，待读越积越多，从来没有真正整理过，也不记得读了哪些、学到了什么。这个工具可以：

- **自动分类** — 96% 的文章自动归入 9 大类，无需手动整理
- **细粒度标签** — 57 个二级标签，精准定位细分主题
- **跨领域识别** — 自动标注"生物医药+投资"等复合主题
- **LLM 增强** — 低置信度条目用大模型智能重判
- **知识库导入** — 一键导入 IMA，构建个人知识库

## 实测数据

基于 32,333 篇文章（2014-2025 收藏）：

| 指标 | 数值 |
|------|------|
| 总收藏数 | 36,853 |
| 文章数 | 32,333 |
| 一级分类覆盖率 | 96.0% (31,088/32,333) |
| LLM 重分类成功率 | 98.5% (8,789/8,912) |
| 二级标签平均覆盖率 | 35.5% |

## 核心能力

| 能力 | 说明 |
|------|------|
| **收藏导出** | 从解析后的 `favorite.db` 导出全部收藏记录为 CSV |
| **关键词分类** | 一级分类 9 类（生物医药/AI/投资等），关键词匹配自动识别 |
| **标签增强** | 二级标签 57 个 + 跨领域标签 6 类，支持多标签组合 |
| **LLM 增强（可选）** | 置信度 < 0.4 时自动调用 LLM 二次分类，需配置 API Key |
| **IMA导入（可选）** | 批量导入到 IMA 知识库，需配置凭证 |
| **报告生成** | 分类统计、各分类 CSV 导出 |

## 前置条件

### 1. 微信收藏数据库

本工具需要已解析的 `favorite.db` 文件。解析步骤请使用专门的微信数据库处理工具。

### 2. Python 环境

```bash
pip install pycryptodome zstandard
```

### 3. IMA 导入（可选）

如需导入 IMA 知识库：
1. 创建 IMA 知识库，获取 `kb_id`
2. 配置凭证：`~/.config/ima/client_id` 和 `~/.config/ima/api_key`


### 4. IMA 导入配置（可选）

IMA 凭证支持多种配置方式（优先级从高到低）：

| 方式 | 说明 |
|------|------|
| 命令行参数 | `--client-id`, `--api-key`, `--kb-id` |
| 环境变量 | `IMA_CLIENT_ID`, `IMA_API_KEY`, `IMA_KB_ID` |
| config.json | `ima_kb_id` 字段 |
| 文件 | `~/.config/ima/client_id`, `~/.config/ima/api_key` |

```bash
# 方式 1: 命令行参数
python import_ima.py --kb-id YOUR_KB_ID --client-id XXX --api-key YYY

# 方式 2: 环境变量
IMA_CLIENT_ID=xxx IMA_API_KEY=yyy python import_ima.py

# 方式 3: 配置文件
# 在项目目录创建 config.json，填写 ima_kb_id
# 创建 ~/.config/ima/client_id 和 api_key 文件
```

## 安全说明

本工具涉及本地文件操作与可选网络调用。所有核心功能（导出 + 本地分类）可在离线环境完成，无需任何网络配置。

| 操作 | 行为 | 数据流向 | 说明 |
|------|------|----------|------|
| **收藏导出** | 读取已解析的 `favorite.db`，导出为 CSV | 本地只读 | 核心功能，完全离线 |
| **智能分类** | 基于关键词本地分类 | 本地计算 | 核心功能，完全离线 |
| **LLM 分类** | 可选，将标题/摘要发送至外部 LLM API | 本地 → OpenRouter (可选，需配置) | 默认关闭，不调用外部 API |
| **IMA 导入** | 可选，将收藏 URL 列表发送至腾讯 IMA | 本地 → ima.qq.com (可选，需配置) | 默认关闭，不调用外部 API |
| **凭证读取** | 读取本地 `~/.config/ima/` 凭证文件 | 本地读取 | 仅 IMA 功能需要，不上传凭证 |

**可选功能说明：**
- `LLM 分类`：依赖 `llm_classify.py`，通过 OpenRouter API 调用大模型。**默认关闭**，需设置 `LLM_API_URL` 等环境变量才会发起网络请求
- `IMA 导入`：依赖 `import_ima.py`，调用腾讯 IMA 知识库 API。**默认关闭**，需配置 `client_id`/`api_key` 才会发起网络请求
- `SAFE_MODE`：**完全禁用网络功能**，设置 `SAFE_MODE=1` 环境变量即可强制离线模式
- **敏感数据**：LLM 仅发送文章标题和摘要，不发送正文内容； IMA 仅发送收藏的 URL 列表，不包含微信聊天记录

**离线使用方案：**
- 导出 + 本地分类：无需网络，无需配置任何 API
- LLM 增强：可使用本地模型（修改 `LLM_API_URL` 指向本地 Ollama）
- IMA 导入：可选功能，不导入不影响其他功能

**建议：** 在信任的网络环境或离线环境使用，网络功能均为可选，默认关闭。

## 快速开始

```bash
cd scripts

# 0. 验证环境
python quick_validate.py

# 1. 解析数据库（如未解析）
python decrypt_db.py  # 或使用其他工具

# 2. 导出收藏记录
python export_favorites.py

# 3. 智能分类（支持 LLM 增强）
python classify_favorites.py

# 4. 导入 IMA（可选）
python import_ima.py
```

## 目录结构

```
wechat-favorites/
├── SKILL.md                     # 本文件
├── LICENSE.txt                  # MIT License
├── CHANGELOG.md                 # 更新日志
├── requirements.txt             # 依赖声明
├── config.json                  # 用户配置（需创建）
├── scripts/
│   ├── quick_validate.py        # 环境验证
│   ├── decrypt_db.py            # 数据库解析
│   ├── export_favorites.py      # 收藏导出
│   ├── classify_favorites.py    # 智能分类（一级+二级+跨领域）
│   ├── llm_classify.py          # LLM 二次分类模块
│   ├── llm_incremental.py       # LLM 增量批处理
│   ├── merge_llm_results.py     # LLM 结果合并
│   ├── normalize_categories.py  # 标签标准化
│   ├── import_ima.py            # IMA 导入
│   ├── config.py                # 配置加载
│   └── key_utils.py             # 密钥工具
├── decrypted/                   # 解析输出
│   └── favorite/favorite.db
├── exported_favorites/          # 导出输出
│   ├── favorites_all.csv        # 全部收藏
│   ├── articles_final.csv       # 带分类标签
│   ├── cat_biomed.csv           # 生物医药分类
│   ├── cat_AI科技.csv           # AI 分类
│   └── ...
└── references/
    ├── classification.md        # 分类算法说明
    └── schema.md                # 数据库结构
```

## 数据流程

```
favorite.db (加密)
      │
      ▼ decrypt_db.py
favorite.db (解析后)
      │
      ▼ export_favorites.py
favorites_all.csv
      │
      ▼ classify_favorites.py [--llm]
articles_final.csv + cat_*.csv
      │
      ▼ import_ima.py
IMA 知识库
```

## 分类体系

### 一级分类（9类）

| 分类 | 关键词示例 |
|------|-----------|
| 生物医药 | 创新药、ADC、CAR-T、mRNA、临床试验、靶点、抗体 |
| AI科技 | GPT、大模型、Agent、RAG、芯片、GPU、NVIDIA |
| 投资金融 | IPO、融资、科创板、估值、基金、VC、PE |
| 科学研究 | Nature、Science、论文、神经科学、突破 |
| 商业财经 | 企业战略、行业分析、商业模式、宏观 |
| 生活方式 | 健康、运动、旅行、读书、电影 |
| 媒体资讯 | 新闻、热点、评论、舆论 |
| 政治国际 | 国际关系、地缘政治、中美、外交 |
| 其他 | 未命中以上分类 |

### 二级标签（57个）

每个一级分类下设细分标签，关键词匹配自动识别：

| 一级分类 | 二级标签示例 |
|---------|-------------|
| 生物医药 | ADC、CAR-T、mRNA、创新药、临床、神经科学、免疫治疗、基因编辑、疫苗、医疗器械... |
| AI科技 | 大模型、AI应用、AI医疗、自动驾驶、机器人、GPU、芯片、深度学习、RAG、Agent... |
| 投资金融 | VC/PE、二级市场、IPO、并购、估值、私募、公募、债券、量化... |
| 科学研究 | 神经科学、物理、化学、生物、材料、天文学、量子计算... |
| 商业财经 | 企业战略、行业分析、商业模式、宏观经济、消费、零售... |
| 生活方式 | 健康、运动、旅行、读书、电影、美食、教育... |

完整标签列表见 `references/classification.md`。

### 跨领域标签（6类）

识别跨领域主题，多标签组合：

| 跨领域标签 | 触发条件 |
|-----------|---------|
| 生物医药+投资 | 医药领域 + 融资/IPO/估值关键词 |
| AI+医疗 | AI领域 + 医疗/医院/诊断关键词 |
| AI+投资 | AI领域 + 融资/IPO/估值关键词 |
| 生物医药+AI | 医药领域 + AI/大模型关键词 |
| 商业+政治 | 商业领域 + 国际关系/政策关键词 |
| 科学+政策 | 科学领域 + 政策/监管关键词 |

## LLM 二次分类

关键词分类置信度不足时，可启用 LLM 二次分类进行智能重判：

```bash
# 置信度低于 0.4 时触发 LLM
python classify_favorites.py --llm

# 全量 LLM 分类（跳过关键词）
python classify_favorites.py --llm-only

# 自定义触发阈值
python classify_favorites.py --llm --llm-threshold 0.3
```

**环境变量配置：**

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LLM_API_URL` | `http://localhost:4200/v1/chat/completions` | API 地址 |
| `LLM_MODEL` | `auto` | 模型名称 |
| `LLM_CONCURRENCY` | `5` | 最大并发数 |
| `LLM_BATCH_SIZE` | `10` | 每批处理数量 |

**OpenRouter 配置示例：**

```bash
export LLM_API_URL="https://openrouter.ai/api/v1/chat/completions"
export LLM_MODEL="deepseek/deepseek-chat"
export LLM_API_KEY="your-openrouter-api-key"
```

## 输出文件说明

| 文件 | 内容 |
|------|------|
| `favorites_all.csv` | 全部收藏记录 |
| `articles_final.csv` | 带 `category`、`subcategory`、`cross_domain` 标签的文章 |
| `cat_*.csv` | 各分类单独文件 |
| `llm_checkpoint.json` | LLM 分类断点（增量处理） |
| `ima_import_state.json` | IMA 导入进度（断点续传） |
| `ima_import.log` | IMA 导入日志 |

**CSV 字段说明：**

| 字段 | 说明 |
|------|------|
| `local_id` | 原始记录 ID |
| `title` | 文章标题 |
| `url` | 文章链接 |
| `desc` | 摘要 |
| `source` | 来源公众号 |
| `create_time` | 收藏时间 |
| `category` | 一级分类 |
| `subcategory` | 二级标签（多个用逗号分隔） |
| `cross_domain` | 跨领域标签（多个用逗号分隔） |
| `confidence` | 分类置信度 |

## favorite.db 表结构

```sql
CREATE TABLE fav_db_item (
    local_id INTEGER PRIMARY KEY,
    fav_local_type INTEGER,  -- 类型：1=文章, 3=图片, 等
    status INTEGER,
    create_time INTEGER,     -- 收藏时间戳
    source_id TEXT,          -- 来源 wxid
    source_type INTEGER,
    content BLOB,            -- XML 内容
    WCDB_CT_content INTEGER  -- 压缩标记：4=zstd
);
```

content 字段解析：
- `<title>` 标题
- `<url>` 链接
- `<source>` 来源公众号
- `<description>` 摘要

## 常见问题

**Q: 收藏数据不完整？**
A: 检查 `favorite.db` 最后修改时间，微信可能未同步最新数据。

**Q: IMA 导入被限流？**
A: API 限流约 200 次/小时，脚本已内置 3 秒/批的限速。

**Q: 如何新增分类？**
A: 编辑 `classify_favorites.py` 中的 `CATEGORIES` 字典。

**Q: 解析失败？**
A: 确保密钥正确，检查 `all_keys.json` 是否包含 `favorite.db` 的密钥。

**Q: LLM 分类中断了怎么办？**
A: 脚本自动保存断点到 `llm_checkpoint.json`，重新运行会从中断处继续。

## 技术细节

### SQLCipher 4 参数

- 加密：AES-256-CBC + HMAC-SHA512
- KDF：PBKDF2-HMAC-SHA512，256,000 iterations
- 页面：4096 bytes，reserve = 80

### 支持平台

| 平台 | 解析支持 |
|------|---------|
| Windows | ✅ |
| Linux | ✅ |
| macOS | ✅ |

## 相关链接

- 本技能仓库：https://github.com/GeoSun/wechat-favorites-skill

## 参考资料

- [references/schema.md](references/schema.md) — 数据库结构详解
- [references/classification.md](references/classification.md) — 分类算法说明

## 更新日志

### v1.1 — 2026-04

- **分类体系升级**：新增三级分类体系——9大主类、57个二级标签、6个跨领域标签，分类更精细多元
- **文档全面优化**：完善 SKILL.md，补充分类逻辑说明、LLM 使用指南、实测数据、文件格式说明
- **快速上手简化**：精简配置示例、优化命令说明、增强引导提示、补充常用触发词，方便快速上手
- **LLM 智能增强（可选）**：新增 LLM 辅助分类脚本（llm_classify.py、llm_incremental.py、merge_llm_results.py、normalize_categories.py），低置信度或模糊条目可交由大模型重新分类
- **安全说明强化**：新增`## 安全说明`章节，强调本地化、隐私保护与数据安全
- **版本升级**：1.1.0 → 1.1，新显示名（微信收藏知识库）

## License

MIT License

## 免责声明

本工具仅供个人备份和学习使用。请勿用于任何商业用途或违法行为。解析的数据仅限个人所有，不得传播或用于侵犯他人隐私。
