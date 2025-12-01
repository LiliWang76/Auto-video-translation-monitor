"""
视频自动翻译监控系统
作者：ChiangShenhung
开发工具：腾讯 Code Buddy CN
版本：2.0
设计思路和调试：ChiangShenhung

主要功能：
1. 监控下载目录中的视频文件
2. 自动启动字幕翻译工具
3. 检测字幕文件生成完成
4. 根据配置清理原视频文件
5. 基于显卡性能限制并发任务数
"""

import os
import time
import subprocess
import logging
import shutil
import threading
import ctypes
from ctypes import wintypes
from config import CONFIG
from status_manager import StatusManager

# Windows API常量 - 用于文件删除到回收站
FO_DELETE = 0x0003      # 删除操作
FOF_ALLOWUNDO = 0x0040  # 允许撤销（即删除到回收站）
FOF_SILENT = 0x0004     # 静默操作
FOF_NOCONFIRMATION = 0x0010  # 不需要确认

# SHFileOperation结构体定义
class SHFILEOPSTRUCT(ctypes.Structure):
    """Windows API文件操作结构体"""
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("wFunc", wintypes.UINT),
        ("pFrom", wintypes.LPCWSTR),
        ("pTo", wintypes.LPCWSTR),
        ("fFlags", wintypes.UINT),
        ("fAnyOperationsAborted", wintypes.BOOL),
        ("hNameMappings", wintypes.LPVOID),
        ("lpszProgressTitle", wintypes.LPCWSTR)
    ]


def delete_to_recycle_bin(file_path: str) -> bool:
    """
    将文件安全删除到回收站
    
    参数:
        file_path: 要删除的文件路径
        
    返回:
        bool: 删除操作是否成功
        
    说明:
        使用Windows API实现安全的文件删除，避免直接永久删除
        适用于需要用户可恢复的文件操作场景
    """
    try:
        shell32 = ctypes.windll.shell32
        file_path = os.path.abspath(file_path)
        
        # 准备文件路径（需要双null结尾的Unicode字符串）
        from_path = file_path + '\0\0'
        
        # 配置文件操作参数
        shf = SHFILEOPSTRUCT()
        shf.wFunc = FO_DELETE
        shf.pFrom = from_path
        shf.pTo = None
        shf.fFlags = FOF_ALLOWUNDO | FOF_SILENT | FOF_NOCONFIRMATION
        shf.fAnyOperationsAborted = False
        shf.hNameMappings = None
        shf.lpszProgressTitle = None
        
        # 执行文件删除操作
        result = shell32.SHFileOperationW(ctypes.byref(shf))
        return result == 0  # 成功返回0
        
    except Exception as e:
        logging.error(f"删除到回收站失败: {file_path}, 错误: {e}")
        return False

def detect_gpu_type():
    """
    检测显卡类型
    如果自动检测失败，将提示用户手动输入显卡类型
    """
    try:
        import wmi
        c = wmi.WMI()
        
        # 获取显卡信息
        gpus = c.Win32_VideoController()
        if not gpus:
            logging.warning("未检测到显卡设备，使用默认配置")
            return "集成显卡"
        
        # 判断显卡类型
        for gpu in gpus:
            name = (gpu.Name or "").lower()
            adapter_ram = getattr(gpu, 'AdapterRAM', 0) or 0
            
            # 集成显卡判断
            if any(keyword in name for keyword in ['intel', 'intel(r)', 'hd graphics', 'uhd graphics', 'iris']):
                logging.info(f"检测到集成显卡: {gpu.Name}")
                return "集成显卡"
            
            # NVIDIA显卡
            if 'nvidia' in name or 'geforce' in name:
                if 'rtx' in name:
                    if '4090' in name or '4080' in name or '3090' in name:
                        logging.info(f"检测到高端独显: {gpu.Name}")
                        return "高端独显"
                    elif '4070' in name or '4060' in name or '3070' in name or '3060' in name:
                        logging.info(f"检测到中端独显: {gpu.Name}")
                        return "中端独显"
                    else:
                        logging.info(f"检测到入门独显: {gpu.Name}")
                        return "入门独显"
                elif 'gtx' in name:
                    if '1660' in name or '1650' in name:
                        logging.info(f"检测到入门独显: {gpu.Name}")
                        return "入门独显"
                    else:
                        logging.info(f"检测到中端独显: {gpu.Name}")
                        return "中端独显"
            
            # AMD显卡
            if 'amd' in name or 'radeon' in name:
                if 'rx' in name:
                    if '7900' in name or '7800' in name:
                        logging.info(f"检测到高端独显: {gpu.Name}")
                        return "高端独显"
                    elif '7700' in name or '7600' in name:
                        logging.info(f"检测到中端独显: {gpu.Name}")
                        return "中端独显"
                    else:
                        logging.info(f"检测到入门独显: {gpu.Name}")
                        return "入门独显"
        
        # 默认返回集成显卡
        logging.warning(f"无法确定显卡类型，使用默认配置。检测到的显卡: {gpus[0].Name if gpus else '未知'}")
        return "集成显卡"
        
    except ImportError:
        logging.warning("未安装wmi库，无法自动检测显卡类型")
        return manual_gpu_selection()
    except Exception as e:
        logging.warning(f"显卡检测失败: {e}")
        return manual_gpu_selection()

def manual_gpu_selection():
    """
    手动选择显卡类型
    当自动检测失败时，提示用户手动选择
    """
    print("\n=== 显卡类型选择 ===")
    print("自动检测显卡失败，请手动选择您的显卡类型：")
    print("1. 集成显卡 (Intel HD Graphics, Iris Xe等)")
    print("2. 入门级独显 (GTX 1650/1660, RTX 3050等)")
    print("3. 中端独显 (RTX 3060/3070/4060/4070等)")
    print("4. 高端独显 (RTX 3080/3090/4080/4090等)")
    print("5. 专业级显卡 (A100, H100, RTX A系列等)")
    
    while True:
        try:
            choice = input("请选择(1-5): ").strip()
            if choice == '1':
                return "集成显卡"
            elif choice == '2':
                return "入门独显"
            elif choice == '3':
                return "中端独显"
            elif choice == '4':
                return "高端独显"
            elif choice == '5':
                return "专业级显卡"
            else:
                print("无效选择，请输入1-5之间的数字")
        except KeyboardInterrupt:
            print("\n用户中断选择，使用默认配置")
            return "集成显卡"

# 全局变量：文件处理锁和已处理文件集合，用于避免并发冲突
_file_processing_lock = threading.Lock()
_processed_files = set()

class FileMonitor:
    """
    文件监控器类 - 负责监控视频文件并调用字幕翻译工具
    
    主要功能：
    - 监控指定目录中的视频文件
    - 调用字幕翻译工具处理视频
    - 检测字幕文件生成状态
    - 根据配置处理原视频文件
    - 基于显卡性能智能控制并发任务数
    """
    
    def __init__(self, config=None):
        """
        初始化文件监控器
        
        参数:
            config: 配置字典，如果为None则使用默认配置
        """
        # 使用传入的配置，如果没有传入则使用默认配置
        if config is None:
            config = CONFIG
        
        # 基础配置参数
        self.download_dir = config["DOWNLOAD_DIR"]
        self.translate_bat = config["TRANSLATE_BAT"]
        self.subtitle_dir = config["SUBTITLE_DIR"]
        self.video_extensions = config["VIDEO_EXTENSIONS"]
        self.delete_mode = config["DELETE_MODE"]
        
        # 初始化日志记录
        self.setup_logging()
        
        # 显卡检测和任务限制配置
        # 优先使用用户选择的显卡类型
        user_gpu_type = config.get("GPU_TYPE", "中端独显")
        user_gpu_max_tasks = config["GPU_DETECTION"]["MAX_TASKS_BY_GPU_TYPE"].get(user_gpu_type, 1)
        
        # 智能显卡检测逻辑：平衡用户选择和自动检测结果
        if config["GPU_DETECTION"]["ENABLED"]:
            detected_gpu = detect_gpu_type()
            detected_gpu_max_tasks = config["GPU_DETECTION"]["MAX_TASKS_BY_GPU_TYPE"].get(detected_gpu, 1)
            
            if user_gpu_type != detected_gpu:
                # 用户选择与检测结果不同，尊重用户选择
                self.max_concurrent_tasks = user_gpu_max_tasks
                self.logger.info(f"用户选择显卡类型: {user_gpu_type}, 检测到显卡类型: {detected_gpu}")
                self.logger.info(f"使用用户选择的设置，最大并发任务数: {self.max_concurrent_tasks}")
            else:
                # 用户选择与检测结果一致，使用检测到的最大值
                self.max_concurrent_tasks = detected_gpu_max_tasks
                self.logger.info(f"检测到显卡类型: {detected_gpu}, 最大并发任务数: {self.max_concurrent_tasks}")
        else:
            # 显卡检测未启用，直接使用用户选择
            self.max_concurrent_tasks = user_gpu_max_tasks
            self.logger.info(f"使用用户选择的显卡类型: {user_gpu_type}, 最大并发任务数: {self.max_concurrent_tasks}")
        
        # 初始化状态管理器
        self.status_manager = StatusManager()
        self.setup_logging()
    
    def setup_logging(self):
        """
        设置日志记录系统
        
        配置日志记录器，同时输出到文件和控制台
        日志格式：时间戳 - 日志级别 - 日志消息
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(CONFIG["LOG_FILE"], encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_video_files(self):
        """
        获取下载目录中的视频文件列表
        
        返回:
            list: 视频文件路径列表
            
        异常处理:
            - 如果目录不存在，记录错误并返回空列表
            - 如果读取目录失败，记录错误并返回已找到的文件列表
        """
        if not os.path.exists(self.download_dir):
            self.logger.error(f"下载目录不存在: {self.download_dir}")
            return []
        
        video_files = []
        try:
            for filename in os.listdir(self.download_dir):
                file_path = os.path.join(self.download_dir, filename)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(filename)
                    if ext.lower() in self.video_extensions:
                        video_files.append(file_path)
        except Exception as e:
            self.logger.error(f"读取下载目录失败: {e}")
        
        return video_files
    
    def is_subtitle_generated(self, video_path):
        """
        检查字幕文件是否已生成
        
        参数:
            video_path: 视频文件路径
            
        返回:
            bool: 字幕文件是否存在
            
        说明:
            根据视频文件名生成对应的.srt字幕文件路径并检查是否存在
        """
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        subtitle_path = os.path.join(self.subtitle_dir, f"{video_name}.srt")
        
        return os.path.exists(subtitle_path)
    
    def execute_translation(self, video_path):
        """执行字幕翻译 - 直接调用infer.exe，保持窗口可见"""
        try:
            # 检查bat文件是否存在
            if not os.path.exists(self.translate_bat):
                self.logger.error(f"字幕翻译工具不存在: {self.translate_bat}")
                return False
            
            # 检查视频文件是否存在
            if not os.path.exists(video_path):
                self.logger.error(f"视频文件不存在: {video_path}")
                return False
            
            # 尝试直接调用infer.exe（避免BAT文件窗口快速关闭）
            bat_dir = os.path.dirname(self.translate_bat)
            infer_exe = os.path.join(bat_dir, "infer.exe")
            
            if os.path.exists(infer_exe):
                # 直接调用infer.exe，保持窗口可见
                cmd = [
                    infer_exe,
                    "--audio_suffixes=mp3,wav,flac,m4a,aac,ogg,wma,mp4,mkv,avi,mov,webm,flv,wmv",
                    "--sub_formats=srt",
                    f"--output_dir={self.subtitle_dir}",
                    "--device=cuda",
                    video_path
                ]
                
                self.logger.info(f"启动字幕翻译工具 (直接调用infer.exe): {os.path.basename(video_path)}")
                process = subprocess.Popen(cmd, 
                                         shell=False,
                                         creationflags=subprocess.CREATE_NEW_CONSOLE,
                                         cwd=bat_dir)
                
                # 检查进程是否成功启动
                if process.poll() is not None:  # 如果进程已经结束
                    self.logger.error(f"字幕翻译工具启动失败: {os.path.basename(video_path)}")
                    return False
                
                self.logger.info(f"已启动字幕翻译工具（新窗口）: {os.path.basename(video_path)}")
                return True
            else:
                # 如果infer.exe不存在，使用原来的BAT文件方式
                self.logger.warning(f"未找到infer.exe，使用BAT文件方式: {infer_exe}")
                process = subprocess.Popen([self.translate_bat, video_path], 
                                         shell=True,
                                         creationflags=subprocess.CREATE_NEW_CONSOLE,
                                         cwd=bat_dir)
                
                # 检查进程是否成功启动
                if process.poll() is not None:  # 如果进程已经结束
                    self.logger.error(f"BAT文件启动失败: {os.path.basename(video_path)}")
                    return False
                
                self.logger.info(f"已启动字幕翻译工具（新窗口）: {os.path.basename(video_path)}")
                return True
                
        except Exception as e:
            self.logger.error(f"执行字幕翻译时出错: {e}")
            return False
    
    def check_subtitle_completion(self, video_path):
        """检查字幕文件是否生成完成"""
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        subtitle_path = os.path.join(self.subtitle_dir, f"{video_name}.srt")
        
        if os.path.exists(subtitle_path):
            # 检查字幕文件大小是否稳定（避免文件正在写入中）
            size = os.path.getsize(subtitle_path)
            
            # 统一使用100字节作为有效阈值（避免空文件）
            if size > 100:
                self.logger.info(f"字幕文件生成完成: {video_name}.srt")
                return True
            elif size == 0:
                # 如果是0字节文件，可能是视频没有声音，直接返回失败
                self.logger.warning(f"检测到空字幕文件（0字节），视频可能没有声音: {video_name}.srt")
                return True  # 返回True让后续逻辑处理这个特殊情况
        
        return False
    
    def cleanup_video_file(self, video_path):
        """根据配置清理原视频文件"""
        max_retries = 3
        retry_delay = 5  # 秒
        
        for attempt in range(max_retries):
            try:
                if not os.path.exists(video_path):
                    self.logger.warning(f"视频文件不存在，无法处理: {video_path}")
                    return False
                
                video_name = os.path.basename(video_path)
                
                # 根据删除模式处理文件
                if self.delete_mode == "recycle_bin":
                    # 删除到回收站
                    if delete_to_recycle_bin(video_path):
                        self.logger.info(f"已删除视频文件到回收站: {video_name}")
                        return True
                    else:
                        self.logger.error(f"删除到回收站失败: {video_name}")
                        return False
                        
                elif self.delete_mode == "delete":
                    # 直接删除
                    os.remove(video_path)
                    self.logger.info(f"已直接删除视频文件: {video_name}")
                    return True
                    
                else:  # backup模式（默认）
                    # 创建备份目录
                    backup_dir = os.path.join(os.path.dirname(video_path), "已处理视频备份")
                    os.makedirs(backup_dir, exist_ok=True)
                    
                    # 生成唯一的备份文件名（避免重复）
                    name, ext = os.path.splitext(video_name)
                    timestamp = int(time.time())
                    backup_name = f"{name}_{timestamp}{ext}"
                    backup_path = os.path.join(backup_dir, backup_name)
                    
                    # 尝试移动文件
                    shutil.move(video_path, backup_path)
                    
                    self.logger.info(f"已移动视频文件到备份目录: {backup_name}")
                    return True
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(f"文件处理失败，第{attempt + 1}次重试: {e}")
                    time.sleep(retry_delay)
                else:
                    self.logger.error(f"文件处理失败，已达到最大重试次数: {e}")
                    return False
        return False
    
    def process_video(self, video_path):
        """处理单个视频文件"""
        video_name = os.path.basename(video_path)
        
        # 检查文件状态
        if self.status_manager.is_file_processed(video_path):
            self.logger.info(f"视频已处理过，跳过: {video_name}")
            return False
        
        if self.status_manager.is_file_processing(video_path):
            self.logger.info(f"视频正在处理中，跳过: {video_name}")
            return False
        
        # 标记为处理中
        self.status_manager.mark_as_processing(video_path)
        self.logger.info(f"开始处理视频: {video_name}")
        
        try:
            # 执行字幕翻译
            if not self.execute_translation(video_path):
                self.status_manager.remove_from_processing(video_path)
                return False
            
            # 立即返回True，让字幕检测在后台进行
            # 字幕检测将在后续的监控循环中完成
            return True
                
        except Exception as e:
            self.logger.error(f"处理视频时发生错误: {video_name}, 错误: {e}")
            self.status_manager.remove_from_processing(video_path)
            return False
    
    def check_all_processing_files(self):
        """检查所有正在处理文件的完成状态"""
        processing_files = self.status_manager.get_processing_files()
        completed_files = []
        failed_files = []
        
        for filename in processing_files:
            # 重建文件路径
            video_path = os.path.join(self.download_dir, filename)
            video_name = os.path.splitext(filename)[0]
            subtitle_path = os.path.join(self.subtitle_dir, f"{video_name}.srt")
            
            # 检查字幕文件是否存在
            if os.path.exists(subtitle_path):
                try:
                    # 检查文件大小
                    size = os.path.getsize(subtitle_path)
                    
                    # 智能字幕文件检测逻辑
                    if size > 100:  # 正常大小的字幕文件
                        # 检查文件是否可以读取且内容有效
                        with open(subtitle_path, 'r', encoding='utf-8') as f:
                            content = f.read(500)  # 读取前500个字符
                            
                            # 等待一段时间确保文件写入完成
                            time.sleep(2)
                            
                            # 再次检查文件大小是否稳定
                            new_size = os.path.getsize(subtitle_path)
                            
                            if new_size > 100:
                                # 字幕文件已稳定生成，完成处理
                                self.logger.info(f"检测到有效字幕文件（{new_size}字节）: {filename}")
                                
                                # 验证字幕内容
                                if self._is_basic_subtitle_content(content):
                                    if self.cleanup_video_file(video_path):
                                        self.status_manager.mark_as_completed(video_path)
                                        self.logger.info(f"已成功完成处理: {filename}")
                                        completed_files.append(filename)
                                    else:
                                        self.logger.error(f"处理视频文件失败: {filename}")
                                else:
                                    self.logger.warning(f"字幕文件内容格式不标准，但文件存在: {filename}")
                                    if self.cleanup_video_file(video_path):
                                        self.status_manager.mark_as_completed(video_path)
                                        self.logger.info(f"已成功完成处理（内容格式不标准）: {filename}")
                                        completed_files.append(filename)
                            else:
                                self.logger.warning(f"字幕文件大小不稳定: {filename}")
                    
                    elif size == 0:  # 空字幕文件（视频可能没有声音）
                        # 检查任务处理时间是否超过超时阈值
                        if self._should_mark_as_failed(filename):
                            self.logger.warning(f"检测到空字幕文件（0字节），任务超时，标记为失败: {filename}")
                            self.status_manager.remove_from_processing(video_path)
                            failed_files.append(filename)
                        else:
                            self.logger.warning(f"检测到空字幕文件（0字节），等待翻译完成: {filename}")
                    
                    elif size <= 100:  # 非常小的文件（可能出错）
                        # 检查任务处理时间是否超过超时阈值
                        if self._should_mark_as_failed(filename):
                            self.logger.warning(f"字幕文件太小（{size}字节），任务超时，标记为失败: {filename}")
                            self.status_manager.remove_from_processing(video_path)
                            failed_files.append(filename)
                        else:
                            self.logger.warning(f"字幕文件太小（{size}字节），等待翻译完成: {filename}")
                            
                except PermissionError:
                    self.logger.warning(f"字幕文件被占用，等待下次检查: {filename}")
                except Exception as e:
                    self.logger.warning(f"检查字幕文件状态时出错: {filename}, 错误: {e}")
            else:
                # 字幕文件不存在，检查是否应该清理长时间挂起的任务
                self._check_and_cleanup_stuck_task(filename)
        
        # 记录失败的任务
        if failed_files:
            self.logger.warning(f"标记为失败的任务: {failed_files}")
        
        return completed_files
    
    def _is_valid_subtitle_content(self, content):
        """检查字幕内容是否有效"""
        # 检查是否包含常见的字幕格式标识
        # 1. 包含时间戳格式（如：00:00:00,000 --> 00:00:02,000）
        # 2. 包含数字序号
        # 3. 内容长度合理
        
        lines = content.strip().split('\n')
        
        # 检查是否有时间戳格式
        timestamp_patterns = ['-->', ':', ',']
        for line in lines:
            if any(pattern in line for pattern in timestamp_patterns):
                return True
        
        # 检查是否有数字序号（字幕通常以数字开头）
        for line in lines:
            if line.strip().isdigit():
                return True
        
        return False
    
    def _is_basic_subtitle_content(self, content):
        """简化的字幕内容检查 - 只要包含一定数量的文字就认为是有效的"""
        # 简化检查：只要内容包含一定数量的字符就认为是有效的
        if len(content.strip()) > 50:  # 至少有50个字符
            return True
        
        # 或者检查是否包含常见的字幕关键词
        subtitle_keywords = ['字幕', 'subtitle', '时间', '时间轴', '对话', 'speech']
        for keyword in subtitle_keywords:
            if keyword.lower() in content.lower():
                return True
        
        return False
    
    def _should_mark_as_failed(self, filename):
        """检查任务是否应该标记为失败（基于处理时间）"""
        from datetime import datetime
        
        # 获取任务开始时间
        processing_info = self.status_manager.status_data["processing"].get(filename, {})
        start_time_str = processing_info.get("start_time", "")
        
        if start_time_str:
            try:
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                current_time = datetime.now()
                
                # 如果任务超过30分钟仍未完成有效字幕文件，认为失败
                # 对于空文件或小文件，缩短超时时间
                if (current_time - start_time).total_seconds() > 1800:  # 30分钟
                    return True
            except:
                pass
        
        return False
    
    def _check_and_cleanup_stuck_task(self, filename):
        """检查并清理卡住的任务"""
        from datetime import datetime
        
        # 获取任务开始时间
        processing_info = self.status_manager.status_data["processing"].get(filename, {})
        start_time_str = processing_info.get("start_time", "")
        
        if start_time_str:
            try:
                start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
                current_time = datetime.now()
                
                # 如果任务超过2小时仍未完成，认为卡住了
                if (current_time - start_time).total_seconds() > 7200:  # 2小时
                    self.logger.warning(f"检测到卡住的任务: {filename}，开始时间: {start_time_str}")
                    # 从处理中移除，但不标记为已完成
                    video_path = os.path.join(self.download_dir, filename)
                    self.status_manager.remove_from_processing(video_path)
                    self.logger.info(f"已清理卡住的任务: {filename}")
            except:
                pass
    
    def check_new_video_files(self):
        """检查新视频文件"""
        all_video_files = self.get_video_files()
        new_video_files = []
        
        for video_path in all_video_files:
            # 检查是否已经处理过或正在处理
            if (not self.status_manager.is_file_processed(video_path) and 
                not self.status_manager.is_file_processing(video_path)):
                # 额外的安全检查：确保文件实际存在且未被占用
                if os.path.exists(video_path):
                    try:
                        # 尝试打开文件以确保未被其他进程占用
                        with open(video_path, 'rb') as f:
                            f.read(1)  # 读取一个字节测试
                        new_video_files.append(video_path)
                    except (IOError, PermissionError):
                        self.logger.warning(f"文件被占用，跳过处理: {os.path.basename(video_path)}")
                else:
                    self.logger.warning(f"文件不存在，跳过处理: {os.path.basename(video_path)}")
        
        return new_video_files
    
    def monitor_once(self):
        """执行单次检查"""
        self.logger.info("执行单次检查...")
        
        # 1. 清理过期的处理状态
        stale_files = self.status_manager.cleanup_stale_processing()
        if stale_files:
            self.logger.info(f"清理了过期的处理状态: {stale_files}")
        
        # 2. 检查所有正在处理文件的完成状态
        completed_files = self.check_all_processing_files()
        if completed_files:
            self.logger.info(f"完成了 {len(completed_files)} 个文件: {completed_files}")
        
        # 3. 获取当前正在处理的任务数量
        current_processing_count = self.status_manager.get_processing_count()
        self.logger.info(f"当前正在处理的任务数: {current_processing_count}/{self.max_concurrent_tasks}")
        
        # 4. 如果已达到最大任务数，跳过新任务启动
        if current_processing_count >= self.max_concurrent_tasks:
            self.logger.info(f"已达到最大并发任务数({self.max_concurrent_tasks})，等待任务完成")
            return
        
        # 5. 检查新视频文件
        new_video_files = self.check_new_video_files()
        
        if new_video_files:
            self.logger.info(f"发现 {len(new_video_files)} 个新视频文件")
            
            # 计算可启动的新任务数量
            available_slots = self.max_concurrent_tasks - current_processing_count
            tasks_to_start = min(len(new_video_files), available_slots)
            
            if tasks_to_start > 0:
                self.logger.info(f"可启动 {tasks_to_start} 个新任务")
                
                # 启动新任务
                for video_path in new_video_files[:tasks_to_start]:
                    self.process_video(video_path)
            else:
                self.logger.info("无可用任务槽位，等待任务完成")
        else:
            self.logger.info("未发现新的视频文件")
    
    def monitor_loop(self):
        """监控循环"""
        self.logger.info("开始监控字幕翻译...")
        self.logger.info(f"监控目录: {self.download_dir}")
        self.logger.info(f"字幕输出目录: {self.subtitle_dir}")
        
        # 清理过期的处理状态
        stale_files = self.status_manager.cleanup_stale_processing()
        if stale_files:
            self.logger.info(f"清理了过期的处理状态: {stale_files}")
        
        try:
            while True:
                try:
                    # 使用monitor_once进行并行处理
                    self.monitor_once()
                    
                    # 等待下次检查
                    time.sleep(CONFIG["CHECK_INTERVAL"])
                    
                except KeyboardInterrupt:
                    # 重新抛出KeyboardInterrupt，让外层的异常处理捕获
                    raise
                except Exception as e:
                    self.logger.error(f"监控循环发生错误: {e}")
                    time.sleep(CONFIG["CHECK_INTERVAL"])  # 出错后等待下次检查
        
        except KeyboardInterrupt:
            self.logger.info("用户中断监控，正在清理处理中的任务状态...")
            self._cleanup_processing_on_exit()
            self.logger.info("程序退出")
            # 重新抛出KeyboardInterrupt，让main.py中的异常处理捕获
            raise
    
    def _cleanup_processing_on_exit(self):
        """在程序退出时清理所有处理中的任务状态"""
        processing_files = self.status_manager.get_processing_files()
        if processing_files:
            self.logger.info(f"清理 {len(processing_files)} 个处理中的任务状态...")
            for filename in processing_files:
                video_path = os.path.join(self.download_dir, filename)
                self.status_manager.remove_from_processing(video_path)
                self.logger.info(f"已清理任务状态: {filename}")
            self.logger.info("所有处理中的任务状态已清理完成")
        else:
            self.logger.info("没有需要清理的处理中任务")