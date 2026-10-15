@echo off
chcp 65001 >nul
title FongMi 字典更新工具
cd /d "%~dp0"

set "PY=python"
if exist "%~dp0..\venv\Scripts\python.exe" set "PY=%~dp0..\venv\Scripts\python.exe"

echo ============================================================
echo   FongMi 配置字典 一键更新
echo   抓取 - 校验 - 重新生成 config/ 与 docs/线路清单.md
echo   只生成文件，不启动任何常驻服务
echo ============================================================
echo.

"%PY%" "%~dp0update.py"

echo.
echo 更新完成，生成的文件在仓库 config/ 目录。
pause
