@echo off


start "" "C:\xampp\apache\bin\httpd.exe"
start "" "C:\xampp\mysql\bin\mysqld.exe"
timeout /t 10 /nobreak > nul

echo Navigating to Django Project...
cd /d "C:\Users\HP\Desktop\Nolans_projects\django\Lender"



echo Starting Django Server...
powershell -NoExit -Command "Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned; & 'c:\Users\HP\Desktop\Nolans_projects\django\.venv\Scripts\Activate.ps1'; cd 'C:\Users\HP\Desktop\Nolans_projects\django\Lender'; python manage.py runserver"
