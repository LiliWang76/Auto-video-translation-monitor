# 配置文件
CONFIG = {
    "DOWNLOAD_DIR": "E:\\115downloads\\等待转字幕",
    "TRANSLATE_BAT": "E:\\BaiduNetdiskDownload\\faster_whisper_transwithai_windows_cu118-chickenrice\\运行(GPU)(输出到当前文件夹).bat",
    "SUBTITLE_DIR": "E:/BaiduNetdiskDownload/faster_whisper_transwithai_windows_cu118-chickenrice/输出",
    "CHECK_INTERVAL": 10,
    "VIDEO_EXTENSIONS": [
        ".mp4",
        ".avi",
        ".mkv",
        ".mov",
        ".wmv",
        ".flv",
        ".m4v",
        ".webm"
    ],
    "STATUS_FILE": "processing_status.json",
    "LOG_FILE": "subtitle_monitor.log",
    "DELETE_MODE": "backup",
    "MAX_CONCURRENT_TASKS": 3,
    "GPU_DETECTION": {
        "ENABLED": True,
        "MAX_TASKS_BY_GPU_TYPE": {
            "集成显卡": 1,
            "入门独显": 2,
            "中端独显": 4,
            "高端独显": 6,
            "专业级显卡": 8
        }
    },
    "GPU_TYPE": "入门独显"
}