# 故障排除指南 - Telegram Notion Uploader

本指南将帮助您诊断和解决使用过程中遇到的常见问题。

## 📋 目录

- [问题诊断流程](#问题诊断流程)
- [日志分析](#日志分析)
- [常见问题分类](#常见问题分类)
- [高级故障排除](#高级故障排除)
- [获取帮助](#获取帮助)

---

## 🔍 问题诊断流程

### 步骤1：确定问题类型

**问题分类表**：
| 症状 | 可能原因 | 跳转章节 |
|------|----------|----------|
| Bot完全无响应 | Telegram配置问题 | [Telegram Bot问题](#telegram-bot问题) |
| 文件下载但不上传 | Notion配置问题 | [Notion API问题](#notion-api问题) |
| 服务启动失败 | 依赖或权限问题 | [服务启动问题](#服务启动问题) |
| 部分功能异常 | 配置或网络问题 | [功能异常问题](#功能异常问题) |

### 步骤2：收集信息

在报告问题前，请收集以下信息：
- 操作系统和版本
- Python版本
- 错误日志（完整的）
- 配置文件内容（隐藏敏感信息）
- 问题重现步骤

---

## 📝 日志分析

### Docker环境日志查看

```bash
# 查看SaveAny Bot日志
docker compose logs -f saveanybot

# 查看Notion Uploader日志
docker compose logs -f notion_uploader

# 查看所有服务日志
docker compose logs -f

# 查看最近100行日志
docker compose logs --tail 100 notion_uploader

# 只显示错误日志
docker compose logs notion_uploader | grep -i error
```

### 本地环境日志查看

本地运行时，日志直接显示在终端中。可以重定向保存：

```bash
# 保存日志到文件
python run_local.py > app.log 2>&1

# 实时查看日志
tail -f app.log

# 只查看错误
grep -i error app.log
```

### 日志级别说明

| 级别 | 含义 | 示例 |
|------|------|------|
| **INFO** | 正常运行信息 | `INFO \| 检测到新目录 album_123` |
| **WARNING** | 警告信息，功能可能受影响 | `WARNING \| ffmpeg生成缩略图失败` |
| **ERROR** | 错误信息，功能异常 | `ERROR \| 处理文件时出错: HTTP 401` |
| **DEBUG** | 调试信息（详细） | `DEBUG \| 已移除目录处理锁` |

---

## 🚨 常见问题分类

### Telegram Bot问题

#### 问题1：Bot完全无响应
**症状**：发送任何消息给Bot都没有反应

**可能原因**：
- Bot Token错误或已过期
- Bot未启动或启动失败
- 网络连接问题

**诊断步骤**：
1. 检查Bot Token格式：
   ```
   正确格式：1234567890:ABCdefGhIjKlMnOpQrStUvWxYz
   错误格式：缺少冒号、包含空格、长度不对
   ```

2. 验证Bot状态：
   - 在Telegram中搜索你的Bot
   - 点击Bot头像查看详情
   - 确认显示"这是一个验证过的机器人"

3. 检查服务状态：
   ```bash
   # Docker环境
   docker compose ps
   
   # 本地环境
   ps aux | grep saveany-bot
   ```

**解决方案**：
```bash
# 重新获取Token
# 1. 向@BotFather发送 /mybots
# 2. 选择你的Bot
# 3. 点击"API Token"
# 4. 更新config.toml中的token

# 重启服务
docker compose restart saveanybot  # Docker
# 或重新运行 python run_local.py    # 本地
```

#### 问题2：Bot响应但不下载文件
**症状**：Bot回复消息但文件没有下载

**诊断步骤**：
1. 检查用户权限配置：
   ```toml
   [[users]]
   id = 你的用户ID
   blacklist = false  # 确保是false
   storages = ["VPS_Downloads"]  # 或 ["Local_Downloads"]
   ```

2. 检查规则配置：
   ```bash
   # 向Bot发送
   /rule list
   
   # 应该看到类似输出
   1: IS-ALBUM true VPS_Downloads NEW-FOR-ALBUM
   ```

**解决方案**：
```bash
# 重新配置规则
/rule switch
/rule del 1
/rule add IS-ALBUM true VPS_Downloads NEW-FOR-ALBUM
/rule list
```

### Notion API问题

#### 问题1：HTTP 401 Unauthorized
**症状**：日志显示"HTTP 401"错误

**可能原因**：
- Notion Token错误或已过期
- Integration权限不足

**解决方案**：
1. 验证Token：
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        -H "Notion-Version: 2022-06-28" \
        https://api.notion.com/v1/users/me
   ```

2. 重新创建Integration：
   - 访问 https://www.notion.so/my-integrations
   - 删除旧的Integration
   - 创建新的Integration
   - 重新给数据库添加权限

#### 问题2：HTTP 404 Not Found
**症状**：日志显示"HTTP 404"错误

**可能原因**：
- 数据库ID错误
- Integration没有数据库访问权限

**解决方案**：
1. 验证数据库ID：
   ```
   数据库URL示例：
   https://notion.so/workspace/Database-1234567890abcdef1234567890abcdef
   
   数据库ID：1234567890abcdef1234567890abcdef
   ```

2. 重新添加Integration权限：
   - 打开数据库页面
   - 点击右上角"..."
   - 选择"添加连接"
   - 选择你的Integration

#### 问题3：上传速度极慢
**症状**：文件上传耗时很长

**可能原因**：
- 网络连接不稳定
- 大文件分块上传配置不当
- Notion API限制

**解决方案**：
1. 检查网络：
   ```bash
   # 测试到Notion的连接
   ping api.notion.com
   
   # 测试下载速度
   curl -o /dev/null -s -w "%{speed_download}\n" \
        https://api.notion.com/v1/users/me
   ```

2. 调整分块大小（在notion_uploader.py中）：
   ```python
   # 当前设置
   PART_SIZE = 19 * 1024 * 1024  # 19MB
   
   # 网络较慢时可以降低
   PART_SIZE = 10 * 1024 * 1024  # 10MB
   ```

### 服务启动问题

#### 问题1：Python依赖缺失
**症状**：ImportError或ModuleNotFoundError

**解决方案**：
```bash
# 重新安装依赖
pip install -r requirements.txt

# 检查已安装的包
pip list | grep -E "(notion|aiohttp|watchdog|dotenv)"

# 如果是虚拟环境问题
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### 问题2：端口占用或权限问题
**症状**：服务启动失败，提示端口占用

**诊断和解决**：
```bash
# 查看端口占用（如果有网络服务）
netstat -tulpn | grep :端口号

# 检查进程
ps aux | grep -E "(saveany|notion)"

# 杀死僵尸进程
pkill -f saveany-bot
pkill -f notion_uploader
```

### 功能异常问题

#### 问题1：视频缩略图生成失败
**症状**：日志显示ffmpeg相关错误

**解决方案**：
```bash
# 检查ffmpeg安装
ffmpeg -version

# 安装ffmpeg
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows：从官网下载并添加到PATH
```

#### 问题2：文件夹不合并或重复处理
**症状**：相册文件创建多个页面

**可能原因**：
- 文件夹稳定检测时间不够
- 并发处理冲突

**解决方案**：
```python
# 在notion_uploader.py中调整稳定延时
STABLE_DELAY = 90.0  # 增加到90秒

# 或检查文件是否正确分组
# 查看downloads目录结构应该是：
# downloads/
# ├── media_group_123/
# │   ├── 1.jpg
# │   ├── 2.jpg
# │   └── 3.mp4
```

---

## 🔧 高级故障排除

### 手动测试组件

#### 测试Notion连接
```python
# test_notion.py
import asyncio
from notion_client import AsyncClient
import os
from dotenv import load_dotenv

load_dotenv()

async def test_notion():
    client = AsyncClient(auth=os.getenv("NOTION_TOKEN"))
    try:
        # 测试API连接
        me = await client.users.me()
        print(f"✅ Notion连接成功: {me['name']}")
        
        # 测试数据库访问
        db_id = os.getenv("NOTION_DATABASE_ID")
        db = await client.databases.retrieve(database_id=db_id)
        print(f"✅ 数据库访问成功: {db['title'][0]['plain_text']}")
        
    except Exception as e:
        print(f"❌ Notion测试失败: {e}")

asyncio.run(test_notion())
```

#### 测试文件监控
```python
# test_watcher.py
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class TestHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(f"文件创建: {event.src_path}")
    
    def on_modified(self, event):
        print(f"文件修改: {event.src_path}")

# 监控downloads目录
watch_dir = Path("downloads")
watch_dir.mkdir(exist_ok=True)

observer = Observer()
observer.schedule(TestHandler(), str(watch_dir), recursive=True)
observer.start()

print(f"监控目录: {watch_dir}")
print("请在downloads目录中添加文件进行测试...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

### 网络连通性测试

#### 测试到GitHub的连接
```bash
# 测试SaveAny Bot下载源
curl -I https://api.github.com/repos/krau/SaveAny-Bot/releases/latest

# 测试文件下载
curl -I https://github.com/krau/SaveAny-Bot/releases/download/v0.5.7/saveany-bot-linux-amd64
```

#### 测试到Notion的连接
```bash
# 基本连通性
ping api.notion.com

# HTTPS连接
curl -I https://api.notion.com/v1/users/me

# 带认证的测试
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Notion-Version: 2022-06-28" \
     https://api.notion.com/v1/users/me
```

### 配置文件验证

#### 验证TOML配置
```python
# validate_config.py
import toml

try:
    config = toml.load("config.toml")
    print("✅ config.toml 格式正确")
    
    # 检查必要字段
    assert "telegram" in config
    assert "token" in config["telegram"]
    assert config["telegram"]["token"] != "YOUR_TELEGRAM_BOT_TOKEN"
    
    assert "users" in config
    assert len(config["users"]) > 0
    assert config["users"][0]["id"] != "YOUR_TELEGRAM_USER_ID"
    
    print("✅ 配置内容验证通过")
    
except Exception as e:
    print(f"❌ 配置验证失败: {e}")
```

#### 验证环境变量
```python
# validate_env.py
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    "NOTION_TOKEN",
    "NOTION_DATABASE_ID", 
    "WATCH_DIR"
]

for var in required_vars:
    value = os.getenv(var)
    if not value:
        print(f"❌ 环境变量缺失: {var}")
    elif "your_" in value.lower():
        print(f"⚠️ 环境变量需要配置: {var}")
    else:
        print(f"✅ 环境变量正常: {var}")
```

---

## 📞 获取帮助

### 在提交Issue前

请确保已经：
1. ✅ 查看了本故障排除指南
2. ✅ 查看了[FAQ](FAQ.md)
3. ✅ 搜索了现有的Issues
4. ✅ 收集了完整的错误日志
5. ✅ 准备了重现问题的步骤

### 提交Issue的信息模板

```markdown
## 问题描述
简要描述你遇到的问题

## 环境信息
- 操作系统：Windows 11 / macOS 13 / Ubuntu 20.04
- Python版本：3.9.7
- 部署方式：Docker / 本地部署

## 重现步骤
1. 
2. 
3. 

## 期望行为
描述你期望发生什么

## 实际行为
描述实际发生了什么

## 错误日志
```
粘贴完整的错误日志
```

## 配置文件（隐藏敏感信息）
```toml
# config.toml 相关部分
```

## 已尝试的解决方案
- [ ] 重启服务
- [ ] 检查配置文件
- [ ] 查看故障排除指南
- [ ] 其他：
```

### 社区支持

- **GitHub Issues**: [项目Issues页面](https://github.com/RanceLee233/telegram-notion-uploader/issues)
- **SaveAny Bot支持**: [SaveAny Bot项目](https://github.com/krau/SaveAny-Bot)
- **Notion API文档**: [Notion开发者文档](https://developers.notion.com/)

### 紧急问题处理

如果遇到数据丢失风险的紧急问题：

1. **立即停止服务**：
   ```bash
   # Docker环境
   docker compose down
   
   # 本地环境
   Ctrl+C 停止 run_local.py
   ```

2. **备份现有数据**：
   ```bash
   # 备份下载目录
   cp -r downloads downloads_backup
   
   # 备份配置文件
   cp config.toml config.toml.backup
   cp .env .env.backup
   ```

3. **记录问题详情**并尽快提交Issue

---

## 🔧 预防性维护

### 定期检查项目
- 每周检查日志是否有异常
- 每月更新SaveAny Bot到最新版本
- 定期清理downloads目录
- 备份重要配置文件

### 监控建议
```bash
# 创建简单的监控脚本
#!/bin/bash
# monitor.sh

# 检查SaveAny Bot进程
if ! pgrep -f saveany-bot > /dev/null; then
    echo "⚠️ SaveAny Bot进程未运行"
fi

# 检查downloads目录大小
SIZE=$(du -sh downloads | cut -f1)
echo "📁 Downloads目录大小: $SIZE"

# 检查磁盘空间
df -h | grep -E "(/$|/home)"
```

记住：及时的问题发现和处理可以避免更大的故障！