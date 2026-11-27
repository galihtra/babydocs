@echo off
setlocal EnableDelayedExpansion
rem Launcher babydocs untuk Windows.
rem Mencari Python 3.8+; jika belum ada, memasangnya otomatis via winget.

set "HOME_DIR=%~dp0.."
set "PY_CMD="

call :find_python
if not defined PY_CMD (
  echo Kebutuhan sistem ^(Python^) belum terpasang. Memasang otomatis...
  where winget >nul 2>nul
  if !errorlevel! equ 0 (
    winget install -e --id Python.Python.3.12 --scope user --accept-source-agreements --accept-package-agreements
    rem Muat ulang PATH user dari registry
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "PATH=%%B;%PATH%"
    call :find_python
  )
)

if not defined PY_CMD (
  echo Pemasangan otomatis belum berhasil.
  echo Silakan klik dua kali file install.bat di folder babydocs, lalu coba lagi.
  exit /b 1
)

%PY_CMD% "%HOME_DIR%\scripts\cli.py" %*
exit /b %errorlevel%

:find_python
where py >nul 2>nul && (
  py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>nul && (
    set "PY_CMD=py -3"
    exit /b 0
  )
)
where python >nul 2>nul && (
  python -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>nul && (
    set "PY_CMD=python"
    exit /b 0
  )
)
for %%P in ("%LocalAppData%\Programs\Python\Python312\python.exe" "%LocalAppData%\Programs\Python\Python311\python.exe" "%LocalAppData%\Programs\Python\Python310\python.exe") do (
  if exist %%P (
    set "PY_CMD=%%P"
    exit /b 0
  )
)
exit /b 1
