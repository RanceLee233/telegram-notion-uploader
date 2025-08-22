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

## 🚀 Deployment Options

This project offers two deployment methods - choose based on your needs:

### 🐳 Docker Deployment (Recommended)
**For**: Users familiar with Docker  
**Pros**: Environment isolation, simple deployment, good stability

### 💻 Local Deployment
**For**: Users who prefer not to use Docker  
**Pros**: Easier debugging, direct control, lower resource usage

📖 **Complete Tutorial**: [Local Deployment Guide](local_deployment/README_LOCAL.md)

---

## 🚀 Docker Quick Start

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

---

## 📚 Complete Beginner Tutorial

### 🔰 First Time Users Start Here

If you're new to Telegram Bots or Notion API, follow this detailed tutorial:

#### Step 1: Create Telegram Bot (Visual Guide)

1. **Open Telegram**
   - Open Telegram app on your phone or computer
   - Register an account if you don't have one

2. **Find BotFather**
   - Search for `@BotFather` in the search box
   - Click the first result (with blue verification checkmark)

3. **Create New Bot**
   - Send `/newbot` command
   - BotFather will ask for bot name, e.g., `My Notion Uploader Bot`
   - Then ask for username (must end with bot), e.g., `my_notion_uploader_bot`
   - On success, BotFather sends a message with the Token

4. **Save Token**
   ```
   Example: 1234567890:ABCdefGhIjKlMnOpQrStUvWxYz
   ```
   ⚠️ **Important**: Save this Token securely, you'll need it later

#### Step 2: Setup Notion (Visual Guide)

1. **Create Notion Account**
   - Visit [notion.so](https://notion.so) to register
   - Login if you already have an account

2. **Create Database**
   - Create a new page in Notion
   - Add a database (select "Table")
   - Set database properties:
     - **Name** (Title type) - for page titles
     - **Files & Media** (Files type) - for media files

3. **Create Integration**
   - Visit [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Click "+ New integration"
   - Fill in details:
     - **Name**: Telegram Uploader
     - **Associated workspace**: Select your workspace
     - **Type**: Internal integration
   - Click "Submit"
   - Copy the generated **Internal Integration Token**

4. **Add Database Permissions**
   - Open your created database page
   - Click the "..." menu in top right
   - Select "Add connections"
   - Find and select your Integration

5. **Get Database ID**
   ```
   Database URL: https://notion.so/username/1234567890abcdef1234567890abcdef?v=...
   Database ID: 1234567890abcdef1234567890abcdef (32-character string)
   ```

#### Step 3: Get Telegram User ID

**Method 1: Using @userinfobot (Recommended)**
1. Search for `@userinfobot` in Telegram
2. Click "Start" or send `/start`
3. Bot returns your user info, note the User ID

**Method 2: Using @RawDataBot**
1. Search for `@RawDataBot` in Telegram
2. Send any message
3. Bot returns detailed info, find the `"id"` field


## 📋 Detailed Configuration

### Notion Integration Setup

1. Visit [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new Integration
3. Get the Internal Integration Token
4. Add Integration permissions to your target database

### Database Properties Requirements

Your Notion database needs the following properties:
- **Name** (Title type): Page title
- **Files & Media** (Files type): Store media files

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

### Detailed Guides

For comprehensive troubleshooting and setup guides:
- 📖 [Complete FAQ](FAQ.md) - 35+ common questions answered
- 🔧 [Troubleshooting Guide](TROUBLESHOOTING.md) - Detailed problem diagnosis
- 💻 [Local Deployment Tutorial](local_deployment/README_LOCAL.md) - Non-Docker setup guide

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

## 🙏 Acknowledgments

- [SaveAny Bot](https://github.com/krau/SaveAny-Bot) - Excellent Telegram media download bot
- [Notion API](https://developers.notion.com/) - Powerful Notion integration API

---

If this project helps you, please give it a ⭐️!