@echo off
REM Daily News Digest 启动脚本
REM 设置 UTF-8 编码以支持 emoji 输出
set PYTHONIOENCODING=utf-8

REM 切换到项目目录
cd /d "%~dp0.."

REM 运行主程序
"C:\Users\aWW\scoop\apps\python-embed\python.exe" main.py
