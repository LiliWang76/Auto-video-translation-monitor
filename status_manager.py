"""
状态管理器模块
作者：ChiangShenhung
开发工具：腾讯 Code Buddy CN
版本：2.0
设计思路和调试：ChiangShenhung

功能说明：
- 管理视频文件处理状态，避免重复处理
- 提供文件状态查询、标记和更新功能
- 支持JSON格式的状态持久化存储
"""

import json
import os
from config import CONFIG

class StatusManager:
    """
    状态管理器类 - 负责管理视频文件处理状态
    
    主要功能：
    - 跟踪文件处理状态（已处理、处理中）
    - 防止重复处理同一文件
    - 持久化存储状态信息到JSON文件
    - 清理异常状态（如文件不存在或超时）
    
    状态数据结构：
    {
        "processed": ["file1.mp4", "file2.avi"],  # 已处理的文件列表
        "processing": {                            # 正在处理中的文件
            "file3.mp4": {
                "start_time": "2024-01-01 10:00:00",
                "file_path": "/path/to/file3.mp4"
            }
        }
    }
    """
    
    def __init__(self):
        """
        初始化状态管理器
        
        加载状态文件，如果文件不存在则创建初始状态结构
        """
        self.status_file = CONFIG["STATUS_FILE"]
        self._load_status()
    
    def _load_status(self):
        """
        加载状态文件数据
        
        从JSON文件加载处理状态，如果文件不存在或格式错误则创建新的状态结构
        
        异常处理:
            - 文件不存在：创建新的状态结构
            - JSON解析错误：创建新的状态结构，避免程序崩溃
        """
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    self.status_data = json.load(f)
            except:
                # JSON解析失败，创建新的状态结构
                self.status_data = {"processed": [], "processing": {}}
        else:
            # 文件不存在，创建新的状态结构
            self.status_data = {"processed": [], "processing": {}}
    
    def _save_status(self):
        """
        保存状态数据到文件
        
        将当前状态数据以JSON格式保存到文件，确保中文正确显示
        使用缩进格式化，便于人工阅读和调试
        """
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(self.status_data, f, ensure_ascii=False, indent=2)
    
    def is_file_processed(self, file_path):
        """
        检查文件是否已经处理完成
        
        参数:
            file_path: 视频文件完整路径
            
        返回:
            bool: 如果文件已处理返回True，否则返回False
            
        说明:
            仅通过文件名判断，不考虑路径差异，避免重复处理同名文件
        """
        filename = os.path.basename(file_path)
        return filename in self.status_data["processed"]
    
    def is_file_processing(self, file_path):
        """
        检查文件是否正在处理中
        
        参数:
            file_path: 视频文件完整路径
            
        返回:
            bool: 如果文件正在处理中返回True，否则返回False
            
        说明:
            如果文件已被标记为已处理，则不会被认为是处理中状态
            避免同一文件同时处于处理和已完成状态
        """
        filename = os.path.basename(file_path)
        # 如果文件已经被标记为已处理，则不应该再被认为是处理中
        if filename in self.status_data["processed"]:
            return False
        return filename in self.status_data["processing"]
    
    def mark_as_processing(self, file_path):
        """
        标记文件为处理中状态
        
        参数:
            file_path: 视频文件完整路径
            
        说明:
            记录文件开始处理的时间戳和完整路径
            立即保存状态到文件，确保数据持久化
        """
        filename = os.path.basename(file_path)
        self.status_data["processing"][filename] = {
            "start_time": self._get_current_time(),
            "file_path": file_path
        }
        self._save_status()
    
    def mark_as_completed(self, file_path):
        """
        标记文件为已完成状态
        
        参数:
            file_path: 视频文件完整路径
            
        说明:
            1. 从处理中状态移除该文件
            2. 添加到已处理文件列表
            3. 保存状态到文件
        """
        filename = os.path.basename(file_path)
        
        # 从处理中移除
        if filename in self.status_data["processing"]:
            del self.status_data["processing"][filename]
        
        # 添加到已处理列表
        if filename not in self.status_data["processed"]:
            self.status_data["processed"].append(filename)
        
        self._save_status()
    
    def remove_from_processing(self, file_path):
        """
        从处理中状态移除文件（用于异常情况）
        
        参数:
            file_path: 视频文件完整路径
            
        说明:
            当处理过程中出现异常时调用此方法
            清理处理中状态，但不会标记为已完成
        """
        filename = os.path.basename(file_path)
        if filename in self.status_data["processing"]:
            del self.status_data["processing"][filename]
            self._save_status()
    
    def get_processing_files(self):
        """
        获取正在处理中的文件列表
        
        返回:
            list: 正在处理中的文件名列表
            
        说明:
            返回文件名列表，不包括文件路径信息
        """
        return list(self.status_data["processing"].keys())
    
    def get_processing_count(self):
        """
        获取当前正在处理的任务数量
        
        返回:
            int: 当前正在处理的任务数量
            
        说明:
            为确保获取最新状态，会重新加载状态文件
            适用于需要准确统计当前活跃任务数的场景
        """
        # 重新加载状态文件以确保获取最新数据
        self._load_status()
        return len(self.status_data["processing"])
    
    def _get_current_time(self):
        """
        获取当前时间字符串
        
        返回:
            str: 格式化的当前时间字符串（YYYY-MM-DD HH:MM:SS）
            
        说明:
            内部方法，用于记录处理开始时间
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def cleanup_stale_processing(self):
        """
        清理异常的处理状态
        
        清理条件：
        - 文件不存在（可能已被删除）
        - 处理时间超过2小时（可能卡死或异常退出）
        
        返回:
            list: 被清理的文件名列表
            
        说明:
            定期调用此方法可防止状态文件异常累积
            确保系统能够正确恢复异常中断的任务
        """
        from datetime import datetime, timedelta
        import os
        
        # 重新加载状态文件以确保获取最新数据
        self._load_status()
        
        current_time = datetime.now()
        stale_files = []
        
        for filename, info in self.status_data["processing"].items():
            try:
                # 检查文件是否存在
                file_path = info.get("file_path")
                if file_path and not os.path.exists(file_path):
                    stale_files.append(filename)
                    continue
                    
                # 检查是否超过2小时（缩短时间，避免任务卡死）
                start_time = datetime.strptime(info["start_time"], "%Y-%m-%d %H:%M:%S")
                if current_time - start_time > timedelta(hours=2):
                    stale_files.append(filename)
            except:
                # 解析时间戳失败或其他异常，标记为过期
                stale_files.append(filename)
        
        # 清理过期状态
        for filename in stale_files:
            if filename in self.status_data["processing"]:
                del self.status_data["processing"][filename]
        
        # 如果有清理操作，保存状态
        if stale_files:
            self._save_status()
            return stale_files
        
        return []