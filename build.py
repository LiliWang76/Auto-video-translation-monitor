#!/usr/bin/env python3
"""
视频字幕翻译监控工具 - 打包脚本
作者：ChiangShenhung
开发工具：腾讯 Code Buddy CN
版本：2.0
设计思路和调试：ChiangShenhung
使用PyInstaller打包GUI应用为可执行文件
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

def check_pyinstaller():
    """
    检查PyInstaller是否已安装
    
    返回:
        bool: PyInstaller是否可用
        
    说明:
        通过尝试导入PyInstaller模块来检测安装状态
    """
    try:
        import PyInstaller
        print("✓ PyInstaller已安装")
        return True
    except ImportError:
        print("✗ PyInstaller未安装")
        return False

def install_pyinstaller():
    """
    自动安装PyInstaller包
    
    返回:
        bool: 安装是否成功
        
    说明:
        使用pip命令安装PyInstaller，适用于打包环境准备
    """
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstaller安装失败: {e}")
        return False

def cleanup_build_dir():
    """
    清理构建过程中生成的临时目录
    
    清理的目录包括:
    - build: PyInstaller构建目录
    - dist: 输出目录
    - __pycache__: Python缓存目录
        
    说明:
        确保每次构建都是干净的，避免旧文件影响新构建
    """
    build_dirs = ["build", "dist", "__pycache__"]
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def create_spec_file():
    """
    创建PyInstaller配置文件（spec文件）
    
    功能:
    - 定义打包参数和配置
    - 指定包含的数据文件
    - 设置程序图标和窗口属性
    - 配置优化选项
    """
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['video_monitor_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.py', '.'),
        ('*.json', '.'),
        ('*.log', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 添加数据文件
# a.datas += collect_data_files('tkinter')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='视频字幕翻译监控工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False以隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('video_monitor.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ Spec文件创建成功")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 构建命令
    cmd = [
        'pyinstaller',
        '--onefile',  # 单文件模式
        '--windowed',  # 窗口模式（不显示控制台）
        '--name=视频字幕翻译监控工具',
        '--icon=icon.ico' if os.path.exists('icon.ico') else '',
        '--add-data=config.py;.',
        '--add-data=*.json;.',
        '--add-data=*.log;.',
        '--clean',  # 清理临时文件
        '--noconfirm',  # 不确认覆盖
        'video_monitor_gui.py'
    ]
    
    # 过滤空参数
    cmd = [arg for arg in cmd if arg]
    
    try:
        subprocess.check_call(cmd)
        print("✓ 可执行文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        return False

def create_installer_script():
    """创建安装脚本"""
    installer_content = '''@echo off
chcp 65001 >nul
title 视频字幕翻译监控工具 - 安装程序

echo ========================================
echo   视频字幕翻译监控工具 v1.0
echo ========================================
echo.
echo 正在准备安装...

REM 检查是否已存在旧版本
if exist "视频字幕翻译监控工具.exe" (
    echo 检测到旧版本，正在备份...
    if not exist "backup" mkdir backup
    move "视频字幕翻译监控工具.exe" "backup\视频字幕翻译监控工具_%date:~0,4%%date:~5,2%%date:~8,2%%time:~0,2%%time:~3,2%.exe"
)

REM 复制可执行文件
if exist "dist\\视频字幕翻译监控工具.exe" (
    copy "dist\\视频字幕翻译监控工具.exe" .
    echo ✓ 程序文件已安装
) else (
    echo ✗ 找不到可执行文件
    pause
    exit /b 1
)

REM 创建配置文件（如果不存在）
if not exist "config.py" (
    echo # 默认配置文件 > config.py
    echo CONFIG = {} >> config.py
    echo ✓ 配置文件已创建
)

REM 创建启动脚本
@echo off > 启动监控工具.bat
echo @echo off >> 启动监控工具.bat
echo chcp 65001 ^>nul >> 启动监控工具.bat
echo echo 正在启动视频字幕翻译监控工具... >> 启动监控工具.bat
echo "视频字幕翻译监控工具.exe" >> 启动监控工具.bat
echo pause >> 启动监控工具.bat

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 使用方法：
echo 1. 双击"启动监控工具.bat"运行程序
echo 2. 或直接双击"视频字幕翻译监控工具.exe"
echo 3. 首次运行请先设置监控目录和翻译工具
echo.
echo 按任意键退出...
pause >nul
'''
    
    with open('install.bat', 'w', encoding='utf-8') as f:
        f.write(installer_content)
    print("✓ 安装脚本创建成功")

def create_readme():
    """创建用户手册"""
    readme_content = '''# 视频字幕翻译监控工具 v1.0

## 功能简介

这是一个自动监控视频文件并调用字幕翻译工具的程序，具有以下功能：

- 🔍 自动监控指定目录中的视频文件
- 🎯 智能调用字幕翻译工具生成字幕
- 📊 实时显示监控状态和任务统计
- ⚙️ 图形化界面配置，简单易用
- 📋 详细的运行日志记录

## 系统要求

- Windows 7/8/10/11
- 无需安装Python环境
- 需要支持CUDA的显卡（用于字幕翻译）

## 安装说明

### 方法一：使用安装脚本（推荐）
1. 双击运行 `install.bat`
2. 按照提示完成安装
3. 安装完成后双击 `启动监控工具.bat`

### 方法二：手动安装
1. 将 `视频字幕翻译监控工具.exe` 复制到任意目录
2. 确保同目录下有 `config.py` 配置文件
3. 双击运行可执行文件

## 使用说明

### 首次使用配置
1. **设置监控目录**：选择存放视频文件的目录
2. **选择翻译工具**：选择字幕翻译工具的.bat或.exe文件
3. **设置字幕输出目录**：选择字幕文件的保存位置
4. **选择显卡类型**：根据您的显卡性能选择
5. **保存配置**：点击"保存配置"按钮
6. **开始监控**：点击"开始监控"按钮

### 监控流程
1. 程序会自动检测监控目录中的新视频文件
2. 启动字幕翻译工具处理视频
3. 等待字幕文件生成完成
4. 完成后自动处理原视频文件（根据配置）

## 配置说明

### 删除模式
- **备份模式**：将处理完成的视频移动到备份目录
- **回收站**：将视频文件移动到回收站
- **直接删除**：永久删除视频文件

### 显卡类型
根据您的显卡选择对应类型，影响并发任务数：
- 集成显卡：1个并发任务
- 入门独显：2个并发任务  
- 中端独显：4个并发任务
- 高端独显：6个并发任务
- 专业级显卡：8个并发任务

## 故障排除

### 常见问题

**Q: 程序无法启动**
A: 确保系统满足要求，尝试以管理员身份运行

**Q: 字幕翻译工具无法启动**
A: 检查翻译工具路径是否正确，确保工具可执行

**Q: 监控目录没有反应**
A: 检查监控目录是否存在，文件格式是否支持

**Q: 字幕文件生成失败**
A: 检查翻译工具是否正常工作，查看日志信息

### 日志文件
程序运行日志保存在 `subtitle_monitor.log` 文件中，遇到问题可查看此文件获取详细信息。

## 技术支持

如有问题请联系技术支持或查看程序内置的帮助信息。

## 版本历史

- v1.0 (2025-11-30): 初始发布版本
  - 图形化界面
  - 智能监控功能
  - 配置管理
  - 日志记录

---
*本工具仅供学习交流使用*'''
    
    with open('README_用户手册.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✓ 用户手册创建成功")

def main():
    """主函数"""
    print("=" * 60)
    print("视频字幕翻译监控工具 - 打包程序")
    print("=" * 60)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("请手动安装PyInstaller: pip install pyinstaller")
            return
    
    # 清理构建目录
    cleanup_build_dir()
    
    # 构建可执行文件
    if not build_executable():
        print("构建失败，请检查错误信息")
        return
    
    # 创建安装脚本
    create_installer_script()
    
    # 创建用户手册
    create_readme()
    
    print("\n" + "=" * 60)
    print("打包完成！")
    print("=" * 60)
    print("生成的文件：")
    print("- dist/视频字幕翻译监控工具.exe (主程序)")
    print("- install.bat (安装脚本)")
    print("- README_用户手册.md (使用说明)")
    print("\n使用方法：")
    print("1. 运行 install.bat 进行安装")
    print("2. 或直接使用 dist/视频字幕翻译监控工具.exe")
    print("=" * 60)

if __name__ == "__main__":
    main()