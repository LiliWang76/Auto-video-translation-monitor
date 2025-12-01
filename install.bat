@echo off
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
if exist "dist\视频字幕翻译监控工具.exe" (
    copy "dist\视频字幕翻译监控工具.exe" .
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
