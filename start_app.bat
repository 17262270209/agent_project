@echo off
echo ====================================
echo 智能问答系统 - Streamlit 可视化界面
echo ====================================
echo.

echo [1/3] 检查依赖...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 Python，请先安装 Python 3.11+
    pause
    exit /b 1
)

echo [2/3] 安装依赖包...
pip install -r requirements_streamlit.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo [3/3] 启动应用...
echo.
echo 应用将在浏览器中打开: http://localhost:8501
echo 按 Ctrl+C 停止应用
echo.

streamlit run app.py

pause