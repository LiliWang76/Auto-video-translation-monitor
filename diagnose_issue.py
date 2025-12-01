#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断脚本：检查状态不一致问题
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
        logging.FileHandler("diagnose_issue.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def diagnose_status_issue():
    """诊断状态不一致问题"""
    status_file = CONFIG["STATUS_FILE"]
    download_dir = CONFIG["DOWNLOAD_DIR"]
    subtitle_dir = CONFIG["SUBTITLE_DIR"]
    
    logger.info("=== 开始诊断状态不一致问题 ===")
    
    # 1. 检查状态文件是否存在
    if not os.path.exists(status_file):
        logger.error("状态文件不存在")
        return
    
    # 2. 读取状态文件
    with open(status_file, 'r', encoding='utf-8') as f:
        status_data = json.load(f)
    
    logger.info(f"状态文件内容: {json.dumps(status_data, ensure_ascii=False, indent=2)}")
    
    # 3. 检查处理中文件状态
    processing_files = list(status_data.get("processing", {}).keys())
    processed_files = list(status_data.get("processed", []))
    
    logger.info(f"处理中文件数量: {len(processing_files)}")
    logger.info(f"已处理文件数量: {len(processed_files)}")
    
    # 4. 检查每个处理中文件的实际状态
    for filename in processing_files:
        video_path = os.path.join(download_dir, filename)
        video_name = os.path.splitext(filename)[0]
        subtitle_path = os.path.join(subtitle_dir, f"{video_name}.srt")
        
        logger.info(f"\n检查文件: {filename}")
        logger.info(f"视频文件存在: {os.path.exists(video_path)}")
        logger.info(f"字幕文件存在: {os.path.exists(subtitle_path)}")
        
        if os.path.exists(subtitle_path):
            try:
                size = os.path.getsize(subtitle_path)
                logger.info(f"字幕文件大小: {size} 字节")
                
                with open(subtitle_path, 'r', encoding='utf-8') as f:
                    content = f.read(200)
                    logger.info(f"字幕文件内容预览: {content[:100]}...")
            except Exception as e:
                logger.error(f"读取字幕文件失败: {e}")
    
    # 5. 检查下载目录中的实际文件
    logger.info(f"\n=== 检查下载目录中的实际文件 ===")
    if os.path.exists(download_dir):
        video_files = []
        for filename in os.listdir(download_dir):
            file_path = os.path.join(download_dir, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename)
                if ext.lower() in CONFIG["VIDEO_EXTENSIONS"]:
                    video_files.append(filename)
        
        logger.info(f"下载目录中的视频文件: {video_files}")
        
        # 检查哪些文件应该被处理但未被标记
        for filename in video_files:
            if filename not in processed_files and filename not in processing_files:
                logger.info(f"⚠️  文件 {filename} 应该被处理但未被标记")
    
    # 6. 检查字幕目录
    logger.info(f"\n=== 检查字幕目录中的文件 ===")
    if os.path.exists(subtitle_dir):
        subtitle_files = []
        for filename in os.listdir(subtitle_dir):
            if filename.endswith('.srt'):
                subtitle_files.append(filename)
        
        logger.info(f"字幕目录中的文件: {subtitle_files}")
        
        # 检查哪些字幕文件对应的视频文件未被标记为已处理
        for subtitle_file in subtitle_files:
            video_name = os.path.splitext(subtitle_file)[0]
            corresponding_videos = [f for f in video_files if f.startswith(video_name)]
            
            for video_file in corresponding_videos:
                if video_file not in processed_files:
                    logger.info(f"⚠️  字幕文件 {subtitle_file} 存在，但视频 {video_file} 未被标记为已处理")
    
    logger.info("=== 诊断完成 ===")

def check_status_manager():
    """检查状态管理器的实际行为"""
    logger.info("\n=== 检查状态管理器行为 ===")
    
    from status_manager import StatusManager
    
    status_manager = StatusManager()
    
    # 检查当前状态
    processing_count = status_manager.get_processing_count()
    processing_files = status_manager.get_processing_files()
    
    logger.info(f"状态管理器返回的处理中文件数量: {processing_count}")
    logger.info(f"状态管理器返回的处理中文件列表: {processing_files}")
    
    # 重新加载状态并再次检查
    status_manager._load_status()
    processing_count_after_reload = status_manager.get_processing_count()
    
    logger.info(f"重新加载后处理中文件数量: {processing_count_after_reload}")

if __name__ == "__main__":
    print("=== 状态不一致问题诊断工具 ===")
    
    diagnose_status_issue()
    check_status_manager()
    
    print("\n诊断完成，请查看 diagnose_issue.log 文件获取详细信息")