<div align="center">

# 🔄 DirSync

**轻量级智能目录对比与同步引擎**

**Lightweight Intelligent Directory Comparison & Synchronization Engine**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-12%20passed-success.svg)]()

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

</div>

---

## 简体中文

### 🎉 项目介绍

DirSync 是一款**零依赖**的轻量级智能目录对比与同步工具，专为开发者和系统管理员设计。它能够智能识别目录间的差异，支持多种同步模式，并提供详细的对比报告。

**灵感来源**：在日常开发工作中，我们经常需要对比和同步不同环境的代码目录、备份数据或部署文件。现有的工具要么过于复杂，要么依赖众多。DirSync 旨在提供一个**简单、快速、可靠**的解决方案。

**自研差异化亮点**：
- ✅ **纯Python实现**，零外部依赖，单文件即可运行
- ✅ **智能差异检测**，支持文件大小、修改时间、MD5哈希多重对比
- ✅ **.gitignore风格忽略规则**，灵活配置需要排除的文件
- ✅ **三种同步模式**，满足不同场景需求
- ✅ **预览模式**，先查看变更再执行，避免误操作

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **智能对比** | 支持文件大小、修改时间、MD5哈希值多重对比 |
| 🔄 **多模式同步** | 镜像模式、更新模式、双向同步模式 |
| 🚫 **灵活忽略** | 支持.gitignore风格的忽略规则配置 |
| 👁️ **预览模式** | 先预览变更，确认后再执行 |
| 📊 **详细报告** | 生成文本/JSON格式的对比报告 |
| 🛡️ **安全可靠** | 保留文件元数据，支持冲突检测 |
| ⚡ **高性能** | 优化的扫描算法，处理大目录依然流畅 |
| 🌐 **跨平台** | 支持Linux、macOS、Windows |

### 🚀 快速开始

#### 环境要求
- Python 3.8 或更高版本
- 无需任何外部依赖

#### 安装

**方式一：直接使用**
```bash
# 克隆仓库
git clone https://github.com/gitstq/DirSync.git
cd DirSync

# 直接使用
python3 dirsync.py --help
```

**方式二：安装为系统命令**
```bash
# 安装
pip install -e .

# 使用
dirsync --help
```

#### 快速使用

```bash
# 1. 对比两个目录
dirsync compare /path/to/source /path/to/target

# 2. 同步目录（更新模式）
dirsync sync /path/to/source /path/to/target --mode update

# 3. 预览同步变更（不实际执行）
dirsync sync /path/to/source /path/to/target --mode mirror --dry-run

# 4. 初始化忽略文件
dirsync init /path/to/source
```

### 📖 详细使用指南

#### 对比模式

```bash
# 基础对比
dirsync compare ./project-v1 ./project-v2

# 不使用哈希对比（加快速度）
dirsync compare ./source ./target --no-hash

# 输出JSON格式报告
dirsync compare ./source ./target --format json -o report.json

# 自定义忽略模式
dirsync compare ./source ./target -i "*.log" -i "temp/"
```

#### 同步模式

**更新模式 (update)** - 仅复制新文件和修改过的文件：
```bash
dirsync sync ./source ./backup --mode update
```

**镜像模式 (mirror)** - 使目标与源完全一致：
```bash
dirsync sync ./source ./backup --mode mirror
```

**双向同步 (bidirectional)** - 双向合并变更：
```bash
dirsync sync ./folder-a ./folder-b --mode bidirectional --conflict newer
```

#### 冲突解决策略

| 策略 | 说明 |
|------|------|
| `source` | 源目录优先 |
| `target` | 目标目录优先 |
| `newer` | 较新文件优先（默认） |
| `larger` | 较大文件优先 |
| `skip` | 跳过冲突 |

#### 忽略规则配置

在项目根目录创建 `.dirsyncignore` 文件：

```gitignore
# 版本控制
.git
.svn

# 依赖目录
node_modules
vendor
__pycache__

# IDE配置
.idea
.vscode
*.swp

# 日志和临时文件
*.log
*.tmp
tmp/

# 否定模式（不忽略）
!important.log
```

### 💡 设计思路与迭代规划

#### 技术选型原因
- **纯Python标准库**：确保零依赖，便于部署和分发
- **MD5哈希算法**：平衡速度和准确性，适合文件对比场景
- **dataclass**：类型安全，代码清晰
- **pathlib**：现代化的路径处理，跨平台兼容

#### 后续功能迭代计划

**v1.1.0 (计划中)**
- [ ] 增量同步支持（基于时间戳）
- [ ] 并行文件处理（多线程）
- [ ] 进度条显示

**v1.2.0 (计划中)**
- [ ] 远程目录支持（SFTP/SCP）
- [ ] 定时任务集成
- [ ] 配置文件支持（YAML）

**v2.0.0 (规划中)**
- [ ] 图形界面（GUI）版本
- [ ] 文件版本历史
- [ ] 云存储集成（S3、OSS等）

### 📦 打包与部署指南

#### 打包为可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包为单文件可执行程序
pyinstaller --onefile --name dirsync dirsync.py

# 输出在 dist/ 目录
```

#### 安装为系统命令

```bash
# 开发模式安装
pip install -e .

# 生产安装
pip install .
```

### 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

**提交规范**：
- `feat:` 新功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关

### 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 繁體中文

### 🎉 專案介紹

DirSync 是一款**零依賴**的輕量級智慧目錄對比與同步工具，專為開發者和系統管理員設計。它能夠智慧識別目錄間的差異，支援多種同步模式，並提供詳細的對比報告。

**靈感來源**：在日常開發工作中，我們經常需要對比和同步不同環境的程式碼目錄、備份資料或部署檔案。現有的工具要麼過於複雜，要麼依賴眾多。DirSync 旨在提供一個**簡單、快速、可靠**的解決方案。

**自研差異化亮點**：
- ✅ **純Python實現**，零外部依賴，單檔案即可執行
- ✅ **智慧差異檢測**，支援檔案大小、修改時間、MD5雜湊多重對比
- ✅ **.gitignore風格忽略規則**，靈活配置需要排除的檔案
- ✅ **三種同步模式**，滿足不同場景需求
- ✅ **預覽模式**，先檢視變更再執行，避免誤操作

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔍 **智慧對比** | 支援檔案大小、修改時間、MD5雜湊值多重對比 |
| 🔄 **多模式同步** | 鏡像模式、更新模式、雙向同步模式 |
| 🚫 **靈活忽略** | 支援.gitignore風格的忽略規則配置 |
| 👁️ **預覽模式** | 先預覽變更，確認後再執行 |
| 📊 **詳細報告** | 生成文字/JSON格式的對比報告 |
| 🛡️ **安全可靠** | 保留檔案元資料，支援衝突檢測 |
| ⚡ **高效能** | 優化的掃描演算法，處理大目錄依然流暢 |
| 🌐 **跨平台** | 支援Linux、macOS、Windows |

### 🚀 快速開始

#### 環境要求
- Python 3.8 或更高版本
- 無需任何外部依賴

#### 安裝

**方式一：直接使用**
```bash
# 克隆倉庫
git clone https://github.com/gitstq/DirSync.git
cd DirSync

# 直接使用
python3 dirsync.py --help
```

**方式二：安裝為系統命令**
```bash
# 安裝
pip install -e .

# 使用
dirsync --help
```

#### 快速使用

```bash
# 1. 對比兩個目錄
dirsync compare /path/to/source /path/to/target

# 2. 同步目錄（更新模式）
dirsync sync /path/to/source /path/to/target --mode update

# 3. 預覽同步變更（不實際執行）
dirsync sync /path/to/source /path/to/target --mode mirror --dry-run

# 4. 初始化忽略檔案
dirsync init /path/to/source
```

### 📖 詳細使用指南

#### 對比模式

```bash
# 基礎對比
dirsync compare ./project-v1 ./project-v2

# 不使用雜湊對比（加快速度）
dirsync compare ./source ./target --no-hash

# 輸出JSON格式報告
dirsync compare ./source ./target --format json -o report.json

# 自定義忽略模式
dirsync compare ./source ./target -i "*.log" -i "temp/"
```

#### 同步模式

**更新模式 (update)** - 僅複製新檔案和修改過的檔案：
```bash
dirsync sync ./source ./backup --mode update
```

**鏡像模式 (mirror)** - 使目標與源完全一致：
```bash
dirsync sync ./source ./backup --mode mirror
```

**雙向同步 (bidirectional)** - 雙向合併變更：
```bash
dirsync sync ./folder-a ./folder-b --mode bidirectional --conflict newer
```

#### 衝突解決策略

| 策略 | 說明 |
|------|------|
| `source` | 源目錄優先 |
| `target` | 目標目錄優先 |
| `newer` | 較新檔案優先（預設） |
| `larger` | 較大檔案優先 |
| `skip` | 跳過衝突 |

#### 忽略規則配置

在專案根目錄建立 `.dirsyncignore` 檔案：

```gitignore
# 版本控制
.git
.svn

# 依賴目錄
node_modules
vendor
__pycache__

# IDE配置
.idea
.vscode
*.swp

# 日誌和臨時檔案
*.log
*.tmp
tmp/

# 否定模式（不忽略）
!important.log
```

### 💡 設計思路與迭代規劃

#### 技術選型原因
- **純Python標準庫**：確保零依賴，便於部署和分發
- **MD5雜湊演算法**：平衡速度和準確性，適合檔案對比場景
- **dataclass**：型別安全，程式碼清晰
- **pathlib**：現代化的路徑處理，跨平台相容

#### 後續功能迭代計劃

**v1.1.0 (計劃中)**
- [ ] 增量同步支援（基於時間戳）
- [ ] 並行檔案處理（多執行緒）
- [ ] 進度條顯示

**v1.2.0 (計劃中)**
- [ ] 遠端目錄支援（SFTP/SCP）
- [ ] 定時任務整合
- [ ] 配置檔案支援（YAML）

**v2.0.0 (規劃中)**
- [ ] 圖形介面（GUI）版本
- [ ] 檔案版本歷史
- [ ] 雲端儲存整合（S3、OSS等）

### 📦 打包與部署指南

#### 打包為可執行檔案

```bash
# 安裝 PyInstaller
pip install pyinstaller

# 打包為單檔案可執行程式
pyinstaller --onefile --name dirsync dirsync.py

# 輸出在 dist/ 目錄
```

#### 安裝為系統命令

```bash
# 開發模式安裝
pip install -e .

# 生產安裝
pip install .
```

### 🤝 貢獻指南

歡迎提交 Issue 和 Pull Request！

**提交規範**：
- `feat:` 新功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `test:` 測試相關

### 📄 開源協議

本專案採用 [MIT License](LICENSE) 開源協議。

---

## English

### 🎉 Project Introduction

DirSync is a **zero-dependency** lightweight intelligent directory comparison and synchronization tool designed for developers and system administrators. It intelligently identifies differences between directories, supports multiple synchronization modes, and provides detailed comparison reports.

**Inspiration**: In daily development work, we often need to compare and synchronize code directories across different environments, backup data, or deployment files. Existing tools are either too complex or have too many dependencies. DirSync aims to provide a **simple, fast, and reliable** solution.

**Differentiation Highlights**:
- ✅ **Pure Python implementation**, zero external dependencies, single file execution
- ✅ **Intelligent difference detection**, supports file size, modification time, MD5 hash comparison
- ✅ **.gitignore-style ignore rules**, flexible configuration for excluded files
- ✅ **Three sync modes**, meeting different scenario requirements
- ✅ **Preview mode**, review changes before execution to avoid mistakes

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Smart Comparison** | Supports file size, modification time, MD5 hash comparison |
| 🔄 **Multi-mode Sync** | Mirror mode, update mode, bidirectional sync mode |
| 🚫 **Flexible Ignore** | Supports .gitignore-style ignore rule configuration |
| 👁️ **Preview Mode** | Preview changes before confirming execution |
| 📊 **Detailed Reports** | Generate text/JSON format comparison reports |
| 🛡️ **Safe & Reliable** | Preserve file metadata, support conflict detection |
| ⚡ **High Performance** | Optimized scanning algorithm, handles large directories smoothly |
| 🌐 **Cross-platform** | Supports Linux, macOS, Windows |

### 🚀 Quick Start

#### Requirements
- Python 3.8 or higher
- No external dependencies required

#### Installation

**Method 1: Direct Use**
```bash
# Clone repository
git clone https://github.com/gitstq/DirSync.git
cd DirSync

# Use directly
python3 dirsync.py --help
```

**Method 2: Install as System Command**
```bash
# Install
pip install -e .

# Use
dirsync --help
```

#### Quick Usage

```bash
# 1. Compare two directories
dirsync compare /path/to/source /path/to/target

# 2. Sync directories (update mode)
dirsync sync /path/to/source /path/to/target --mode update

# 3. Preview sync changes (no actual execution)
dirsync sync /path/to/source /path/to/target --mode mirror --dry-run

# 4. Initialize ignore file
dirsync init /path/to/source
```

### 📖 Detailed Usage Guide

#### Compare Mode

```bash
# Basic comparison
dirsync compare ./project-v1 ./project-v2

# Skip hash comparison (faster)
dirsync compare ./source ./target --no-hash

# Output JSON format report
dirsync compare ./source ./target --format json -o report.json

# Custom ignore patterns
dirsync compare ./source ./target -i "*.log" -i "temp/"
```

#### Sync Mode

**Update Mode** - Only copy new and modified files:
```bash
dirsync sync ./source ./backup --mode update
```

**Mirror Mode** - Make target identical to source:
```bash
dirsync sync ./source ./backup --mode mirror
```

**Bidirectional Sync** - Merge changes both ways:
```bash
dirsync sync ./folder-a ./folder-b --mode bidirectional --conflict newer
```

#### Conflict Resolution Strategies

| Strategy | Description |
|----------|-------------|
| `source` | Source directory takes precedence |
| `target` | Target directory takes precedence |
| `newer` | Newer file takes precedence (default) |
| `larger` | Larger file takes precedence |
| `skip` | Skip conflicts |

#### Ignore Rules Configuration

Create `.dirsyncignore` file in project root:

```gitignore
# Version control
.git
.svn

# Dependencies
node_modules
vendor
__pycache__

# IDE config
.idea
.vscode
*.swp

# Logs and temp files
*.log
*.tmp
tmp/

# Negation (don't ignore)
!important.log
```

### 💡 Design Philosophy & Roadmap

#### Technical Choices
- **Pure Python Standard Library**: Ensures zero dependencies, easy deployment
- **MD5 Hash Algorithm**: Balances speed and accuracy for file comparison
- **dataclass**: Type-safe, clean code
- **pathlib**: Modern path handling, cross-platform compatible

#### Future Roadmap

**v1.1.0 (Planned)**
- [ ] Incremental sync support (timestamp-based)
- [ ] Parallel file processing (multithreading)
- [ ] Progress bar display

**v1.2.0 (Planned)**
- [ ] Remote directory support (SFTP/SCP)
- [ ] Scheduled task integration
- [ ] Configuration file support (YAML)

**v2.0.0 (In Planning)**
- [ ] GUI version
- [ ] File version history
- [ ] Cloud storage integration (S3, OSS, etc.)

### 📦 Packaging & Deployment Guide

#### Package as Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Package as single executable
pyinstaller --onefile --name dirsync dirsync.py

# Output in dist/ directory
```

#### Install as System Command

```bash
# Development mode
pip install -e .

# Production install
pip install .
```

### 🤝 Contributing

Issues and Pull Requests are welcome!

**Commit Convention**:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ by DirSync Team**

⭐ Star us on GitHub if you find this project helpful!

</div>
