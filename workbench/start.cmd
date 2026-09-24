@echo off
setlocal
rem Run the existing workbench; never install packages or use the legacy installer.
rem Prefer the Python command already selected on PATH (venv/setup-python/current
rem Windows installs). Keep the Python Launcher as a compatibility fallback.
where python >nul 2>nul
if not errorlevel 1 goto use_python
where py >nul 2>nul
if not errorlevel 1 goto use_py
echo Python 3.11 or newer is required. No packages were installed. 1>&2
exit /b 1
:use_python
if "%~1"=="" goto python_browser
python "%~dp0start.py" %*
exit /b %errorlevel%
:python_browser
python "%~dp0start.py" --open-browser
exit /b %errorlevel%
:use_py
if "%~1"=="" goto py_browser
py -3 "%~dp0start.py" %*
exit /b %errorlevel%
:py_browser
py -3 "%~dp0start.py" --open-browser
exit /b %errorlevel%
