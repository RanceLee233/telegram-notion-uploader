# Telegram Notion Uploader

**Telegram Notion Uploader** is a Docker-based automation system that seamlessly syncs media files from Telegram to Notion databases. Built upon the excellent open-source [SaveAny Bot](https://github.com/krau/SaveAny-Bot) project, it provides a complete solution for automatic Telegram media archiving.

English | [中文](./README.md)

## ✨ Key Features

- 🤖 **Smart Organization**: Single files create individual pages, albums merge into unified pages
- 🎬 **Video Thumbnails**: Auto-generate video thumbnails and set as page covers
- 📁 **Folder Stability Detection**: Wait for folder stability before processing to prevent file loss
- 🔄 **Chunked Upload**: Support large file chunked uploads, bypassing size limitations
- 🐳 **One-Click Deploy**: Docker Compose based, simple and fast deployment

## 🏗️ System Architecture

The project consists of two core services:
- **SaveAny Bot**: Handles Telegram media file downloads (based on [krau/SaveAny-Bot](https://github.com/krau/SaveAny-Bot))
- **Notion Uploader**: Automatically monitors download directory and uploads to Notion database

```
Telegram → SaveAny Bot → /downloads (shared volume) → Notion Uploader → Notion Database
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- Notion API Token and Database ID

### 1. Clone the Repository

```bash
git clone https://github.com/RanceLee233/telegram-notion-uploader.git
cd telegram-notion-uploader
```

### 2. Configure Telegram Bot

Copy and configure the SaveAny Bot configuration file:

```bash
cp saveanybot_data/config.toml.example saveanybot_data/config.toml
```

Edit `saveanybot_data/config.toml` and set:
- `token`: Your Telegram Bot Token
- `users.id`: Your Telegram User ID

### 3. Configure Notion

Copy and configure Notion environment variables:

```bash
cp notion_uploader_data/.env.example notion_uploader_data/.env
```

Edit `notion_uploader_data/.env` and set:
- `NOTION_TOKEN`: Your Notion Integration Token
- `NOTION_DATABASE_ID`: Target Notion Database ID

### 4. Start Services

```bash
docker compose up -d --build
```

### 5. Configure Telegram Bot Rules

Send the following commands to your Bot in Telegram:

```
/rule switch                                     # Enable rule mode if not already enabled
/rule del 1                                      # (Optional) Delete previous incorrect rule
/rule add IS-ALBUM true VPS_Downloads NEW-FOR-ALBUM  # Required for batch download and upload
/rule list                                       # Confirm: should see 1: IS-ALBUM true VPS_Downloads NEW-FOR-ALBUM
```

> ⚠️ **Important**: Please refer to the [SaveAny Bot official documentation](https://github.com/krau/SaveAny-Bot) for complete configuration options and rule settings. This project's core download functionality relies entirely on the excellent implementation of SaveAny Bot.

## 📋 Detailed Configuration

### Notion Integration Setup

1. Visit [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new Integration
3. Get the Internal Integration Token
4. Add Integration permissions to your target database

### Database Properties Requirements

Your Notion database needs the following properties:
- **名称** (Title type): Page title
- **文件和媒体** (Files type): Store media files

### File Processing Rules

- **Single Files**: Files directly in root directory create individual Notion pages
- **Albums/Multiple Files**: Multiple files in folders wait 60 seconds for stability then merge into single page
- **Video Processing**: Auto-generate thumbnails and set as page covers

## 🔧 Common Commands

### View Logs

```bash
# View download logs
docker compose logs -f saveanybot

# View upload logs
docker compose logs -f notion_uploader
```

### Restart Services

```bash
# Rebuild and restart Notion Uploader
docker compose build notion_uploader
docker compose up -d notion_uploader

# Complete restart
docker compose down
docker compose up -d --build
```

### Clean Download Files

```bash
# Clear download folder
docker compose exec notion_uploader find /downloads -mindepth 1 -delete
```

## 📝 File Size Limits

- Single file upload limit: 20MB
- Large files automatically use chunked upload, chunk size: 19MB
- Folder stability detection delay: 60 seconds

## 🐛 Troubleshooting

### Common Issues

1. **Files cannot upload to Notion**
   - Check if `NOTION_TOKEN` and `NOTION_DATABASE_ID` are correct
   - Ensure Notion Integration has database access permissions

2. **Telegram Bot not responding**
   - Check Bot Token in `config.toml`
   - Ensure Bot is started and user rules are added

3. **Video thumbnail generation fails**
   - ffmpeg is pre-installed in container, check if video format is supported

4. **Folder processing exceptions**
   - Check `notion_uploader` logs for detailed error information
   - Ensure file paths and permissions are correct

### Log Analysis

```bash
# Monitor all logs in real-time
docker compose logs -f

# View error logs only
docker compose logs saveanybot | grep -i error
docker compose logs notion_uploader | grep -i error
```

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

## 🙏 Acknowledgments

- [SaveAny Bot](https://github.com/krau/SaveAny-Bot) - Excellent Telegram media download bot
- [Notion API](https://developers.notion.com/) - Powerful Notion integration API

---

If this project helps you, please give it a ⭐️!