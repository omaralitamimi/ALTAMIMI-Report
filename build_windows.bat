@echo off
setlocal
if not exist .venv (
  py -3.14 -m venv .venv 2>nul || py -3.13 -m venv .venv 2>nul || py -3.12 -m venv .venv 2>nul || py -3.11 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --windowed --name "ALTAMIMI-Report" app.py
echo.
echo Build complete: dist\ALTAMIMI-Report\ALTAMIMI-Report.exe
pause
