# 常见问题 FAQ - Telegram Notion Uploader

## 📋 目录

- [基础问题](#基础问题)
- [配置问题](#配置问题)
- [功能问题](#功能问题)
- [性能问题](#性能问题)
- [安全问题](#安全问题)

---

## 🔰 基础问题

### Q1: 这个项目是做什么的？
**A**: Telegram Notion Uploader 是一个自动化工具，可以将您在 Telegram 中发送给机器人的媒体文件（图片、视频等）自动上传到 Notion 数据库中。支持单文件和相册的智能处理。

### Q2: 需要编程基础吗？
**A**: 不需要。我们提供了详细的新手教程和一键安装脚本。只需要按照教程配置即可。

### Q3: Docker和本地部署有什么区别？
**A**: 
- **Docker部署**: 环境隔离，安装简单，适合熟悉Docker的用户
- **本地部署**: 直接在系统上运行，更容易调试，适合不想使用Docker的用户

两种方式功能完全相同，选择您喜欢的方式即可。

### Q4: 这个项目安全吗？
**A**: 
- ✅ 开源代码，完全透明
- ✅ 本地运行，数据不经过第三方服务器
- ✅ 仅使用官方API（Telegram Bot API + Notion API）
- ✅ 不收集或上传任何个人信息

### Q5: 免费吗？
**A**: 完全免费！但需要注意：
- Notion有使用限制（个人版通常够用）
- 网络带宽消耗由您承担
- 如果使用云服务器，可能产生服务器费用

---

## ⚙️ 配置问题

### Q6: 如何获取Telegram Bot Token？
**A**: 
1. 在Telegram中搜索 `@BotFather`
2. 发送 `/newbot` 命令
3. 按提示设置Bot名称和用户名
4. 复制返回的Token

详细步骤请查看 [README教程](README.md#步骤1创建-telegram-bot)

### Q7: 如何获取Notion Database ID？
**A**: 
从数据库URL中提取：
```
数据库URL: https://notion.so/workspace/Database-1234567890abcdef1234567890abcdef?v=...
数据库ID: 1234567890abcdef1234567890abcdef
```

### Q8: 数据库属性设置错误怎么办？
**A**: 确保数据库包含以下属性：
- **名称** (标题类型) - 存储页面标题
- **文件和媒体** (文件类型) - 存储媒体文件

如果属性名称不同，请修改 `notion_uploader.py` 中的对应字段。

### Q9: 为什么Bot不响应我的消息？
**A**: 检查以下配置：
1. **Token是否正确**: 格式为 `数字:字母数字组合`
2. **用户ID是否正确**: 在config.toml中配置
3. **规则是否启用**: 发送 `/rule list` 检查
4. **blacklist设置**: 确保设为 `false`

### Q10: Integration权限怎么添加？
**A**: 
1. 打开Notion数据库页面
2. 点击右上角 "..." 菜单
3. 选择 "添加连接"
4. 找到并选择您的Integration

---

## 🚀 功能问题

### Q11: 支持哪些文件类型？
**A**: 
- **图片**: JPG, PNG, GIF, WebP等
- **视频**: MP4, MOV, AVI等常见格式
- **其他**: 所有Telegram支持的媒体文件

### Q12: 文件大小有限制吗？
**A**: 
- **Telegram限制**: 最大2GB
- **Notion限制**: 单文件20MB，超过自动分块上传
- **实际处理**: 理论上无限制，取决于网络和存储

### Q13: 相册文件为什么要等60秒？
**A**: 这是稳定检测机制，确保相册中的所有文件都下载完成后再统一处理，避免文件遗漏。

### Q14: 可以修改等待时间吗？
**A**: 可以。在 `notion_uploader.py` 中修改：
```python
STABLE_DELAY = 60.0  # 改为你想要的秒数
```

### Q15: 为什么视频没有缩略图？
**A**: 需要安装ffmpeg：
- **Windows**: 下载并添加到PATH
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### Q16: 文件上传后本地文件会删除吗？
**A**: 是的，成功上传到Notion后，本地文件会自动删除以节省空间。如果上传失败，文件会保留。

### Q17: 支持批量处理历史文件吗？
**A**: 当前版本主要针对实时处理。如需处理历史文件，可以：
1. 将文件放入downloads目录
2. 手动触发处理（需要修改代码）

---

## ⚡ 性能问题

### Q18: 上传速度慢怎么办？
**A**: 
1. **检查网络**: 确保网络稳定
2. **调整分块大小**: 修改 `PART_SIZE` 参数
3. **减少并发**: 降低 `workers` 数量
4. **优化文件**: 压缩大文件

### Q19: 占用内存太多怎么办？
**A**: 
1. **重启服务**: 定期重启释放内存
2. **减少并发**: 降低处理线程数
3. **清理临时文件**: 定期清理downloads目录

### Q20: 可以处理多少个文件？
**A**: 
理论上无限制，但建议：
- 同时处理的相册不超过10个
- 单个相册文件数不超过50个
- 定期重启服务保持稳定

### Q21: 断网重连后会继续处理吗？
**A**: 
- **已下载的文件**: 会继续处理
- **正在下载的文件**: 需要重新发送
- **建议**: 网络不稳定时分批发送文件

---

## 🔒 安全问题

### Q22: Token会被泄露吗？
**A**: 
配置文件中的Token仅在本地使用，不会发送到任何第三方服务器。请注意：
- 不要将配置文件分享给他人
- 不要在公开场所展示配置文件
- 定期更换Token（可选）

### Q23: 可以多人使用同一个Bot吗？
**A**: 
技术上可以，但不推荐：
- 文件会混在一起
- 权限管理复杂
- 建议每人创建自己的Bot

### Q24: 如何限制Bot的使用权限？
**A**: 
在 `config.toml` 中配置：
```toml
[[users]]
id = 允许的用户ID
blacklist = false
storages = ["允许的存储"]

# 禁止某用户
[[users]]
id = 禁止的用户ID
blacklist = true
```

### Q25: 数据存储在哪里？
**A**: 
- **媒体文件**: 最终存储在Notion
- **临时文件**: 本地downloads目录（处理后删除）
- **配置信息**: 本地配置文件
- **运行日志**: 控制台输出（可保存到文件）

---

## 🛠️ 技术问题

### Q26: 支持哪些操作系统？
**A**: 
- **Windows**: 10/11（推荐64位）
- **macOS**: 10.14+（Intel和Apple Silicon）
- **Linux**: Ubuntu 18+, CentOS 7+, Debian 9+

### Q27: Python版本要求？
**A**: 
- **最低要求**: Python 3.8
- **推荐版本**: Python 3.9+
- **不支持**: Python 2.x

### Q28: 可以在树莓派上运行吗？
**A**: 
可以！支持ARM架构：
- 使用对应的SaveAny Bot ARM版本
- 可能需要编译某些Python包
- 性能较x86略低但完全可用

### Q29: 可以部署到云服务器吗？
**A**: 
完全可以：
- **VPS**: 推荐使用Docker部署
- **云主机**: 支持阿里云、腾讯云等
- **注意**: 确保网络可以访问Telegram和Notion

### Q30: 如何升级到新版本？
**A**: 
```bash
# 备份配置
cp config.toml config.toml.backup
cp .env .env.backup

# 下载新版本
git pull origin main

# Docker用户
docker compose pull
docker compose up -d

# 本地用户
# 下载新的SaveAny Bot二进制文件
# 重启服务
```

---

## 🆘 其他问题

### Q31: 项目会持续维护吗？
**A**: 
是的！项目会持续维护和更新：
- 修复发现的Bug
- 适配API变化
- 添加新功能
- 改进用户体验

### Q32: 如何参与项目贡献？
**A**: 
欢迎参与！可以通过以下方式：
- 报告Bug和建议
- 提交Pull Request
- 改进文档
- 分享使用经验

### Q33: 有交流群或社区吗？
**A**: 
目前主要通过GitHub进行交流：
- [Issues](https://github.com/RanceLee233/telegram-notion-uploader/issues): 报告问题
- [Discussions](https://github.com/RanceLee233/telegram-notion-uploader/discussions): 讨论交流

### Q34: 可以商业使用吗？
**A**: 
可以！项目采用MIT许可证：
- ✅ 商业使用
- ✅ 修改和分发
- ✅ 私人使用
- ❗ 需保留原始许可证声明

### Q35: 找不到问题的解决方案怎么办？
**A**: 
1. 查看 [故障排除指南](TROUBLESHOOTING.md)
2. 搜索现有的 [GitHub Issues](https://github.com/RanceLee233/telegram-notion-uploader/issues)
3. 提交新的Issue（提供详细信息）
4. 参考 [SaveAny Bot文档](https://github.com/krau/SaveAny-Bot)

---

## 💡 使用技巧

### 技巧1: 批量处理文件
将多个文件选中后一起发送，系统会智能识别为相册并合并处理。

### 技巧2: 自定义页面标题
文件名会作为页面标题，发送前重命名文件可以自定义页面标题。

### 技巧3: 快速测试配置
发送一张小图片测试配置是否正确，比发送大文件更快。

### 技巧4: 定期维护
- 每周重启一次服务
- 定期清理downloads目录
- 备份重要配置文件

### 技巧5: 优化性能
- 网络高峰期避免大文件传输
- 分批处理大量文件
- 关闭不必要的其他网络应用

---

**还有其他问题？** 欢迎在 [GitHub Issues](https://github.com/RanceLee233/telegram-notion-uploader/issues) 中提问！