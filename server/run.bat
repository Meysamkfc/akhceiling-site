@echo off
cd /d %~dp0
if not exist .venv ( python -m venv .venv & .venv\Scripts\python -m pip install -r requirements.txt )
set PORT=8790
.venv\Scripts\python -m waitress --listen=127.0.0.1:%PORT% app:app
