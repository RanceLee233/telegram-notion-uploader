#!/usr/bin/env python3
"""
Telegram Notion Uploader - 本地运行脚本
用于在本地环境中启动和管理服务
"""

import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

class LocalRunner:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.saveany_process = None
        self.uploader_process = None
        self.running = False
        
    def check_dependencies(self):
        """检查依赖是否安装"""
        print("🔍 检查依赖...")
        
        # 检查Python依赖
        try:
            import notion_client
            import aiohttp
            import watchdog
            from dotenv import load_dotenv
            print("✅ Python依赖检查通过")
        except ImportError as e:
            print(f"❌ Python依赖缺失: {e}")
            print("请运行: pip install -r requirements.txt")
            return False
            
        # 检查配置文件
        config_file = self.base_dir / "config.toml"
        env_file = self.base_dir / ".env"
        
        if not config_file.exists():
            print("❌ 配置文件不存在: config.toml")
            print("请复制 config.toml.example 为 config.toml 并填入真实信息")
            return False
            
        if not env_file.exists():
            print("❌ 环境文件不存在: .env")
            print("请复制 .env.example 为 .env 并填入真实信息")
            return False
            
        print("✅ 配置文件检查通过")
        
        # 检查SaveAny Bot可执行文件
        saveany_bot = self.find_saveany_bot()
        if not saveany_bot:
            print("❌ SaveAny Bot可执行文件未找到")
            print("请下载对应平台的二进制文件到当前目录")
            return False
            
        print("✅ SaveAny Bot可执行文件检查通过")
        return True
        
    def find_saveany_bot(self):
        """查找SaveAny Bot可执行文件"""
        possible_names = [
            "saveany-bot",
            "saveany-bot.exe", 
            "saveanybot",
            "saveanybot.exe"
        ]
        
        for name in possible_names:
            bot_path = self.base_dir / name
            if bot_path.exists():
                return bot_path
        return None
        
    def create_downloads_dir(self):
        """创建下载目录"""
        downloads_dir = self.base_dir / "downloads"
        downloads_dir.mkdir(exist_ok=True)
        print(f"📁 下载目录: {downloads_dir}")
        
    def start_saveany_bot(self):
        """启动SaveAny Bot"""
        saveany_bot = self.find_saveany_bot()
        if not saveany_bot:
            return False
            
        print(f"🚀 启动SaveAny Bot: {saveany_bot}")
        
        try:
            # 确保可执行权限（Linux/macOS）
            if os.name != 'nt':
                os.chmod(saveany_bot, 0o755)
                
            self.saveany_process = subprocess.Popen(
                [str(saveany_bot)],
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(2)  # 等待启动
            
            if self.saveany_process.poll() is None:
                print("✅ SaveAny Bot 启动成功")
                return True
            else:
                stdout, stderr = self.saveany_process.communicate()
                print(f"❌ SaveAny Bot 启动失败:")
                print(f"输出: {stdout}")
                print(f"错误: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 启动SaveAny Bot时出错: {e}")
            return False
            
    def start_notion_uploader(self):
        """启动Notion Uploader"""
        print("🚀 启动Notion Uploader...")
        
        try:
            self.uploader_process = subprocess.Popen(
                [sys.executable, "notion_uploader.py"],
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(2)  # 等待启动
            
            if self.uploader_process.poll() is None:
                print("✅ Notion Uploader 启动成功")
                return True
            else:
                stdout, stderr = self.uploader_process.communicate()
                print(f"❌ Notion Uploader 启动失败:")
                print(f"输出: {stdout}")
                print(f"错误: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 启动Notion Uploader时出错: {e}")
            return False
            
    def monitor_processes(self):
        """监控进程状态"""
        while self.running:
            # 检查SaveAny Bot
            if self.saveany_process and self.saveany_process.poll() is not None:
                print("⚠️ SaveAny Bot 进程已停止")
                break
                
            # 检查Notion Uploader  
            if self.uploader_process and self.uploader_process.poll() is not None:
                print("⚠️ Notion Uploader 进程已停止")
                break
                
            time.sleep(5)
            
    def stop_services(self):
        """停止所有服务"""
        print("\n🛑 正在停止服务...")
        self.running = False
        
        if self.saveany_process:
            self.saveany_process.terminate()
            try:
                self.saveany_process.wait(timeout=10)
                print("✅ SaveAny Bot 已停止")
            except subprocess.TimeoutExpired:
                self.saveany_process.kill()
                print("🔥 强制终止SaveAny Bot")
                
        if self.uploader_process:
            self.uploader_process.terminate()
            try:
                self.uploader_process.wait(timeout=10)
                print("✅ Notion Uploader 已停止")
            except subprocess.TimeoutExpired:
                self.uploader_process.kill()
                print("🔥 强制终止Notion Uploader")
                
    def signal_handler(self, signum, frame):
        """处理中断信号"""
        print(f"\n收到信号 {signum}")
        self.stop_services()
        sys.exit(0)
        
    def run(self):
        """主运行函数"""
        print("🎯 Telegram Notion Uploader - 本地运行模式")
        print("=" * 50)
        
        # 检查依赖
        if not self.check_dependencies():
            sys.exit(1)
            
        # 创建下载目录
        self.create_downloads_dir()
        
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # 启动服务
        if not self.start_saveany_bot():
            sys.exit(1)
            
        if not self.start_notion_uploader():
            self.stop_services()
            sys.exit(1)
            
        self.running = True
        
        print("\n🎉 所有服务启动成功!")
        print("📁 监控目录:", self.base_dir / "downloads")
        print("📝 使用 Ctrl+C 停止服务")
        print("=" * 50)
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        try:
            # 主线程等待
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_services()

if __name__ == "__main__":
    runner = LocalRunner()
    runner.run()