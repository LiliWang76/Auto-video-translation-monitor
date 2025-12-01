@echo off
chcp 65001 >nul
title 视频字幕翻译监控工具 - 完整版

echo ========================================
echo   视频字幕翻译监控工具 v1.0
echo   完整GUI版本
echo ========================================
echo.

echo 正在检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Python未安装或未添加到PATH环境变量
    echo 请先安装Python或使用打包后的可执行文件版本
    pause
    exit /b 1
)

echo ✓ Python环境检测正常

if not exist "video_monitor_gui.py" (
    echo 错误: 找不到主程序文件 video_monitor_gui.py
    pause
    exit /b 1
)

echo 正在启动视频字幕翻译监控工具...
echo.
echo 功能特点:
echo - 图形化界面，简单易用
echo - 自动监控视频文件
echo - 智能调用字幕翻译工具
echo - 实时状态显示和日志记录
echo.
echo 按Ctrl+C可退出程序
echo.

python video_monitor_gui.py

if %errorlevel% neq 0 (
    echo.
    echo 程序异常退出，错误代码: %errorlevel%
    echo 请检查日志文件或重新启动程序
    pause
) else (
    echo.
    echo 程序已正常退出
)

exit /b 0