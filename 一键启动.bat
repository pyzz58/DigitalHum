@echo off

rem 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo 虚拟环境不存在，直接运行...
)

rem 安装依赖
echo 安装依赖...
pip install -r requirements.txt

rem 运行应用
echo 启动应用...
streamlit run src/app.py

pause
