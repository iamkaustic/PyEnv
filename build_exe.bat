@echo off
echo Building Python Environment Manager executable...
pyinstaller --clean --onefile --windowed --icon=icon.ico --name="Python Environment Manager" pyenv_manager.py
echo Build process completed.
pause
