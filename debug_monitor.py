#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：用于诊断视频字幕监控系统的问题
"""

import os
import sys
from config import CONFIG
from status_manager import StatusManager

def debug_status():
    """调试状态管理"""
    print("=== 状态调试 ===")
    
    status_manager = StatusManager()
    
    # 检查处理中的文件
    processing_files = status_manager.get_processing_files()
    print(f"正在处理的文件数量: {len(processing_files)}")
    
    for filename in processing_files:
        print(f"处理中: {filename}")
    
    # 检查已处理的文件
    print(f"已处理的文件数量: {len(status_manager.status_data['processed'])}")
    
    return processing_files

def debug_directory_structure():
    """调试目录结构"""
    print("\n=== 目录结构调试 ===")
    
    download_dir = CONFIG["DOWNLOAD_DIR"]
    subtitle_dir = CONFIG["SUBTITLE_DIR"]
    
    print(f"下载目录: {download_dir}")
    print(f"字幕目录: {subtitle_dir}")
    
    # 检查下载目录
    if os.path.exists(download_dir):
        video_files = []
        for filename in os.listdir(download_dir):
            file_path = os.path.join(download_dir, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename)
                if ext.lower() in CONFIG["VIDEO_EXTENSIONS"]:
                    video_files.append(filename)
        
        print(f"下载目录中的视频文件: {len(video_files)}")
        for filename in video_files:
            print(f"  - {filename}")
    else:
        print("下载目录不存在")
    
    # 检查字幕目录
    if os.path.exists(subtitle_dir):
        subtitle_files = []
        for filename in os.listdir(subtitle_dir):
            if filename.endswith('.srt'):
                subtitle_files.append(filename)
        
        print(f"字幕目录中的字幕文件: {len(subtitle_files)}")
        for filename in subtitle_files:
            print(f"  - {filename}")
    else:
        print("字幕目录不存在")

def debug_subtitle_matching():
    """调试字幕文件匹配"""
    print("\n=== 字幕文件匹配调试 ===")
    
    download_dir = CONFIG["DOWNLOAD_DIR"]
    subtitle_dir = CONFIG["SUBTITLE_DIR"]
    status_manager = StatusManager()
    processing_files = status_manager.get_processing_files()
    
    if not os.path.exists(subtitle_dir):
        print("字幕目录不存在，无法进行匹配调试")
        return
    
    # 获取字幕目录中的所有字幕文件
    subtitle_files = []
    for filename in os.listdir(subtitle_dir):
        if filename.endswith('.srt'):
            subtitle_files.append(filename)
    
    print(f"字幕目录中的字幕文件: {len(subtitle_files)}")
    
    # 检查处理中的文件是否有对应的字幕文件
    matches = []
    for video_filename in processing_files:
        video_name = os.path.splitext(video_filename)[0]
        expected_subtitle = f"{video_name}.srt"
        
        if expected_subtitle in subtitle_files:
            subtitle_path = os.path.join(subtitle_dir, expected_subtitle)
            size = os.path.getsize(subtitle_path)
            matches.append((video_filename, expected_subtitle, size))
        else:
            print(f"未找到字幕文件: {video_filename} -> {expected_subtitle}")
    
    print(f"找到匹配的字幕文件: {len(matches)}")
    for video, subtitle, size in matches:
        print(f"  - {video} -> {subtitle} ({size} 字节)")

def main():
    """主调试函数"""
    print("视频字幕监控系统调试工具")
    print("=" * 50)
    
    # 调试状态管理
    processing_files = debug_status()
    
    # 调试目录结构
    debug_directory_structure()
    
    # 调试字幕文件匹配
    debug_subtitle_matching()
    
    print("\n=== 调试建议 ===")
    if not processing_files:
        print("1. 没有正在处理的文件，系统可能没有启动翻译任务")
        print("2. 检查是否有新的视频文件出现在下载目录")
        print("3. 检查监控系统是否正在运行")
    else:
        print("1. 检查对应的字幕文件是否已生成")
        print("2. 检查字幕文件是否可读且内容完整")
        print("3. 检查监控系统的日志文件查看详细信息")

if __name__ == "__main__":
    main()