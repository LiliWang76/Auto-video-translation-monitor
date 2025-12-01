#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
立即修复脚本：清理处理中的任务状态
用于解决用户中断程序后状态不一致的问题
"""

import json
import os
import logging
from config import CONFIG

# 设置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("immediate_fix.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def cleanup_processing_status():
    """清理处理中的任务状态"""
    status_file = CONFIG["STATUS_FILE"]
    download_dir = CONFIG["DOWNLOAD_DIR"]
    
    if not os.path.exists(status_file):
        logger.info("状态文件不存在，无需清理")
        return
    
    try:
        # 读取状态文件
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = json.load(f)
        
        logger.info(f"当前状态: 已处理 {len(status_data.get('processed', []))} 个文件")
        logger.info(f"当前状态: 处理中 {len(status_data.get('processing', {}))} 个文件")
        
        # 检查处理中的文件是否实际存在
        processing_files = list(status_data.get("processing", {}).keys())
        files_to_remove = []
        
        for filename in processing_files:
            file_path = os.path.join(download_dir, filename)
            if not os.path.exists(file_path):
                files_to_remove.append(filename)
                logger.info(f"文件不存在，标记为清理: {filename}")
            else:
                logger.info(f"文件存在，保留状态: {filename}")
        
        # 清理不存在的文件状态
        if files_to_remove:
            for filename in files_to_remove:
                if filename in status_data["processing"]:
                    del status_data["processing"][filename]
            
            # 保存清理后的状态
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"已清理 {len(files_to_remove)} 个不存在的文件状态")
        else:
            logger.info("没有需要清理的文件状态")
        
        # 显示清理后的状态
        logger.info(f"清理后状态: 已处理 {len(status_data.get('processed', []))} 个文件")
        logger.info(f"清理后状态: 处理中 {len(status_data.get('processing', {}))} 个文件")
        
        # 如果还有处理中的文件，检查是否需要强制清理
        remaining_processing = len(status_data.get("processing", {}))
        if remaining_processing > 0:
            logger.warning(f"仍有 {remaining_processing} 个文件在处理中")
            
            # 询问是否强制清理所有处理中状态
            response = input("是否强制清理所有处理中状态？(y/N): ").strip().lower()
            if response == 'y':
                status_data["processing"] = {}
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, ensure_ascii=False, indent=2)
                logger.info("已强制清理所有处理中状态")
        
    except Exception as e:
        logger.error(f"清理状态时出错: {e}")

def reset_all_status():
    """重置所有状态"""
    status_file = CONFIG["STATUS_FILE"]
    
    try:
        # 创建新的状态文件
        status_data = {"processed": [], "processing": {}}
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)
        
        logger.info("已重置所有状态")
        
    except Exception as e:
        logger.error(f"重置状态时出错: {e}")

if __name__ == "__main__":
    print("=== 立即修复脚本 ===")
    print("1. 清理处理中的任务状态")
    print("2. 重置所有状态（谨慎使用）")
    print("3. 退出")
    
    while True:
        choice = input("请选择操作 (1-3): ").strip()
        
        if choice == '1':
            cleanup_processing_status()
            break
        elif choice == '2':
            confirm = input("警告：这将重置所有状态，包括已处理记录！确定要继续吗？(y/N): ").strip().lower()
            if confirm == 'y':
                reset_all_status()
            break
        elif choice == '3':
            print("退出修复脚本")
            break
        else:
            print("无效选择，请输入1-3")
    
    print("修复完成，请重新启动监控程序")