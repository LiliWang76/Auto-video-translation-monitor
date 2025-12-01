#!/usr/bin/env python3
"""
视频字幕翻译自动监控程序
作者：ChiangShenhung
开发工具：腾讯 Code Buddy CN
版本：2.0
设计思路和调试：ChiangShenhung
功能：自动监控网盘下载目录，检测新视频并调用字幕翻译工具
"""

import sys
import argparse
import os
from config_wizard import ConfigWizard
from file_monitor import FileMonitor

def check_configuration():
    """检查配置是否有效，如果无效则运行配置向导"""
    wizard = ConfigWizard()
    missing_paths, invalid_paths = wizard.check_config_validity()
    
    if missing_paths or invalid_paths:
        print("=" * 60)
        print("配置检查")
        print("=" * 60)
        print("检测到配置问题，需要重新设置路径。")
        
        for config_key, description, reason in missing_paths:
            print(f"  - {description}: {reason}")
        for config_key, description, path in invalid_paths:
            print(f"  - {description}: 路径不存在 - {path}")
        
        print("\n启动配置向导...")
        
        # 运行配置向导
        if wizard.run_wizard():
            print("配置已更新，重新启动程序...")
            # 重新导入配置模块以确保使用最新配置
            import importlib
            import config
            importlib.reload(config)
            return True
        else:
            print("配置未完成，程序退出")
            sys.exit(1)
    
    return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='视频字幕翻译自动监控程序')
    parser.add_argument('--daemon', action='store_true', help='以守护进程模式运行')
    parser.add_argument('--once', action='store_true', help='只执行一次检查后退出')
    parser.add_argument('--interval', type=int, default=60, help='检查间隔（秒）')
    parser.add_argument('--config-only', action='store_true', help='只运行配置向导后退出')
    
    args = parser.parse_args()
    
    # 如果指定了--config-only参数，只运行配置向导
    if args.config_only:
        wizard = ConfigWizard()
        wizard.run_wizard()
        return
    
    # 检查配置有效性
    config_updated = check_configuration()
    
    # 如果配置已更新，重新加载配置模块
    if config_updated:
        import importlib
        import config
        importlib.reload(config)
    
    print("=" * 50)
    print("视频字幕翻译自动监控程序")
    print("=" * 50)
    
    # 创建FileMonitor实例来获取配置信息
    monitor = FileMonitor()
    
    print(f"监控目录: {monitor.download_dir}")
    print(f"翻译工具: {monitor.translate_bat}")
    print(f"字幕输出: {monitor.subtitle_dir}")
    print(f"检查间隔: {args.interval} 秒")
    print("=" * 50)
    print("按 Ctrl+C 停止监控")
    print("=" * 50)
    
    try:
        if args.once:
            # 单次检查模式
            monitor.monitor_once()
        else:
            # 持续监控模式
            monitor.monitor_loop()
            
    except KeyboardInterrupt:
        print("\n监控程序已停止")
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()