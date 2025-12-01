#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
状态修复工具：手动清理不存在的文件状态
"""

import json
import os
from config import CONFIG

def fix_processing_status():
    """修复处理状态文件"""
    status_file = CONFIG["STATUS_FILE"]
    
    if not os.path.exists(status_file):
        print("状态文件不存在，无需修复")
        return
    
    # 读取状态文件
    with open(status_file, 'r', encoding='utf-8') as f:
        status_data = json.load(f)
    
    print("=== 修复前状态 ===")
    print(f"正在处理的文件数: {len(status_data['processing'])}")
    for filename, info in status_data['processing'].items():
        file_path = info.get('file_path', '未知路径')
        exists = os.path.exists(file_path)
        print(f"  - {filename}: {'存在' if exists else '不存在'} ({file_path})")
    
    # 清理不存在的文件
    files_to_remove = []
    for filename, info in status_data['processing'].items():
        file_path = info.get('file_path')
        if file_path and not os.path.exists(file_path):
            files_to_remove.append(filename)
    
    for filename in files_to_remove:
        del status_data['processing'][filename]
        print(f"已移除不存在的文件状态: {filename}")
    
    # 保存修复后的状态
    if files_to_remove:
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
        
        print("\n=== 修复后状态 ===")
        print(f"正在处理的文件数: {len(status_data['processing'])}")
        for filename in status_data['processing']:
            print(f"  - {filename}")
        print(f"\n已成功修复状态文件，移除了 {len(files_to_remove)} 个不存在的文件状态")
    else:
        print("无需修复，所有文件状态正常")

def main():
    """主函数"""
    print("视频字幕监控系统状态修复工具")
    print("=" * 50)
    
    fix_processing_status()
    
    print("\n修复完成！现在可以重新启动监控系统")

if __name__ == "__main__":
    main()