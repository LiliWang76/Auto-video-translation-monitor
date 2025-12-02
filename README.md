# 视频字幕翻译自动监控工具 - Faster-Whisper-TransWithAI集成版

## 🎯 项目概述

**基于 🔗 [Faster-Whisper-TransWithAI-ChickenRice](https://github.com/TransWithAI/Faster-Whisper-TransWithAI-ChickenRice) 的自动化监控解决方案**

这是一个专为Faster-Whisper-TransWithAI字幕翻译工具设计的自动化监控程序。程序会持续监控指定目录，自动发现新视频文件，调用Faster-Whisper-TransWithAI进行字幕翻译处理，并在字幕生成完成后自动清理原视频文件，实现从下载到字幕生成的全流程自动化。

## ✨ 核心特色

### 🎯 与Faster-Whisper-TransWithAI完美集成
- **专为Faster-Whisper设计**: 完全适配Faster-Whisper-TransWithAI的工作流程
- **自动参数传递**: 智能调用Faster-Whisper的批处理文件进行字幕翻译
- **进度监控**: 实时跟踪Faster-Whisper的处理状态和进度
- **错误处理**: 自动处理Faster-Whisper运行中的异常情况

### 🔧 自动化监控功能
- 🔍 **智能监控**: 持续监控指定目录，自动发现新视频文件
- ⚡ **并行处理**: 支持同时处理多个视频文件，互不干扰
- 📊 **状态管理**: 智能跟踪文件处理状态，避免重复处理
- 🎮 **显卡优化**: 根据显卡性能自动限制并发任务数
- 🛡️ **文件安全**: 支持三种删除方式（回收站/备份目录/直接删除）
- 📋 **详细日志**: 完整的运行日志记录，便于问题排查

## 📋 系统要求

### 🎯 必需组件
- **Python 3.6+**（仅源代码运行需要）
- **Windows操作系统**（支持Linux/macOS但需要调整路径格式）
- **🔗 [Faster-Whisper-TransWithAI-ChickenRice](https://github.com/TransWithAI/Faster-Whisper-TransWithAI-ChickenRice)** 字幕翻译工具

### 💻 硬件要求
- **显卡要求：推荐NVIDIA显卡（CUDA加速）**
  - 最低要求：支持CUDA 6.1+的NVIDIA显卡（GTX 10系列及以上）
  - AMD显卡用户需使用CPU模式（性能较慢）
  - 不支持Intel集成显卡的硬件加速
- **内存**: 8GB以上（根据视频文件大小调整）
- **存储**: 足够的磁盘空间存放视频文件和字幕文件

## 🔗 Faster-Whisper-TransWithAI 集成说明

### 🎯 集成原理
本监控工具是专为 **Faster-Whisper-TransWithAI-ChickenRice** 设计的自动化前端工具，通过以下方式实现完美集成：

1. **自动调用**: 监控工具自动检测新视频文件，并调用Faster-Whisper的批处理文件进行字幕翻译
2. **参数传递**: 智能传递视频文件路径和输出目录参数给Faster-Whisper
3. **进度监控**: 实时监控Faster-Whisper的处理状态和字幕生成进度
4. **错误处理**: 自动处理Faster-Whisper运行中的异常情况

### ⚙️ 配置要求
- **Faster-Whisper路径**: 确保正确配置Faster-Whisper的bat文件路径
- **输出目录一致**: 监控工具的字幕输出目录应与Faster-Whisper设置保持一致
- **文件格式支持**: 确保监控工具支持的文件格式与Faster-Whisper一致

### 🔄 工作流程
1. 监控工具检测到新视频文件
2. 自动调用Faster-Whisper进行字幕翻译
3. 等待Faster-Whisper完成字幕生成
4. 检测字幕文件生成完成
5. 自动清理原视频文件（可选）

### 💡 使用建议
- 确保Faster-Whisper已正确安装和配置
- 建议先在Faster-Whisper中测试单个视频文件处理
- 配置合适的监控间隔，避免过于频繁的文件检测

## 快速开始

### 1. 使用独立可执行文件（推荐，无需安装Python）

程序已打包为独立可执行文件，无需安装Python环境：

**方法一：使用安装脚本（最简单）**
```bash
双击运行 install.bat
然后双击运行 启动监控工具.bat
```

**方法二：直接运行可执行文件**
```bash
双击运行 视频字幕翻译监控工具.exe
```

### 2. 使用源代码运行（需要Python环境）

#### 安装依赖
本项目使用Python标准库，无需额外安装依赖包。

#### 配置设置

编辑 `config.py` 文件，修改以下配置项：

```python
CONFIG = {
    # 网盘下载目录（监控目录）
    "DOWNLOAD_DIR": r"C:\path\to\monitor\directory",
    
    # Faster-Whisper-TransWithAI的bat文件路径
    # 例如："TRANSLATE_BAT": r"C:\Faster-Whisper-TransWithAI-ChickenRice\faster-whisper.bat"
    "TRANSLATE_BAT": r"C:\path\to\Faster-Whisper-TransWithAI\translate_tool.bat",
    
    # 字幕输出目录（应与Faster-Whisper设置一致）
    "SUBTITLE_DIR": r"C:\path\to\subtitle\output",
    
    # 监控间隔（秒）
    "CHECK_INTERVAL": 10,
    
    # 支持的视频文件扩展名（应与Faster-Whisper支持格式一致）
    "VIDEO_EXTENSIONS": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".m4v", ".webm"],
    
    # 处理状态文件路径
    "STATUS_FILE": "processing_status.json",
    
    # 日志文件路径
    "LOG_FILE": "subtitle_monitor.log"
}
```

#### 启动程序

**方式一：使用批处理文件启动（推荐）**
```bash
双击运行 run_gui_full.bat （GUI版本）
或双击运行 start_monitor.bat （命令行版本）
```

**方式二：使用Python命令启动**
```bash
python video_monitor_gui.py （GUI版本）
或 python main.py （命令行版本）
```

**方式三：使用命令行参数**
```bash
# 单次检查模式
python main.py --once

# 自定义检查间隔
python main.py --interval 30

# 守护进程模式
python main.py --daemon
```

## 文件结构

```
视频自动翻译监控解决方案—1764439751573/
├── 核心程序文件
│   ├── main.py                 # 命令行主程序入口
│   ├── video_monitor_gui.py    # GUI主程序入口
│   ├── file_monitor.py         # 文件监控核心逻辑
│   ├── status_manager.py       # 状态管理模块
│   ├── config.py              # 配置文件管理
│   ├── config_wizard.py        # 配置向导模块
│   └── build.py               # 打包构建脚本
├── 打包相关文件
│   ├── install.bat            # 自动安装脚本
│   ├── run_gui_full.bat       # GUI版本启动脚本
│   ├── run_gui.bat            # GUI测试脚本
│   ├── start_monitor.bat      # 命令行版本启动脚本
│   └── 视频字幕翻译监控工具.spec  # PyInstaller打包配置
├── 用户文档
│   ├── README.md              # 主项目说明文档
│   ├── README_用户手册.md        # 详细用户手册
│   └── README_综合说明.md        # 技术综合说明
├── 构建输出目录
│   ├── build/                 # PyInstaller构建临时文件
│   └── dist/                  # 打包生成的可执行文件
└── 运行生成文件（自动生成）
    ├── processing_status.json # 处理状态记录文件
    └── subtitle_monitor.log   # 运行日志文件
```

## 工作原理

### 监控流程
1. **检测视频文件**: 每10秒扫描监控目录，发现新视频文件
2. **状态检查**: 检查文件是否正在处理或已处理过
3. **启动翻译**: 调用字幕翻译工具在新窗口中处理视频
4. **等待字幕**: 持续检查字幕文件是否生成完成
5. **清理文件**: 字幕生成后将原视频移动到备份目录
6. **状态更新**: 标记文件为已处理完成

### 并行处理
程序支持同时处理多个视频文件：
- 每个视频文件在独立的新窗口中处理
- 状态管理器跟踪每个文件的处理进度
- 避免重复启动同一个文件的翻译

### 文件安全
- 原视频文件不会被直接删除，而是移动到"已处理视频备份"目录
- 备份文件名包含时间戳，避免文件名冲突
- 支持文件锁定冲突重试机制

## 历史修改记录

### 版本历史

#### 2025-12-01 打包系统完善
- **完整打包支持**: 实现从源代码到独立可执行文件的完整打包流程
- **自动安装脚本**: 创建install.bat自动化安装脚本，简化部署过程
- **用户手册生成**: 自动生成详细的用户使用手册，包含完整的操作指南
- **配置管理优化**: 改进配置文件的打包策略，确保运行时配置可用性
- **README文档更新**: 完善README文档，明确说明打包功能和使用方法

#### 2025-11-30 主要优化
- **字幕检测优化**: 将检测间隔从30秒改为10秒，与监控间隔保持一致
- **文件稳定性检查**: 优化字幕文件检测逻辑，避免检测到正在写入的文件
- **文件大小阈值**: 将有效字幕文件大小从0字节改为100字节，避免空文件
- **等待时间优化**: 缩短文件稳定性检查的等待时间

#### 2025-11-30 并行处理优化
- **并行处理机制**: 实现真正的并行处理，支持同时处理多个视频文件
- **状态管理改进**: 完善状态跟踪，避免重复处理同一文件
- **窗口创建优化**: 使用subprocess.Popen + CREATE_NEW_CONSOLE确保每个翻译在新窗口中运行

#### 2025-11-30 文件安全改进
- **安全删除机制**: 将直接删除改为移动到备份目录
- **文件名冲突处理**: 添加时间戳确保备份文件名唯一
- **重试机制**: 文件移动失败时自动重试

#### 2025-11-30 初始版本
- **基础监控功能**: 实现基本的文件监控和翻译工具调用
- **串行处理**: 支持单个视频文件的顺序处理
- **日志记录**: 基本的运行日志记录

## 故障排除

### 常见问题

**Q: 程序启动后没有反应？**
A: 检查config.py中的路径配置是否正确，确保翻译工具路径存在

**Q: 字幕翻译工具没有在新窗口中启动？**
A: 确保翻译工具支持命令行参数，且程序有足够的权限创建新窗口

**Q: 字幕文件生成了但程序没有检测到？**
A: 检查字幕输出目录配置，确保程序有读取权限

**Q: 如何处理多个视频文件？**
A: 程序会自动并行处理，但需要确保翻译工具支持并发运行

**Q: 如何查看运行日志？**
A: 查看subtitle_monitor.log文件获取详细运行信息

**Q: 打包后的程序无法启动？**
A: 确保系统为64位Windows，尝试以管理员身份运行

**Q: 打包时出现依赖错误？**
A: 运行`pip install pyinstaller`安装最新版本PyInstaller

**Q: 打包后的程序文件过大？**
A: 这是正常现象，单文件打包包含了Python解释器和所有依赖库

**Q: 打包后的程序无法启动？**
A: 确保系统为64位Windows，尝试以管理员身份运行

**Q: 打包时出现依赖错误？**
A: 运行`pip install pyinstaller`安装最新版本PyInstaller

**Q: 打包后的程序文件过大？**
A: 这是正常现象，单文件打包包含了Python解释器和所有依赖库

### 日志分析

程序会生成详细的日志文件，包含：
- 文件检测和启动信息
- 翻译工具执行状态
- 字幕生成进度
- 错误和警告信息

## 打包说明

### 🎯 打包功能概述

本项目已完全支持打包为独立可执行文件，具备以下特点：
- ✅ **无需Python环境**: 用户无需安装Python即可运行程序
- ✅ **一键安装**: 提供自动安装脚本，简化部署过程
- ✅ **双版本支持**: 同时支持GUI界面和命令行版本
- ✅ **完整配置**: 包含所有必要的配置文件和依赖项

### 📦 打包为独立可执行文件

#### 打包方法（开发者使用）
```bash
# 1. 确保已安装PyInstaller
pip install pyinstaller

# 2. 运行打包脚本
python build.py

# 3. 生成的exe文件位于dist目录
# 4. 运行install.bat进行安装部署
```

#### 打包配置详情
- **打包工具**: PyInstaller (最新版本)
- **打包模式**: 单文件模式（--onefile），便于分发
- **窗口模式**: 隐藏控制台窗口（--windowed），提供更好的用户体验
- **包含文件**: config.py配置文件、状态文件、日志文件等
- **优化选项**: 启用UPX压缩，减小文件体积

#### 打包生成的文件结构
```
dist/                              # 打包输出目录
├── 视频字幕翻译监控工具.exe         # 主程序（可执行文件）
└── 其他依赖文件...                 # 自动包含的配置文件

项目根目录/                         # 打包后生成的文件
├── install.bat                   # 自动安装脚本
├── 启动监控工具.bat               # 快捷启动脚本
└── README_用户手册.md             # 详细使用说明
```

### 🚀 打包功能的历史演进

#### 2025-12-01 打包系统完善
- **完整打包支持**: 实现从源代码到独立可执行文件的完整打包流程
- **自动安装脚本**: 创建install.bat自动化安装脚本
- **用户手册生成**: 自动生成详细的用户使用手册
- **配置管理优化**: 改进配置文件的打包策略，确保运行时可用

#### 2025-11-30 初始打包功能
- **基础打包**: 实现基本的PyInstaller打包配置
- **GUI版本支持**: 支持GUI界面的独立打包
- **依赖管理**: 自动处理Python依赖项的打包

### 开发说明

#### 扩展功能

项目采用模块化设计，易于扩展：
- `file_monitor.py`: 核心监控逻辑
- `status_manager.py`: 状态管理
- `config.py`: 配置管理
- `build.py`: 打包构建脚本
- `config_wizard.py`: 配置向导模块

#### 自定义翻译工具

如需集成其他翻译工具，修改`execute_translation`方法中的命令调用逻辑。

## 📜 许可证与声明

### 许可证
本项目仅供学习和研究使用。

### 依赖声明
本监控工具是专为 **🔗 [Faster-Whisper-TransWithAI-ChickenRice](https://github.com/TransWithAI/Faster-Whisper-TransWithAI-ChickenRice)** 设计的自动化前端工具，需要依赖该字幕翻译工具进行实际的字幕生成工作。

### 使用说明
- 本工具仅提供自动监控和任务调度功能
- 实际的字幕翻译功能由Faster-Whisper-TransWithAI提供
- 用户需自行确保已正确安装和配置Faster-Whisper-TransWithAI

## 技术支持

如有问题或建议，请查看日志文件或联系开发者。
