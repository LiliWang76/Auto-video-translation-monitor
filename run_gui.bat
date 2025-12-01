@echo off
chcp 65001 >nul
echo ========================================
echo   视频字幕翻译监控工具 - GUI原型测试
echo ========================================
echo.
echo 正在启动GUI界面...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查PySimpleGUI是否安装
python -c "import PySimpleGUI" >nul 2>&1
if errorlevel 1 (
    echo 正在安装PySimpleGUI库...
    echo 注意: PySimpleGUI已迁移到私有服务器，安装可能需要额外时间
    
    :: 尝试标准安装
    pip install PySimpleGUI
    if errorlevel 1 (
        echo 标准安装失败，尝试从私有服务器安装...
        pip install --extra-index-url https://PySimpleGUI.net/install PySimpleGUI
        if errorlevel 1 (
            echo 错误: PySimpleGUI安装失败
            echo 请手动安装: pip install --extra-index-url https://PySimpleGUI.net/install PySimpleGUI
            pause
            exit /b 1
        )
    )
)

:: 启动GUI程序
echo 启动GUI界面...
python gui_prototype.py

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
)

@echo on