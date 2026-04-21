# WeChat Data Tools for QClaw

微信本地数据解密与整理工具集，为 [QClaw](https://github.com/qclaw/qclaw) 提供 Skill 封装。

## 包含技能

### 1. wechat-decrypt

微信 4.x 数据库解密与消息查询。

**核心能力：**
- 从运行中的微信进程内存提取 SQLCipher 4 加密密钥（Windows/macOS/Linux）
- 解密所有本地数据库（message、contact、session、favorite 等）
- MCP Server 提供消息查询、联系人搜索、图片解密等工具
- Web UI 实时消息监听

**触发词：** 微信解密、聊天记录、微信数据库、微信消息搜索、微信MCP

### 2. wechat-favorites

微信收藏夹导出、分类与知识库管理。

**核心能力：**
- 从解密后的 `favorite.db` 导出收藏记录
- 多标签智能分类（生物医药、AI、投资、科学等）
- 批量导入 IMA 知识库（支持断点续传）
- 生成分类报告、年度趋势、热门话题

**触发词：** 微信收藏、收藏夹导出、收藏分类、IMA导入

## 前置条件

- Python 3.10+
- 微信 4.x 正在运行并登录
- Windows 需要管理员权限（读取进程内存）

```bash
pip install pycryptodome zstandard mcp[cli] psutil
```

## 快速开始

### 1. 解密数据库

```bash
cd wechat-decrypt

# 提取密钥 + 启动 Web UI
python main.py

# 或：提取密钥 + 解密全部数据库
python main.py decrypt
```

首次运行自动检测微信数据目录并生成 `config.json`。

### 2. 整理收藏夹

```bash
# 导出收藏记录（需要先解密）
python export_favorites.py

# 分类
python classify_favorites.py

# 导入 IMA 知识库
python ima_batch_import.py
```

## 目录结构

```
wechat-decrypt/
├── main.py                  # 一键启动入口
├── find_all_keys.py         # 跨平台密钥提取
├── decrypt_db.py            # 全量解密
├── mcp_server.py            # MCP Server
├── monitor_web.py           # Web UI
├── decode_image.py          # 图片解密
├── config.json              # 运行时配置
├── all_keys.json            # 提取的密钥
├── decrypted/               # 解密输出
├── exported_favorites/      # 收藏导出
│   ├── articles_final.csv   # 带分类标签
│   └── classification_report.md
└── ima_batch_import.py      # IMA 导入
```

## MCP 工具列表

| 工具 | 说明 |
|------|------|
| `get_recent_sessions(limit)` | 最近会话列表 |
| `get_chat_history(chat_name, limit, offset, start_time, end_time)` | 聊天消息记录 |
| `search_messages(keyword, chat_name, start_time, end_time, limit)` | 搜索消息 |
| `get_contacts(query, limit)` | 搜索/列出联系人 |
| `get_contact_tags()` | 联系人标签列表 |
| `get_tag_members(tag_name)` | 标签成员 |
| `decode_image(chat_name, local_id)` | 解密图片 |
| `get_chat_images(chat_name, limit)` | 列出聊天图片 |

## 技术细节

### SQLCipher 4 参数

- 加密：AES-256-CBC + HMAC-SHA512
- KDF：PBKDF2-HMAC-SHA512，256,000 iterations
- 页面：4096 bytes，reserve = 80

### 支持平台

| 平台 | 密钥提取 | 说明 |
|------|---------|------|
| Windows | ✅ | 扫描 Weixin.exe/WeChat.exe 进程内存 |
| Linux | ✅ | 扫描 wechat 进程 /proc/<pid>/mem |
| macOS | ✅ | Mach VM API 扫描 |

### 收藏分类体系

| 分类 | 关键词示例 |
|------|-----------|
| 生物医药 | 创新药、ADC、CAR-T、mRNA、临床试验 |
| AI/科技 | GPT、大模型、Agent、RAG、芯片 |
| 投资/金融 | IPO、融资、科创板、估值、基金 |
| 科学/研究 | 神经科学、Nature、Science、论文 |
| 商业/财经 | 企业战略、行业分析、商业模式 |

## 注意事项

1. **Weixin.exe vs WeChat.exe**：Windows Store 版进程名为 Weixin.exe
2. **数据库时效性**：本地数据库可能不包含最新数据，检查 DB 最后修改时间
3. **API 频率限制**：IMA OpenAPI 约 200 次/小时，已内置限速
4. **编码问题**：微信数据库中文可能是 GBK，导出时需转 UTF-8

## 致谢

核心解密逻辑基于 [ylytdeng/wechat-decrypt](https://github.com/ylytdeng/wechat-decrypt)（2315 stars）。

## License

MIT License

## 免责声明

本项目仅供个人学习和研究使用。请勿用于任何商业用途或违法行为。使用本工具解密的数据仅限个人所有，不得传播或用于侵犯他人隐私。