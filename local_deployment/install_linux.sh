#!/bin/bash

# Telegram Notion Uploader - Linux/macOS 安装脚本

set -e

echo "================================================"
echo "   Telegram Notion Uploader - 安装脚本"
echo "================================================"
echo

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${BLUE}🔍 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检测操作系统和架构
detect_platform() {
    local os=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)
    
    case "$os" in
        linux*)
            OS="linux"
            ;;
        darwin*)
            OS="darwin"
            ;;
        *)
            print_error "不支持的操作系统: $os"
            exit 1
            ;;
    esac
    
    case "$arch" in
        x86_64|amd64)
            ARCH="amd64"
            ;;
        arm64|aarch64)
            ARCH="arm64"
            ;;
        i386|i686)
            ARCH="386"
            ;;
        armv7l)
            ARCH="arm"
            ;;
        *)
            print_error "不支持的架构: $arch"
            exit 1
            ;;
    esac
    
    PLATFORM="${OS}-${ARCH}"
    print_success "检测到平台: $PLATFORM"
}

# 检查Python
check_python() {
    print_info "检查Python安装..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python未安装"
        echo "请安装Python 3.8+："
        echo "- Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "- CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "- macOS: brew install python3"
        exit 1
    fi
    
    # 检查Python版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    print_success "Python版本: $PYTHON_VERSION"
    
    # 检查pip
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        print_error "pip未安装"
        echo "请安装pip："
        echo "- Ubuntu/Debian: sudo apt install python3-pip"
        echo "- CentOS/RHEL: sudo yum install python3-pip"
        echo "- macOS: pip通常随Python一起安装"
        exit 1
    fi
    
    print_success "pip已安装"
}

# 安装Python依赖
install_python_deps() {
    print_info "安装Python依赖..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt文件不存在"
        exit 1
    fi
    
    $PYTHON_CMD -m pip install --user -r requirements.txt
    print_success "Python依赖安装完成"
}

# 下载SaveAny Bot
download_saveany_bot() {
    print_info "下载SaveAny Bot..."
    
    # 获取最新版本
    if command -v curl &> /dev/null; then
        LATEST_RELEASE=$(curl -s https://api.github.com/repos/krau/SaveAny-Bot/releases/latest)
    elif command -v wget &> /dev/null; then
        LATEST_RELEASE=$(wget -qO- https://api.github.com/repos/krau/SaveAny-Bot/releases/latest)
    else
        print_error "需要curl或wget来下载文件"
        echo "请安装curl或wget："
        echo "- Ubuntu/Debian: sudo apt install curl"
        echo "- CentOS/RHEL: sudo yum install curl"
        echo "- macOS: curl通常已预装"
        exit 1
    fi
    
    # 解析版本号
    VERSION=$(echo "$LATEST_RELEASE" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')
    
    if [ -z "$VERSION" ]; then
        print_error "无法获取最新版本信息"
        echo "请手动下载：https://github.com/krau/SaveAny-Bot/releases"
        exit 1
    fi
    
    print_success "最新版本: $VERSION"
    
    # 构建下载URL
    DOWNLOAD_URL="https://github.com/krau/SaveAny-Bot/releases/download/$VERSION/saveany-bot-$PLATFORM"
    echo "下载地址: $DOWNLOAD_URL"
    
    # 下载文件
    if command -v curl &> /dev/null; then
        curl -L -o saveany-bot "$DOWNLOAD_URL"
    else
        wget -O saveany-bot "$DOWNLOAD_URL"
    fi
    
    if [ $? -ne 0 ]; then
        print_error "下载失败"
        echo "请手动下载：$DOWNLOAD_URL"
        echo "并重命名为 saveany-bot"
        exit 1
    fi
    
    # 设置执行权限
    chmod +x saveany-bot
    print_success "SaveAny Bot下载完成"
}

# 创建必要目录
create_directories() {
    print_info "创建必要目录..."
    mkdir -p downloads
    print_success "下载目录已创建"
}

# 处理配置文件
setup_config_files() {
    print_info "配置文件设置..."
    
    # 检查并创建config.toml
    if [ ! -f "config.toml" ]; then
        if [ -f "config.toml.example" ]; then
            cp config.toml.example config.toml
            print_warning "已创建config.toml，请编辑此文件填入你的信息："
            echo "   - Telegram Bot Token"
            echo "   - Telegram 用户ID"
        else
            print_error "配置文件模板不存在"
            exit 1
        fi
    else
        print_success "config.toml 已存在"
    fi
    
    # 检查并创建.env
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "已创建.env，请编辑此文件填入你的信息："
            echo "   - Notion Token"
            echo "   - Notion Database ID"
        else
            print_error "环境文件模板不存在"
            exit 1
        fi
    else
        print_success ".env 已存在"
    fi
}

# 检查ffmpeg（用于视频缩略图）
check_ffmpeg() {
    print_info "检查ffmpeg（用于视频缩略图生成）..."
    
    if command -v ffmpeg &> /dev/null; then
        print_success "ffmpeg已安装"
    else
        print_warning "ffmpeg未安装，视频缩略图功能将不可用"
        echo "安装ffmpeg（可选）："
        echo "- Ubuntu/Debian: sudo apt install ffmpeg"
        echo "- CentOS/RHEL: sudo yum install ffmpeg"
        echo "- macOS: brew install ffmpeg"
    fi
}

# 主函数
main() {
    echo "开始安装..."
    echo
    
    detect_platform
    check_python
    install_python_deps
    download_saveany_bot
    create_directories
    setup_config_files
    check_ffmpeg
    
    echo
    print_success "安装完成！"
    echo
    print_warning "下一步操作："
    echo "1. 编辑 config.toml 文件，填入你的Telegram Bot信息"
    echo "2. 编辑 .env 文件，填入你的Notion API信息"
    echo "3. 运行: $PYTHON_CMD run_local.py"
    echo
    echo "💡 提示："
    echo "- 详细配置方法请查看 README_LOCAL.md"
    echo "- 如有问题请查看 TROUBLESHOOTING.md"
    echo
}

# 运行主函数
main