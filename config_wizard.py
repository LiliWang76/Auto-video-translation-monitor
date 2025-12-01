"""
配置向导模块
作者：ChiangShenhung
开发工具：腾讯 Code Buddy CN
版本：2.0
设计思路和调试：ChiangShenhung
功能：引导用户设置视频下载目录和字幕翻译工具路径
"""

import os
import sys
import json
from config import CONFIG

class ConfigWizard:
    """
    配置向导类 - 提供交互式配置界面
    
    主要功能：
    - 检查当前配置的有效性
    - 引导用户设置必要的目录路径
    - 验证用户输入的路径
    - 创建和保存配置文件
    - 提供示例配置文件模板
    
    支持的配置项：
    - 下载目录 (DOWNLOAD_DIR)
    - 字幕翻译工具 (TRANSLATE_BAT)
    - 字幕输出目录 (SUBTITLE_DIR)
    """
    
    def __init__(self):
        """
        初始化配置向导
        
        初始化配置参数：
        - 配置文件名
        - 默认配置引用
        - 待修改配置项列表
        """
        self.config_file = "config.json"
        self.default_config = CONFIG
        self.modify_paths = []  # 要修改的配置项列表
        
    def check_config_validity(self):
        """
        检查当前配置的有效性
        
        检查内容：
        - 配置项是否已设置（非空）
        - 路径是否存在
        - 翻译工具是否为有效的BAT文件
        
        返回:
            tuple: (missing_paths, invalid_paths)
            - missing_paths: 缺失的配置项列表
            - invalid_paths: 无效的路径配置项列表
            
        每个配置项包含信息：
            (配置键, 描述, 原因/路径)
        """
        missing_paths = []
        invalid_paths = []
        
        # 检查下载目录
        download_dir = str(self.default_config.get("DOWNLOAD_DIR", ""))
        if not download_dir:
            missing_paths.append(("DOWNLOAD_DIR", "下载目录", "未设置下载目录"))
        elif not os.path.exists(download_dir):
            invalid_paths.append(("DOWNLOAD_DIR", "下载目录", download_dir))
        
        # 检查翻译工具
        translate_bat = str(self.default_config.get("TRANSLATE_BAT", ""))
        if not translate_bat:
            missing_paths.append(("TRANSLATE_BAT", "字幕翻译工具", "未设置翻译工具路径"))
        elif not os.path.exists(translate_bat):
            invalid_paths.append(("TRANSLATE_BAT", "字幕翻译工具", translate_bat))
        elif not translate_bat.lower().endswith('.bat'):
            invalid_paths.append(("TRANSLATE_BAT", "字幕翻译工具", "不是有效的BAT文件路径"))
        
        # 检查字幕输出目录
        subtitle_dir = str(self.default_config.get("SUBTITLE_DIR", ""))
        if not subtitle_dir:
            missing_paths.append(("SUBTITLE_DIR", "字幕输出目录", "未设置字幕输出目录"))
        elif not os.path.exists(subtitle_dir):
            invalid_paths.append(("SUBTITLE_DIR", "字幕输出目录", subtitle_dir))
        
        return missing_paths, invalid_paths
    
    def get_user_input_path(self, prompt, default_path=""):
        """
        获取用户输入的路径并进行验证
        
        参数:
            prompt: 提示信息
            default_path: 默认路径（可选）
            
        返回:
            str: 用户输入的路径
            
        功能:
            - 显示当前设置（如果有默认路径）
            - 允许用户直接回车使用默认设置
            - 验证路径是否存在
            - 提供重新输入选项
            - 支持用户强制使用不存在的路径
        """
        while True:
            print(f"\n{prompt}")
            if default_path:
                print(f"当前设置: {default_path}")
                user_input = input("请输入新路径（直接回车使用当前设置）: ").strip()
            else:
                user_input = input("请输入路径: ").strip()
            
            # 如果用户直接回车且存在默认路径，则使用默认路径
            if not user_input and default_path:
                return default_path
            
            if not user_input:
                print("路径不能为空，请重新输入")
                continue
            
            # 检查路径是否存在
            if os.path.exists(user_input):
                return user_input
            else:
                print(f"路径不存在: {user_input}")
                retry = input("路径不存在，是否重新输入？(y/n, 默认y): ").strip().lower()
                if retry not in ['', 'y', 'yes']:
                    return user_input  # 用户确认使用不存在的路径
    
    def get_bat_file_path(self, prompt, default_path=""):
        """获取BAT文件路径，并验证是否是有效的BAT文件"""
        while True:
            path = self.get_user_input_path(prompt, default_path)
            
            # 检查是否是BAT文件
            if path.lower().endswith('.bat'):
                if os.path.exists(path):
                    return path
                else:
                    print("BAT文件不存在")
            else:
                print("请输入有效的BAT文件路径（以.bat结尾）")
    
    def run_wizard(self):
        """运行配置向导"""
        print("=" * 60)
        print("视频字幕翻译监控系统 - 配置向导")
        print("=" * 60)
        print("\n本向导将帮助您设置必要的目录路径。")
        
        # 检查当前配置状态
        missing_paths, invalid_paths = self.check_config_validity()
        
        if not missing_paths and not invalid_paths:
            print("\n当前配置有效，无需重新配置。")
            print("1. 下载目录:", self.default_config["DOWNLOAD_DIR"])
            print("2. 翻译工具:", self.default_config["TRANSLATE_BAT"])
            print("3. 字幕输出:", self.default_config["SUBTITLE_DIR"])
            
            print("\n请选择要修改的配置项：")
            print("1. 修改下载目录")
            print("2. 修改翻译工具")
            print("3. 修改字幕输出目录")
            print("4. 修改全部配置")
            print("5. 保持当前配置")
            
            choice = input("\n请输入选项 (1-5, 默认5): ").strip()
            
            if choice == "5" or not choice:
                return False  # 保持当前配置
            elif choice == "4":
                print("\n开始修改全部配置...")
                # 设置要修改全部配置
                self.modify_paths = ["DOWNLOAD_DIR", "TRANSLATE_BAT", "SUBTITLE_DIR"]
            elif choice == "1":
                print("\n开始修改下载目录...")
                self.modify_paths = ["DOWNLOAD_DIR"]
            elif choice == "2":
                print("\n开始修改翻译工具...")
                self.modify_paths = ["TRANSLATE_BAT"]
            elif choice == "3":
                print("\n开始修改字幕输出目录...")
                self.modify_paths = ["SUBTITLE_DIR"]
            else:
                print("无效选择，保持当前配置")
                return False
        
        # 显示配置问题
        if missing_paths or invalid_paths:
            print("\n检测到以下配置问题:")
            for config_key, description, reason in missing_paths:
                print(f"  - {description}: {reason}")
            for config_key, description, path in invalid_paths:
                print(f"  - {description}: 路径不存在 - {path}")
            print("\n开始配置向导...")
        
        # 根据用户选择配置相应的路径
        download_dir = self.default_config.get("DOWNLOAD_DIR", "")
        translate_bat = self.default_config.get("TRANSLATE_BAT", "")
        subtitle_dir = self.default_config.get("SUBTITLE_DIR", "")
        
        # 配置下载目录（如果需要修改）
        if not self.modify_paths or "DOWNLOAD_DIR" in self.modify_paths:
            print("\n" + "-" * 40)
            print("步骤1: 设置下载目录")
            print("-" * 40)
            print("请设置网盘下载目录，该目录用于监控新下载的视频文件。")
            download_dir = self.get_user_input_path(
                "请输入网盘下载目录路径:",
                self.default_config.get("DOWNLOAD_DIR", "")
            )
        
        # 配置字幕翻译工具（如果需要修改）
        if not self.modify_paths or "TRANSLATE_BAT" in self.modify_paths:
            print("\n" + "-" * 40)
            print("步骤2: 设置字幕翻译工具")
            print("-" * 40)
            print("请设置字幕翻译工具的BAT文件路径。")
            translate_bat = self.get_bat_file_path(
                "请输入字幕翻译工具BAT文件路径:",
                self.default_config.get("TRANSLATE_BAT", "")
            )
        
        # 配置字幕输出目录（如果需要修改）
        if not self.modify_paths or "SUBTITLE_DIR" in self.modify_paths:
            print("\n" + "-" * 40)
            print("步骤3: 设置字幕输出目录")
            print("-" * 40)
            print("请设置字幕文件的输出目录。")
            subtitle_dir = self.get_user_input_path(
                "请输入字幕输出目录路径:",
                self.default_config.get("SUBTITLE_DIR", "")
            )
        
        # 显示配置摘要
        print("\n" + "=" * 60)
        print("配置摘要")
        print("=" * 60)
        print(f"下载目录: {download_dir}")
        print(f"翻译工具: {translate_bat}")
        print(f"字幕输出: {subtitle_dir}")
        
        # 确认配置
        confirm = input("\n确认使用以上配置？(y/n, 默认y): ").strip().lower()
        if confirm in ['', 'y', 'yes']:
            # 更新配置
            self.update_config(download_dir, translate_bat, subtitle_dir)
            print("\n配置已保存！")
            return True
        else:
            print("\n配置已取消。")
            return False
    
    def update_config(self, download_dir, translate_bat, subtitle_dir):
        """更新配置文件"""
        # 更新默认配置
        self.default_config["DOWNLOAD_DIR"] = download_dir
        self.default_config["TRANSLATE_BAT"] = translate_bat
        self.default_config["SUBTITLE_DIR"] = subtitle_dir
        
        # 保存到config.py文件
        config_content = f'''# 配置文件
CONFIG = {json.dumps(self.default_config, indent=4, ensure_ascii=False)}
'''
        
        try:
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(config_content)
            print("配置文件已更新")
        except Exception as e:
            print(f"保存配置文件时出错: {e}")
            # 如果保存失败，至少更新内存中的配置
            import config
            config.CONFIG = self.default_config
    
    def create_sample_config(self):
        """创建示例配置文件"""
        sample_config = {
            "DOWNLOAD_DIR": r"C:\\your\\download\\directory",
            "TRANSLATE_BAT": r"C:\\path\\to\\your\\translate_tool.bat",
            "SUBTITLE_DIR": r"C:\\path\\to\\subtitle\\output",
            "CHECK_INTERVAL": 10,
            "VIDEO_EXTENSIONS": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".m4v", ".webm"],
            "STATUS_FILE": "processing_status.json",
            "LOG_FILE": "subtitle_monitor.log",
            "DELETE_MODE": "backup",
            "MAX_CONCURRENT_TASKS": 3,
            "GPU_DETECTION": {
                "ENABLED": True,
                "MAX_TASKS_BY_GPU_TYPE": {
                    "集成显卡": 1,
                    "入门独显": 2,
                    "中端独显": 4,
                    "高端独显": 6,
                    "专业级显卡": 8
                }
            }
        }
        
        config_content = f'''# 配置文件 - 请根据实际情况修改路径
CONFIG = {json.dumps(sample_config, indent=4, ensure_ascii=False)}
'''
        
        try:
            with open("config_sample.py", "w", encoding="utf-8") as f:
                f.write(config_content)
            print("示例配置文件已创建: config_sample.py")
            print("请复制此文件为 config.py 并根据实际情况修改路径")
        except Exception as e:
            print(f"创建示例配置文件时出错: {e}")

def main():
    """配置向导主函数"""
    wizard = ConfigWizard()
    
    print("视频字幕翻译监控系统 - 配置向导")
    print("1. 运行配置向导")
    print("2. 创建示例配置文件")
    print("3. 检查当前配置")
    
    choice = input("请选择 (1-3): ").strip()
    
    if choice == "1":
        wizard.run_wizard()
    elif choice == "2":
        wizard.create_sample_config()
    elif choice == "3":
        missing, invalid = wizard.check_config_validity()
        if not missing and not invalid:
            print("当前配置有效")
        else:
            print("发现配置问题:")
            for item in missing + invalid:
                print(f"  - {item[1]}: {item[2]}")
    else:
        print("无效选择")

if __name__ == "__main__":
    main()