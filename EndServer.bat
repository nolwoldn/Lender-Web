@echo off
title Lender Dev Stopper

echo Stopping Django Server and closing terminals...
:: Forces termination of Python (Django) and PowerShell windows
taskkill /F /IM python.exe /T
taskkill /F /IM powershell.exe /T

echo Stopping XAMPP Services...
:: Forces termination of Apache and MySQL background instances
taskkill /F /IM httpd.exe /T
taskkill /F /IM mysqld.exe /T

echo Lender development environment successfully stopped.
timeout /t 2 > nul
exit