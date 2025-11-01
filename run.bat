@echo off
echo 启动文件删除工具...
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

echo 启动应用程序...
python file_deleter_app.py

pause