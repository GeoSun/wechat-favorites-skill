---
name: wechat-favorites
description: 微信收藏夹导出、分类与知识库管理。当用户提到微信收藏、收藏夹导出、收藏文章分类、IMA知识库导入、收藏整理时触发。支持从解密后的 favorite.db 导出收藏记录、智能分类（生物医药/AI/投资等）、批量导入IMA知识库。
---

# WeChat Favorites Skill

微信收藏夹导出、智能分类与知识库管理工具。

## 核心能力

| 能力 | 说明 |
|------|------|
| **收藏导出** | 从解密后的 `favorite.db` 导出全部收藏记录为 CSV |
| **智能分类** | 多标签分类（生物医药、AI、投资、科学、商业等） |
| **IMA导入** | 批量导入到 IMA 知识库，支持断点续传 |
| **报告生成** | 分类统计、各分类 CSV 导出 |

## 前置条件

### 1. 微信数据库解密

本 skill 依赖已解密的 `favorite.db`。需先完成：

```bash
# 使用 wechat-decrypt 或其他工具解密微信数据库
# 输出: decrypted/favorite/favorite.db
```

解密方案（任选其一）：
- **wechat-decrypt**：https://github.com/GeoSun/wechat-favorites-skill
- 手动提取密钥 + SQLCipher 解密

### 2. Python 环境

```bash
pip install pycryptodome zstandard
```

### 3. IMA 导入（可选）

如需导入 IMA 知识库：
1. 创建 IMA 知识库，获取 `kb_id`
2. 配置凭证：`~/.config/ima/client_id` 和 `~/.config/ima/api_key`

### 4. 配置文件

在项目目录创建 `config.json`：

```json
{
  "db_dir": "/path/to/wechat/data",
  "keys_file": "/path/to/all_keys.json",
  "decrypted_dir": "decrypted",
  "ima_kb_id": "your_kb_id"
}
```

字段说明：
- `db_dir`: 微信数据库路径
- `keys_file`: 密钥文件路径（由 wechat-decrypt 生成）
- `decrypted_dir`: 解密输出目录
- `ima_kb_id`: IMA 知识库 ID（可选）

### 5. IMA 导入配置（可选）

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

# 方式 3: 配置文件（推荐）
# 在项目目录创建 config.json，填写 ima_kb_id
# 创建 ~/.config/ima/client_id 和 api_key 文件
```

## 快速开始

```bash
cd scripts

# 0. 验证环境
python quick_validate.py

# 1. 解密数据库（如未解密）
python decrypt_db.py

# 2. 导出收藏记录
python export_favorites.py

# 3. 智能分类
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
│   ├── decrypt_db.py            # 数据库解密
│   ├── export_favorites.py      # 收藏导出
│   ├── classify_favorites.py    # 智能分类
│   ├── import_ima.py            # IMA 导入
│   ├── config.py                # 配置加载
│   └── key_utils.py             # 密钥工具
├── decrypted/                   # 解密输出
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
favorite.db (解密)
      │
      ▼ export_favorites.py
favorites_all.csv
      │
      ▼ classify_favorites.py
articles_final.csv + cat_*.csv
      │
      ▼ import_ima.py
IMA 知识库
```

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

## 分类体系

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

自定义分类：编辑 `scripts/classify_favorites.py` 中的 `CATEGORIES` 字典。

## 输出文件说明

| 文件 | 内容 |
|------|------|
| `favorites_all.csv` | 全部收藏记录 |
| `articles_final.csv` | 带 `categories` 标签的文章 |
| `cat_*.csv` | 各分类单独文件 |
| `ima_import_state.json` | IMA 导入进度（断点续传） |
| `ima_import.log` | IMA 导入日志 |

## 常见问题

**Q: 收藏数据不完整？**
A: 检查 `favorite.db` 最后修改时间，微信可能未同步最新数据。

**Q: IMA 导入被限流？**
A: API 限流约 200 次/小时，脚本已内置 3 秒/批的限速。

**Q: 如何新增分类？**
A: 编辑 `classify_favorites.py` 中的 `CATEGORIES` 字典。

**Q: 解密失败？**
A: 确保密钥正确，检查 `all_keys.json` 是否包含 `favorite.db` 的密钥。

## 技术细节

### SQLCipher 4 参数

- 加密：AES-256-CBC + HMAC-SHA512
- KDF：PBKDF2-HMAC-SHA512，256,000 iterations
- 页面：4096 bytes，reserve = 80

### 支持平台

| 平台 | 解密支持 |
|------|---------|
| Windows | ✅ |
| Linux | ✅ |
| macOS | ✅ |

## 相关链接

- 完整 wechat-decrypt：https://github.com/GeoSun/wechat-favorites-skill
- 原始解密逻辑：https://github.com/ylytdeng/wechat-decrypt

## 参考资料

- [references/schema.md](references/schema.md) — 数据库结构详解
- [references/classification.md](references/classification.md) — 分类算法说明

## License

MIT License

## 免责声明

本工具仅供个人备份和学习使用。请勿用于任何商业用途或违法行为。解密的数据仅限个人所有，不得传播或用于侵犯他人隐私。
