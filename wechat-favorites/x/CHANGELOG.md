# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-04-22

### Added / 新增

- **CLI & Environment Variable Support** — Restored command-line arguments and environment variables for `import_ima.py`
  - `--csv`, `--kb-id`, `--client-id`, `--api-key`, `--state`, `--log`, `--batch-size`
  - Environment variables: `IMA_CLIENT_ID`, `IMA_API_KEY`, `IMA_KB_ID`
  - Priority: CLI args > Environment variables > config.json > ~/.config/ima/
  
  **命令行与环境变量支持** — 恢复 `import_ima.py` 的命令行参数和环境变量配置
  - 支持参数：`--csv`, `--kb-id`, `--client-id`, `--api-key`, `--state`, `--log`, `--batch-size`
  - 环境变量：`IMA_CLIENT_ID`, `IMA_API_KEY`, `IMA_KB_ID`
  - 优先级：命令行 > 环境变量 > config.json > ~/.config/ima/

- **Quick Validation Script** — Added `scripts/quick_validate.py` to check dependencies and configuration
  - Python version, dependencies, config file, decrypted DB, IMA credentials
  
  **快速验证脚本** — 新增 `scripts/quick_validate.py` 检查依赖和配置
  - 检查 Python 版本、依赖包、配置文件、解密数据库、IMA 凭证

- **LICENSE.txt** — Added MIT License file
  
  **许可证文件** — 新增 MIT License 文件

- **.gitignore** — Prevent sensitive data from being committed
  - Excludes: config.json, decrypted/, *.db, exported_favorites/, *.csv, state files
  
  **.gitignore** — 防止敏感数据被提交
  - 排除：config.json, decrypted/, *.db, exported_favorites/, *.csv, 状态文件

### Fixed / 修复

- **import_ima.py batch counting** — Unified batch counter, removed duplicate `batch_count` variable
  
  **batch 计数修复** — 统一 batch 计数器，移除重复的 `batch_count` 变量

- **import_ima.py rate-limit state** — Now saves state before sleep, preventing progress loss
  
  **限流状态保存修复** — 限流睡眠前先保存状态，防止进度丢失

- **classify_favorites.py cross-platform** — Replaced hardcoded Windows path separator `\\` with `os.path.join()`
  
  **跨平台路径修复** — 替换 Windows 硬编码路径分隔符为 `os.path.join()`

### Changed / 变更

- **Documentation improved** — Updated SKILL.md with validation step and CLI usage examples
  
  **文档改进** — 更新 SKILL.md，添加验证步骤和命令行使用示例

---

## [1.0.1] - 2026-04-22

### Added / 新增

- Initial release / 初始发布
- Export WeChat favorites from decrypted favorite.db / 从解密的 favorite.db 导出微信收藏
- Multi-tag classification (Biotech, AI, Investment, Science, Business, etc.) / 多标签分类（生物医药、AI、投资、科学、商业等）
- Batch import to IMA knowledge base with resume support / 批量导入 IMA 知识库（支持断点续传）
- Classification report generation / 分类报告生成

---

## Configuration Priority (v1.1.0+)

| Priority | Method | Example |
|----------|--------|---------|
| 1 (highest) | CLI args | `--kb-id YOUR_KB_ID` |
| 2 | Environment variables | `IMA_KB_ID=xxx` |
| 3 | config.json | `{"ima_kb_id": "xxx"}` |
| 4 | ~/.config/ima/ | `client_id`, `api_key` files |

## 配置优先级（v1.1.0+）

| 优先级 | 方式 | 示例 |
|--------|------|------|
| 1（最高） | 命令行参数 | `--kb-id YOUR_KB_ID` |
| 2 | 环境变量 | `IMA_KB_ID=xxx` |
| 3 | config.json | `{"ima_kb_id": "xxx"}` |
| 4 | ~/.config/ima/ | `client_id`, `api_key` 文件 |
