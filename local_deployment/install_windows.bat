@echo off
chcp 65001 >nul
echo ================================================
echo    Telegram Notion Uploader - Windows 安装脚本
echo ================================================
echo.

echo 🔍 检查Python安装...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未加入PATH
    echo 请访问 https://python.org 下载并安装Python 3.8+
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)
echo ✅ Python已安装

echo.
echo 🔍 检查pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip未找到
    echo 请重新安装Python并确保包含pip
    pause
    exit /b 1
)
echo ✅ pip已安装

echo.
echo 📦 安装Python依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Python依赖安装失败
    pause
    exit /b 1
)
echo ✅ Python依赖安装成功

echo.
echo 🔍 检查系统架构...
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set ARCH=windows-amd64
    echo 检测到: Windows 64位
) else if "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
    set ARCH=windows-arm64
    echo 检测到: Windows ARM64
) else (
    set ARCH=windows-386
    echo 检测到: Windows 32位
)

echo.
echo 📥 下载SaveAny Bot...
echo 正在从GitHub下载最新版本...

REM 获取最新版本号
curl -s https://api.github.com/repos/krau/SaveAny-Bot/releases/latest > latest.json
if errorlevel 1 (
    echo ❌ 无法获取最新版本信息
    echo 请检查网络连接或手动下载：
    echo https://github.com/krau/SaveAny-Bot/releases
    del latest.json 2>nul
    pause
    exit /b 1
)

REM 解析版本号（简单方法）
for /f "tokens=4 delims=," %%a in ('findstr "tag_name" latest.json') do (
    set VERSION=%%a
    set VERSION=!VERSION:"=!
    set VERSION=!VERSION: =!
)

if "%VERSION%"=="" (
    echo ❌ 无法解析版本号
    del latest.json
    pause
    exit /b 1
)

echo 最新版本: %VERSION%

REM 构建下载URL
set DOWNLOAD_URL=https://github.com/krau/SaveAny-Bot/releases/download/%VERSION%/saveany-bot-%ARCH%.exe

echo 下载地址: %DOWNLOAD_URL%
echo.

REM 下载文件
curl -L -o saveany-bot.exe "%DOWNLOAD_URL%"
if errorlevel 1 (
    echo ❌ 下载失败
    echo 请手动下载：%DOWNLOAD_URL%
    echo 并重命名为 saveany-bot.exe
    del latest.json 2>nul
    pause
    exit /b 1
)

del latest.json
echo ✅ SaveAny Bot下载完成

echo.
echo 📁 创建必要目录...
if not exist "downloads" mkdir downloads
echo ✅ 下载目录已创建

echo.
echo 📝 配置文件检查...
if not exist "config.toml" (
    if exist "config.toml.example" (
        copy config.toml.example config.toml >nul
        echo ⚠️ 已创建config.toml，请编辑此文件填入你的信息：
        echo    - Telegram Bot Token
        echo    - Telegram 用户ID
    ) else (
        echo ❌ 配置文件模板不存在
        pause
        exit /b 1
    )
) else (
    echo ✅ config.toml 已存在
)

if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo ⚠️ 已创建.env，请编辑此文件填入你的信息：
        echo    - Notion Token
        echo    - Notion Database ID
    ) else (
        echo ❌ 环境文件模板不存在
        pause
        exit /b 1
    )
) else (
    echo ✅ .env 已存在
)

echo.
echo 🎉 安装完成！
echo.
echo ⚠️ 下一步操作：
echo 1. 编辑 config.toml 文件，填入你的Telegram Bot信息
echo 2. 编辑 .env 文件，填入你的Notion API信息
echo 3. 运行: python run_local.py
echo.
echo 💡 提示：
echo - 详细配置方法请查看 README_LOCAL.md
echo - 如有问题请查看 TROUBLESHOOTING.md
echo.
pause