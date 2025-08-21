# Telegram Notion Uploader

**Telegram Notion Uploader** 是一个基于 Docker 的自动化系统，可以将 Telegram 中的媒体文件无缝同步到 Notion 数据库。本项目基于优秀的开源项目 [SaveAny Bot](https://github.com/krau/SaveAny-Bot) 构建，提供了完整的 Telegram 媒体文件自动转存解决方案。

[English](./README_EN.md) | 中文

## ✨ 核心功能

- 🤖 **智能分类**：单文件创建独立页面，相册文件合并到同一页面
- 🎬 **视频缩略图**：自动为视频生成缩略图并设置为页面封面
- 📁 **文件夹稳定检测**：等待文件夹稳定后统一处理，避免文件丢失
- 🔄 **分块上传**：支持大文件分块上传，突破文件大小限制
- 🐳 **一键部署**：基于 Docker Compose，部署简单快捷

## 🏗️ 系统架构

本项目由两个核心服务组成：
- **SaveAny Bot**：负责 Telegram 媒体文件下载（基于 [krau/SaveAny-Bot](https://github.com/krau/SaveAny-Bot)）
- **Notion Uploader**：自动监控下载目录并上传到 Notion 数据库

```
Telegram → SaveAny Bot → /downloads (共享卷) → Notion Uploader → Notion 数据库
```

## 🚀 快速开始

### 前置要求

- Docker 和 Docker Compose
- Telegram Bot Token（从 [@BotFather](https://t.me/BotFather) 获取）
- Notion API Token 和数据库 ID

### 1. 克隆项目

```bash
git clone https://github.com/RanceLee233/telegram-notion-uploader.git
cd telegram-notion-uploader
```

### 2. 配置 Telegram Bot

复制并配置 SaveAny Bot 配置文件：

```bash
cp saveanybot_data/config.toml.example saveanybot_data/config.toml
```

编辑 `saveanybot_data/config.toml`，设置：
- `token`：你的 Telegram Bot Token
- `users.id`：你的 Telegram 用户 ID

### 3. 配置 Notion

复制并配置 Notion 环境变量：

```bash
cp notion_uploader_data/.env.example notion_uploader_data/.env
```

编辑 `notion_uploader_data/.env`，设置：
- `NOTION_TOKEN`：你的 Notion Integration Token
- `NOTION_DATABASE_ID`：目标 Notion 数据库 ID

### 4. 启动服务

```bash
docker compose up -d --build
```

### 5. 配置 Telegram Bot 规则

在 Telegram 中向你的 Bot 发送以下命令：

```
/rule switch                                     # 如果没开规则模式先打开
/rule del 1                                      # (可选) 删掉之前那条错误规则
/rule add IS-ALBUM true VPS_Downloads NEW-FOR-ALBUM  # 如果要整体下载和上传，必须打开
/rule list                                       # 确认：应看到 1: IS-ALBUM true VPS_Downloads NEW-FOR-ALBUM
```

> ⚠️ **重要提示**：请务必参考 [SaveAny Bot 官方文档](https://github.com/krau/SaveAny-Bot) 了解完整的配置选项和规则设置。本项目的核心下载功能完全依赖于 SaveAny Bot 的优秀实现。

## 📋 详细配置

### Notion 集成设置

1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 创建新的 Integration
3. 获取 Internal Integration Token
4. 在目标数据库中添加 Integration 权限

### 数据库属性要求

你的 Notion 数据库需要包含以下属性：
- **名称**（标题类型）：页面标题
- **文件和媒体**（文件类型）：存储媒体文件

### 文件处理规则

- **单文件**：直接在根目录的文件会创建单独的 Notion 页面
- **相册/多文件**：文件夹中的多个文件会等待 60 秒稳定后合并到单个页面
- **视频处理**：自动生成缩略图并设置为页面封面

## 🔧 常用命令

### 查看日志

```bash
# 查看下载日志
docker compose logs -f saveanybot

# 查看上传日志
docker compose logs -f notion_uploader
```

### 重启服务

```bash
# 重新构建并启动 Notion Uploader
docker compose build notion_uploader
docker compose up -d notion_uploader

# 完整重启
docker compose down
docker compose up -d --build
```

### 清理下载文件

```bash
# 清空下载文件夹
docker compose exec notion_uploader find /downloads -mindepth 1 -delete
```

## 📝 文件大小限制

- 单文件上传限制：20MB
- 大文件自动分块上传，分块大小：19MB
- 文件夹稳定检测延迟：60秒

## 🐛 故障排除

### 常见问题

1. **文件无法上传到 Notion**
   - 检查 `NOTION_TOKEN` 和 `NOTION_DATABASE_ID` 是否正确
   - 确认 Notion Integration 有数据库访问权限

2. **Telegram Bot 无响应**
   - 检查 `config.toml` 中的 Bot Token
   - 确认 Bot 已启动并添加了用户规则

3. **视频缩略图生成失败**
   - 容器内已预装 ffmpeg，检查视频文件格式是否支持

4. **文件夹处理异常**
   - 查看 `notion_uploader` 日志获取详细错误信息
   - 确认文件路径和权限正常

### 日志分析

```bash
# 实时监控所有日志
docker compose logs -f

# 只查看错误日志
docker compose logs saveanybot | grep -i error
docker compose logs notion_uploader | grep -i error
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [SaveAny Bot](https://github.com/krau/SaveAny-Bot) - 优秀的 Telegram 媒体下载机器人
- [Notion API](https://developers.notion.com/) - 强大的 Notion 集成 API

---

如果这个项目对你有帮助，请给个 ⭐️！