@echo off
"%~dp0runtime\python.exe" -B "%~dp0install.py" uninstall
set "KRATOS_RESULT=%ERRORLEVEL%"
echo Press any key to close this window . . .
pause >nul
exit /b %KRATOS_RESULT%
