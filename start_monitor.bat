@echo off
chcp 65001 >nul
echo 启动视频字幕翻译自动监控程序
echo ========================================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查是否安装了必要的库
python -c "import subprocess, os, time, logging, json" >nul 2>&1
if errorlevel 1 (
    echo 错误: 缺少必要的Python库
    echo 请运行: pip install subprocess os time logging json
    pause
    exit /b 1
)

echo 正在启动监控程序...
echo 按 Ctrl+C 停止监控
python main.py

pause