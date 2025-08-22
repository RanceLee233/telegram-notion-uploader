# 本地部署教程 - Telegram Notion Uploader

本教程将帮助您在本地计算机上部署 Telegram Notion Uploader，无需使用 Docker。

## 📋 目录

- [系统要求](#系统要求)
- [第一章：前期准备](#第一章前期准备)
- [第二章：本地安装](#第二章本地安装)
- [第三章：配置设置](#第三章配置设置)
- [第四章：运行和测试](#第四章运行和测试)
- [第五章：故障排除](#第五章故障排除)

## 系统要求

### 基础要求
- **操作系统**: Windows 10+, macOS 10.14+, 或 Linux
- **Python**: 3.8 或更高版本
- **网络**: 稳定的互联网连接
- **存储**: 至少 1GB 可用空间

### 可选要求
- **ffmpeg**: 用于视频缩略图生成（推荐安装）

---

## 第一章：前期准备

### 📱 步骤1：创建 Telegram Bot

#### 1.1 打开 Telegram
- 在手机或电脑上打开 Telegram 应用
- 如果没有账户，请先注册

#### 1.2 找到 BotFather
- 在搜索框中输入 `@BotFather`
- 点击第一个结果（有蓝色验证标记）

#### 1.3 创建新的 Bot
1. 发送 `/newbot` 命令
2. BotFather 会要求输入 Bot 名称：
   ```
   输入示例：My Notion Uploader Bot
   ```
3. 接着要求输入用户名（必须以 bot 结尾）：
   ```
   输入示例：my_notion_uploader_bot
   ```
4. 创建成功后，BotFather 会发送一条包含 Token 的消息：
   ```
   Use this token to access the HTTP API:
   1234567890:ABCdefGhIjKlMnOpQrStUvWxYz
   ```

#### 1.4 保存 Token
⚠️ **重要**: 将这个 Token 复制并安全保存，后面会用到。

### 🗂️ 步骤2：设置 Notion

#### 2.1 创建 Notion 账户
- 访问 [notion.so](https://notion.so) 注册账户
- 如果已有账户，请登录

#### 2.2 创建数据库
1. 在 Notion 中创建新页面
2. 添加数据库（选择"表格"）
3. 设置数据库属性：
   - **名称** (标题类型) - 用于存储页面标题
   - **文件和媒体** (文件类型) - 用于存储媒体文件

#### 2.3 创建 Integration
1. 访问 [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. 点击 "+ 新建integration"
3. 填写信息：
   - **名称**: Telegram Uploader
   - **关联的工作区**: 选择你的工作区
   - **类型**: 内部integration
4. 点击"提交"
5. 复制生成的 **Internal Integration Token**

#### 2.4 给数据库添加权限
1. 打开你创建的数据库页面
2. 点击右上角的"..."菜单
3. 选择"添加连接"
4. 找到并选择你刚创建的 Integration

#### 2.5 获取数据库 ID
**方法一：从 URL 获取**
```
数据库URL: https://notion.so/username/1234567890abcdef1234567890abcdef?v=...
数据库ID: 1234567890abcdef1234567890abcdef
```

**方法二：使用开发者工具**
1. 在数据库页面按 F12
2. 在控制台输入: `window.location.pathname`
3. 从结果中提取 32 位字符串

### 🆔 步骤3：获取 Telegram 用户 ID

#### 方法一：使用 @userinfobot（推荐）
1. 在 Telegram 中搜索 `@userinfobot`
2. 点击 "Start" 或发送 `/start`
3. Bot 会返回你的用户信息，包含 User ID

#### 方法二：使用 @RawDataBot
1. 在 Telegram 中搜索 `@RawDataBot`
2. 发送任意消息
3. Bot 会返回详细信息，找到 `"id"` 字段

---

## 第二章：本地安装

### 🔽 步骤1：下载项目

```bash
# 下载项目
git clone https://github.com/RanceLee233/telegram-notion-uploader.git
cd telegram-notion-uploader/local_deployment
```

### 🛠️ 步骤2：自动安装

#### Windows 用户
1. 双击运行 `install_windows.bat`
2. 等待安装完成

#### Linux/macOS 用户
```bash
# 给脚本执行权限
chmod +x install_linux.sh

# 运行安装脚本
./install_linux.sh
```

### 📚 步骤3：手动安装（如果自动安装失败）

#### 3.1 安装 Python 依赖
```bash
# 使用 pip 安装依赖
pip install -r requirements.txt

# 或者使用 pip3（某些系统）
pip3 install -r requirements.txt
```

#### 3.2 下载 SaveAny Bot
1. 访问 [SaveAny Bot Releases](https://github.com/krau/SaveAny-Bot/releases)
2. 下载对应你系统的版本：
   - Windows 64位: `saveany-bot-windows-amd64.exe`
   - Windows ARM: `saveany-bot-windows-arm64.exe`
   - macOS Intel: `saveany-bot-darwin-amd64`
   - macOS Apple Silicon: `saveany-bot-darwin-arm64`
   - Linux 64位: `saveany-bot-linux-amd64`
3. 重命名为 `saveany-bot`（Windows 保留 .exe 扩展名）
4. 放到 `local_deployment` 目录中

#### 3.3 安装 ffmpeg（可选但推荐）
**Windows:**
1. 下载 [ffmpeg](https://ffmpeg.org/download.html)
2. 解压并添加到 PATH

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg
```

---

## 第三章：配置设置

### ⚙️ 步骤1：配置 SaveAny Bot

1. 复制配置文件：
   ```bash
   cp config.toml.example config.toml
   ```

2. 编辑 `config.toml` 文件：
   ```toml
   [telegram]
   token = "你的Bot Token"     # 替换为第一章获取的Token
   
   [[users]]
   id = 你的用户ID              # 替换为第一章获取的用户ID
   blacklist = false
   storages = ["Local_Downloads"]
   ```

### 🔑 步骤2：配置 Notion

1. 复制环境文件：
   ```bash
   cp .env.example .env
   ```

2. 编辑 `.env` 文件：
   ```bash
   NOTION_TOKEN=你的Notion Token        # 第一章获取的Integration Token
   NOTION_DATABASE_ID=你的数据库ID      # 第一章获取的数据库ID
   WATCH_DIR=./downloads               # 监控目录（通常不需要修改）
   ```

### 📂 步骤3：创建下载目录

```bash
mkdir downloads
```

---

## 第四章：运行和测试

### 🚀 步骤1：启动服务

```bash
python run_local.py
```

如果一切正常，你会看到：
```
🎯 Telegram Notion Uploader - 本地运行模式
==================================================
🔍 检查依赖...
✅ Python依赖检查通过
✅ 配置文件检查通过
✅ SaveAny Bot可执行文件检查通过
📁 下载目录: /path/to/downloads
🚀 启动SaveAny Bot: /path/to/saveany-bot
✅ SaveAny Bot 启动成功
🚀 启动Notion Uploader...
✅ Notion Uploader 启动成功

🎉 所有服务启动成功!
📁 监控目录: /path/to/downloads
📝 使用 Ctrl+C 停止服务
==================================================
```

### 🔧 步骤2：配置 Telegram Bot 规则

在 Telegram 中向你的 Bot 发送以下命令：

```
/rule switch
/rule add IS-ALBUM true Local_Downloads NEW-FOR-ALBUM
/rule list
```

确认看到类似输出：
```
1: IS-ALBUM true Local_Downloads NEW-FOR-ALBUM
```

### 📤 步骤3：测试上传

1. **测试单文件**：
   - 向 Bot 发送一张图片或视频
   - 查看 Notion 数据库是否创建新页面

2. **测试相册**：
   - 选择多个文件一起发送
   - 等待约60秒
   - 查看是否合并到一个页面

### ✅ 步骤4：验证功能

- ✅ 单文件上传创建独立页面
- ✅ 相册文件合并到同一页面  
- ✅ 视频文件生成缩略图
- ✅ 文件在上传后被删除

---

## 第五章：故障排除

### 🔍 查看日志

运行时的所有输出都会显示在终端中。常见日志类型：

```bash
# 正常运行日志
INFO | 检测到新目录 album_123
INFO | 文件夹 album_123 稳定 60 秒，开始处理
INFO | ✅ 相册上传成功！包含 3 个文件

# 错误日志
ERROR | 处理文件 photo.jpg 时出错: HTTP 401
WARNING | ffmpeg生成缩略图失败
```

### 🚨 常见问题

#### 问题1：Bot 无响应
**症状**: 发送文件给 Bot 没有反应

**解决方案**:
1. 检查 Bot Token 是否正确
2. 检查用户 ID 是否正确
3. 确认已运行 `/rule` 命令
4. 重启服务

#### 问题2：文件下载但不上传到 Notion
**症状**: 文件出现在 downloads 目录但没有上传

**解决方案**:
1. 检查 `.env` 文件中的 Notion 配置
2. 确认 Integration 有数据库权限
3. 检查网络连接

#### 问题3：视频缩略图生成失败
**症状**: 日志显示 ffmpeg 错误

**解决方案**:
1. 安装 ffmpeg
2. 确认 ffmpeg 在 PATH 中
3. 检查视频文件格式是否支持

#### 问题4：权限错误（Linux/macOS）
**症状**: 无法执行 saveany-bot

**解决方案**:
```bash
chmod +x saveany-bot
```

### 📞 获取帮助

如果问题仍未解决：

1. 查看完整的 [故障排除指南](../TROUBLESHOOTING.md)
2. 查看 [常见问题 FAQ](../FAQ.md)
3. 在 GitHub 提交 Issue

---

## 🎯 高级配置

### 自定义下载目录
修改 `.env` 文件中的 `WATCH_DIR`：
```bash
# Windows 示例
WATCH_DIR=C:/MyTelegramFiles

# macOS/Linux 示例
WATCH_DIR=/Users/username/telegram-files
```

### 开机自启动

#### Windows（任务计划程序）
1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器为"计算机启动时"
4. 操作设置为运行 `python run_local.py`

#### Linux（systemd）
1. 创建服务文件：
   ```bash
   sudo nano /etc/systemd/system/telegram-notion.service
   ```

2. 添加内容：
   ```ini
   [Unit]
   Description=Telegram Notion Uploader
   After=network.target

   [Service]
   Type=simple
   User=yourusername
   WorkingDirectory=/path/to/local_deployment
   ExecStart=/usr/bin/python3 run_local.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. 启用服务：
   ```bash
   sudo systemctl enable telegram-notion.service
   sudo systemctl start telegram-notion.service
   ```

#### macOS（launchd）
1. 创建 plist 文件：
   ```bash
   nano ~/Library/LaunchAgents/com.telegram.notion.plist
   ```

2. 添加内容：
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
       <key>Label</key>
       <string>com.telegram.notion</string>
       <key>ProgramArguments</key>
       <array>
           <string>/usr/bin/python3</string>
           <string>/path/to/local_deployment/run_local.py</string>
       </array>
       <key>RunAtLoad</key>
       <true/>
       <key>KeepAlive</key>
       <true/>
   </dict>
   </plist>
   ```

3. 加载服务：
   ```bash
   launchctl load ~/Library/LaunchAgents/com.telegram.notion.plist
   ```

---

## 📝 注意事项

1. **网络稳定性**: 确保网络连接稳定，否则可能导致上传失败
2. **存储空间**: 定期清理下载目录，避免占用过多磁盘空间  
3. **Token 安全**: 不要分享你的 Bot Token 和 Notion Token
4. **系统资源**: 大文件上传会消耗更多内存和带宽
5. **备份配置**: 定期备份 `config.toml` 和 `.env` 文件

---

恭喜！你已经成功部署了本地版本的 Telegram Notion Uploader 🎉