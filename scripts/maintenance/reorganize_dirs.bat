@echo off
cd /d "%~dp0..\.."
python scripts\maintenance\reorganize_dirs.py
