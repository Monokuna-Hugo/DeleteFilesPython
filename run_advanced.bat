@echo off
echo 启动高级文件清理工具...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.6或更高版本
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import wx" >nul 2>&1
if errorlevel 1 (
    echo 警告: wxPython未安装，正在尝试安装...
    pip install wxPython
    if errorlevel 1 (
        echo 错误: wxPython安装失败，请手动安装: pip install wxPython
        pause
        exit /b 1
    )
    echo wxPython安装成功！
)

python -c "import send2trash" >nul 2>&1
if errorlevel 1 (
    echo 警告: send2trash未安装，正在尝试安装...
    pip install send2trash
    if errorlevel 1 (
        echo 错误: send2trash安装失败，请手动安装: pip install send2trash
        pause
        exit /b 1
    )
    echo send2trash安装成功！
)

echo 启动高级文件清理工具...
python advanced_file_cleaner.py

pause