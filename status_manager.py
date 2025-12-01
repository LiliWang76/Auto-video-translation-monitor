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
    def __init__(self):
        self.status_file = CONFIG["STATUS_FILE"]
        self._load_status()
    
    def _load_status(self):
        """加载处理状态"""
        if os.path.exists(self.status_file):
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    self.status_data = json.load(f)
            except:
                self.status_data = {"processed": [], "processing": {}}
        else:
            self.status_data = {"processed": [], "processing": {}}
    
    def _save_status(self):
        """保存处理状态"""
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(self.status_data, f, ensure_ascii=False, indent=2)
    
    def is_file_processed(self, file_path):
        """检查文件是否已经处理过"""
        filename = os.path.basename(file_path)
        return filename in self.status_data["processed"]
    
    def is_file_processing(self, file_path):
        """检查文件是否正在处理中"""
        filename = os.path.basename(file_path)
        # 如果文件已经被标记为已处理，则不应该再被认为是处理中
        if filename in self.status_data["processed"]:
            return False
        return filename in self.status_data["processing"]
    
    def mark_as_processing(self, file_path):
        """标记文件为处理中"""
        filename = os.path.basename(file_path)
        self.status_data["processing"][filename] = {
            "start_time": self._get_current_time(),
            "file_path": file_path
        }
        self._save_status()
    
    def mark_as_completed(self, file_path):
        """标记文件为已完成"""
        filename = os.path.basename(file_path)
        
        # 从处理中移除
        if filename in self.status_data["processing"]:
            del self.status_data["processing"][filename]
        
        # 添加到已处理列表
        if filename not in self.status_data["processed"]:
            self.status_data["processed"].append(filename)
        
        self._save_status()
    
    def remove_from_processing(self, file_path):
        """从处理中状态移除（用于异常情况）"""
        filename = os.path.basename(file_path)
        if filename in self.status_data["processing"]:
            del self.status_data["processing"][filename]
            self._save_status()
    
    def get_processing_files(self):
        """获取正在处理中的文件列表"""
        return list(self.status_data["processing"].keys())
    
    def get_processing_count(self):
        """获取当前正在处理的任务数量，确保加载最新状态"""
        # 重新加载状态文件以确保获取最新数据
        self._load_status()
        return len(self.status_data["processing"])
    
    def _get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def cleanup_stale_processing(self):
        """清理长时间处于处理状态的文件（超过2小时）或文件不存在的状态"""
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
                stale_files.append(filename)
        
        for filename in stale_files:
            if filename in self.status_data["processing"]:
                del self.status_data["processing"][filename]
        
        if stale_files:
            self._save_status()
            return stale_files
        
        return []