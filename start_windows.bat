@echo off
title Facebook Video Downloader
where python >nul 2>nul || (echo Chua co Python. Cai Python 3.11+ truoc.& pause & exit /b)
where ffmpeg >nul 2>nul || echo CANH BAO: Chua co FFmpeg - video chat luong cao co the khong ghep duoc.
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
start http://127.0.0.1:8000
uvicorn app:app --host 127.0.0.1 --port 8000
pause
