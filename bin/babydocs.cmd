@echo off
rem babydocs untuk Windows (cmd / PowerShell)
where py >nul 2>nul && (py -3 "%~dp0babydocs" %*) || (python "%~dp0babydocs" %*)
