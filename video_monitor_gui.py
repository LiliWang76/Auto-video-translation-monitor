#!/usr/bin/env python3
"""
视频字幕翻译监控工具 - GUI完整版
作者：ChiangShenhung
开发工具：腾讯 Code Buddy CN
版本：2.0 完整版
设计思路和调试：ChiangShenhung
集成所有监控逻辑的图形界面版本
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import json
import threading
import time
from datetime import datetime

# 导入现有模块
from config import CONFIG
from file_monitor import FileMonitor, detect_gpu_type
from status_manager import StatusManager

class VideoMonitorGUI:
    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread = None
        self.file_monitor = None
        self.root = tk.Tk()
        self.root.title("视频字幕翻译监控工具 v1.0")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # 设置程序图标
        try:
            self.root.iconbitmap("")
        except:
            pass
        
        # 加载配置
        self.config = CONFIG.copy()
        
        # 显示显卡检测提示
        self.show_gpu_detection_info()
        
        self.setup_layout()
        self.load_current_config()
        
        # 初始化状态管理器
        self.status_manager = StatusManager()
        
        # 启动GUI更新循环
        self.update_interval = 2000  # 2秒更新一次
        self.update_gui()
        
    def get_detailed_gpu_info(self):
        """获取详细的显卡信息"""
        try:
            import wmi
            c = wmi.WMI()
            
            gpus = c.Win32_VideoController()
            if not gpus:
                return None
            
            gpu_info = []
            for gpu in gpus:
                info = {
                    'name': getattr(gpu, 'Name', '未知'),
                    'adapter_ram': getattr(gpu, 'AdapterRAM', 0),
                    'driver_version': getattr(gpu, 'DriverVersion', '未知'),
                    'video_processor': getattr(gpu, 'VideoProcessor', '未知')
                }
                gpu_info.append(info)
            
            return gpu_info
            
        except Exception as e:
            return None
    
    def show_gpu_detection_info(self):
        """显示显卡检测信息提示"""
        try:
            # 获取详细显卡信息
            gpu_info = self.get_detailed_gpu_info()
            if not gpu_info:
                return
            
            # 检测显卡类型
            detected_type = detect_gpu_type()
            
            # 构建提示信息
            message = "显卡检测信息：\n\n"
            for i, gpu in enumerate(gpu_info):
                message += f"显卡 {i+1}:\n"
                message += f"  型号: {gpu['name']}\n"
                if gpu['adapter_ram']:
                    ram_gb = gpu['adapter_ram'] / (1024**3)
                    message += f"  显存: {ram_gb:.1f} GB\n"
                if gpu['driver_version'] != '未知':
                    message += f"  驱动版本: {gpu['driver_version']}\n"
                message += "\n"
            
            message += f"检测到的显卡类型: {detected_type}\n"
            message += f"建议选择: {detected_type}\n\n"
            message += "您可以在\"显卡类型\"设置中选择其他选项，但请注意：\n"
            message += "• 选择高于检测结果的类型可能导致性能问题\n"
            message += "• 选择低于检测结果的类型会限制并发任务数量\n"
            
            # 显示提示框
            messagebox.showinfo("显卡检测信息", message)
            
        except Exception as e:
            # 如果检测失败，显示错误信息
            messagebox.showwarning("显卡检测", f"无法检测显卡信息: {e}\n\n请手动选择合适的显卡类型。")
        
    def setup_layout(self):
        """设置GUI布局"""
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置窗口权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题区域
        title_label = ttk.Label(main_frame, text="🎬 视频字幕翻译监控工具", 
                               font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame, text="自动监控视频文件并调用字幕翻译工具",
                                  font=("微软雅黑", 10))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="配置设置", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # 监控目录
        ttk.Label(config_frame, text="监控目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.download_dir_var = tk.StringVar()
        self.download_dir_entry = ttk.Entry(config_frame, textvariable=self.download_dir_var, width=50)
        self.download_dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(config_frame, text="选择文件夹", command=self.select_download_dir).grid(row=0, column=2, padx=5)
        
        # 翻译工具
        ttk.Label(config_frame, text="翻译工具:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.translate_bat_var = tk.StringVar()
        self.translate_bat_entry = ttk.Entry(config_frame, textvariable=self.translate_bat_var, width=50)
        self.translate_bat_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(config_frame, text="选择文件", command=self.select_translate_bat).grid(row=1, column=2, padx=5)
        
        # 字幕输出目录
        ttk.Label(config_frame, text="字幕输出:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.subtitle_dir_var = tk.StringVar()
        self.subtitle_dir_entry = ttk.Entry(config_frame, textvariable=self.subtitle_dir_var, width=50)
        self.subtitle_dir_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(config_frame, text="选择文件夹", command=self.select_subtitle_dir).grid(row=2, column=2, padx=5)
        
        # 显卡类型
        ttk.Label(config_frame, text="显卡类型:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.gpu_type_var = tk.StringVar(value="中端独显")
        gpu_frame = ttk.Frame(config_frame)
        gpu_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 显卡类型定义和说明（包含并发任务数）
        gpu_concurrent_tasks = {
            "集成显卡": 1,
            "入门独显": 2,
            "中端独显": 4,
            "高端独显": 6,
            "专业级显卡": 8
        }
        
        gpu_info = [
            ("集成显卡", "Intel UHD/HD系列 (仅NVIDIA CUDA显卡)", "如：Intel UHD 630 (仅软件加速)", gpu_concurrent_tasks["集成显卡"]),
            ("入门独显", "NVIDIA GTX 10/16系列 (CUDA 6.1+)", "如：GTX 1050, GTX 1650", gpu_concurrent_tasks["入门独显"]),
            ("中端独显", "NVIDIA RTX 20/30系列 (CUDA 7.5+)", "如：RTX 2060, RTX 3060", gpu_concurrent_tasks["中端独显"]),
            ("高端独显", "NVIDIA RTX 30/40系列 (CUDA 8.6+)", "如：RTX 3080, RTX 4080", gpu_concurrent_tasks["高端独显"]),
            ("专业级显卡", "NVIDIA Quadro/Tesla系列", "如：Quadro RTX 6000, Tesla V100", gpu_concurrent_tasks["专业级显卡"])
        ]
        
        for i, (gpu_type, series, examples, concurrent_tasks) in enumerate(gpu_info):
            btn = ttk.Radiobutton(gpu_frame, text=f"{gpu_type} ({concurrent_tasks}任务)", variable=self.gpu_type_var, 
                                value=gpu_type)
            btn.grid(row=0, column=i, sticky=tk.W, padx=5)
            # 添加工具提示，显示具体系列、示例和并发任务数
            tooltip_text = f"{series}\n示例：{examples}\n\n最大并发任务数：{concurrent_tasks}"
            self.create_tooltip(btn, tooltip_text)
        
        # 添加说明标签（放在新的一行，避免遮挡）
        gpu_help_label = ttk.Label(config_frame, text="⚠️ 仅支持NVIDIA显卡 (CUDA加速)，AMD显卡需使用CPU模式", 
                                  foreground="red")
        gpu_help_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # 处理原视频方式
        ttk.Label(config_frame, text="处理原视频:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.delete_mode_var = tk.StringVar(value="backup")
        delete_frame = ttk.Frame(config_frame)
        delete_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        delete_modes = [
            ("备份模式", "backup", "将处理完成的视频移动到备份目录"),
            ("移动到回收站", "recycle_bin", "将视频文件移动到回收站"),
            ("直接删除", "delete", "永久删除视频文件")
        ]
        
        for i, (label, mode, tooltip) in enumerate(delete_modes):
            btn = ttk.Radiobutton(delete_frame, text=label, variable=self.delete_mode_var, 
                                value=mode)
            btn.grid(row=0, column=i, sticky=tk.W, padx=5)
            # 添加工具提示
            self.create_tooltip(btn, tooltip)
        
        # 控制按钮区域
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        self.start_btn = ttk.Button(control_frame, text="▶️  开始监控", 
                                   command=self.start_monitoring)
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="⏹️  停止监控", 
                                  command=self.stop_monitoring, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        ttk.Button(control_frame, text="⚙️  保存配置", command=self.save_config).grid(row=0, column=2, padx=5)
        ttk.Button(control_frame, text="❓ 帮助", command=self.show_help).grid(row=0, column=3, padx=5)
        
        # 状态显示区域
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="10")
        status_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="当前状态:", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, sticky=tk.W)
        self.status_label = ttk.Label(status_frame, text="监控未启动", foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(status_frame, text="任务统计:", font=("微软雅黑", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.stats_label = ttk.Label(status_frame, text="待处理: 0 | 进行中: 0 | 已完成: 0")
        self.stats_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # 日志显示区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=15, 
                                                 state="disabled", bg="#f0f0f0")
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 日志控制按钮
        log_buttons_frame = ttk.Frame(log_frame)
        log_buttons_frame.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
        
        ttk.Button(log_buttons_frame, text="复制日志", command=self.copy_log).grid(row=0, column=0, padx=2)
        ttk.Button(log_buttons_frame, text="清空日志", command=self.clear_log).grid(row=0, column=1, padx=2)
        ttk.Button(log_buttons_frame, text="保存日志", command=self.save_log).grid(row=0, column=2, padx=2)
        
        # 设置行权重
        main_frame.rowconfigure(5, weight=1)
        
    def load_current_config(self):
        """加载当前配置到界面"""
        try:
            self.download_dir_var.set(self.config.get("DOWNLOAD_DIR", ""))
            self.translate_bat_var.set(self.config.get("TRANSLATE_BAT", ""))
            self.subtitle_dir_var.set(self.config.get("SUBTITLE_DIR", ""))
            
            # 加载处理原视频方式
            self.delete_mode_var.set(self.config.get("DELETE_MODE", "backup"))
            
            # 加载显卡类型
            self.gpu_type_var.set(self.config.get("GPU_TYPE", "中端独显"))
            
        except Exception as e:
            self.log(f"加载配置失败: {e}")
    
    def select_download_dir(self):
        """选择监控目录"""
        directory = filedialog.askdirectory(title="选择监控目录")
        if directory:
            self.download_dir_var.set(directory)
    
    def select_translate_bat(self):
        """选择翻译工具"""
        filename = filedialog.askopenfilename(
            title="选择字幕翻译工具",
            filetypes=[("批处理文件", "*.bat"), ("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.translate_bat_var.set(filename)
    
    def select_subtitle_dir(self):
        """选择字幕输出目录"""
        directory = filedialog.askdirectory(title="选择字幕输出目录")
        if directory:
            self.subtitle_dir_var.set(directory)
    
    def validate_config(self):
        """验证配置是否有效"""
        errors = []
        
        download_dir = self.download_dir_var.get().strip()
        if not download_dir:
            errors.append("请选择监控目录")
        elif not os.path.exists(download_dir):
            errors.append(f"监控目录不存在: {download_dir}")
        
        translate_bat = self.translate_bat_var.get().strip()
        if not translate_bat:
            errors.append("请选择翻译工具")
        elif not os.path.exists(translate_bat):
            errors.append(f"翻译工具不存在: {translate_bat}")
        
        subtitle_dir = self.subtitle_dir_var.get().strip()
        if not subtitle_dir:
            errors.append("请选择字幕输出目录")
        elif not os.path.exists(subtitle_dir):
            errors.append(f"字幕输出目录不存在: {subtitle_dir}")
        
        return errors
    
    def save_config(self):
        """保存配置到文件"""
        errors = self.validate_config()
        if errors:
            messagebox.showerror("配置错误", "\n".join(errors))
            return
        
        try:
            # 更新配置
            self.config.update({
                "DOWNLOAD_DIR": self.download_dir_var.get().strip(),
                "TRANSLATE_BAT": self.translate_bat_var.get().strip(),
                "SUBTITLE_DIR": self.subtitle_dir_var.get().strip(),
                "DELETE_MODE": self.delete_mode_var.get(),
                "GPU_TYPE": self.gpu_type_var.get()
            })
            
            # 保存到配置文件
            with open('config.py', 'w', encoding='utf-8') as f:
                f.write("# 配置文件\n")
                import json
                # 确保布尔值保持正确格式
                config_str = json.dumps(self.config, ensure_ascii=False, indent=4)
                # 将JSON中的布尔值转换为Python布尔值
                config_str = config_str.replace(': true', ': True').replace(': false', ': False')
                f.write("CONFIG = " + config_str) 
            
            messagebox.showinfo("成功", "配置已保存成功！")
            self.log("配置已保存")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def start_monitoring(self):
        """开始监控"""
        errors = self.validate_config()
        if errors:
            messagebox.showerror("配置错误", "\n".join(errors))
            return
        
        if self.is_monitoring:
            messagebox.showwarning("警告", "监控已在运行中")
            return
        
        try:
            # 保存配置
            self.save_config()
            
            # 重新加载配置模块
            import importlib
            import config
            importlib.reload(config)
            
            # 创建文件监控器，传入当前GUI配置
            self.file_monitor = FileMonitor(self.config)
            
            # 启动监控线程
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            # 更新界面状态
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.status_label.config(text="监控运行中", foreground="green")
            
            self.log("监控已启动")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动监控失败: {e}")
            self.log(f"启动监控失败: {e}")
    
    def stop_monitoring(self):
        """停止监控"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        
        # 更新界面状态
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.status_label.config(text="监控已停止", foreground="red")
        
        self.log("监控已停止")
    
    def monitor_loop(self):
        """监控循环（在单独线程中运行）"""
        while self.is_monitoring:
            try:
                # 执行单次监控检查
                self.file_monitor.monitor_once()
                
                # 等待下次检查
                time.sleep(self.config.get("CHECK_INTERVAL", 10))
                
            except Exception as e:
                self.log(f"监控循环错误: {e}")
                time.sleep(10)  # 出错后等待10秒
    
    def update_gui(self):
        """更新GUI状态"""
        if self.is_monitoring and self.status_manager:
            try:
                # 获取任务统计
                processing_count = self.status_manager.get_processing_count()
                processed_count = len(self.status_manager.status_data.get("processed", []))
                
                # 获取待处理文件数
                if self.file_monitor:
                    new_files = self.file_monitor.check_new_video_files()
                    pending_count = len(new_files)
                else:
                    pending_count = 0
                
                # 更新统计显示
                stats_text = f"待处理: {pending_count} | 进行中: {processing_count} | 已完成: {processed_count}"
                self.stats_label.config(text=stats_text)
                
            except Exception as e:
                self.log(f"更新统计信息失败: {e}")
        
        # 继续循环更新
        self.root.after(self.update_interval, self.update_gui)
    
    def create_tooltip(self, widget, text):
        """创建工具提示"""
        def on_enter(event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=text, justify='left',
                           background='#ffffe0', relief='solid', borderwidth=1)
            label.pack(ipadx=1)
        
        def on_leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
        
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def log(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
    
    def copy_log(self):
        """复制日志内容"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(log_content)
            messagebox.showinfo("成功", "日志已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制日志失败: {e}")
    
    def clear_log(self):
        """清空日志"""
        if messagebox.askyesno("确认", "确定要清空日志吗？"):
            self.log_text.config(state="normal")
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state="disabled")
            self.log("日志已清空")
    
    def save_log(self):
        """保存日志到文件"""
        try:
            filename = filedialog.asksaveasfilename(
                title="保存日志文件",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if filename:
                log_content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                messagebox.showinfo("成功", f"日志已保存到: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"保存日志失败: {e}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """视频字幕翻译监控工具 - 使用说明

功能说明：
1. 自动监控指定目录中的视频文件
2. 调用字幕翻译工具生成字幕
3. 完成后自动处理原视频文件

使用步骤：
1. 设置监控目录（视频文件所在目录）
2. 选择字幕翻译工具（.bat或.exe文件）
3. 设置字幕输出目录
4. 选择显卡类型（影响并发任务数）
5. 点击"开始监控"

注意事项：
- 确保所有路径都存在且可访问
- 翻译工具需要支持命令行调用
- 监控过程中不要移动或删除文件

技术支持：如有问题请查看日志信息
"""
        messagebox.showinfo("使用帮助", help_text)
    
    def run(self):
        """运行GUI主循环"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.stop_monitoring()
            self.root.destroy()

def main():
    """主函数"""
    try:
        app = VideoMonitorGUI()
        app.run()
    except Exception as e:
        print(f"GUI启动失败: {e}")
        messagebox.showerror("错误", f"程序启动失败: {e}")

if __name__ == "__main__":
    main()