Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL17.SQLEXPRESS\MSSQLServer" -Name "LoginMode" -Value 2 -Force
net stop "MSSQL$SQLEXPRESS" /y
net start "MSSQL$SQLEXPRESS"
$sqlcmd = "C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\180\Tools\Binn\SQLCMD.EXE"
Start-Sleep -Seconds 8
"ALTER LOGIN sa WITH PASSWORD='YourStrongPassword123'; ALTER LOGIN sa ENABLE;" | & $sqlcmd -S ".\SQLEXPRESS" -E -C
"SELECT 'sa_OK' AS result" | & $sqlcmd -S ".\SQLEXPRESS" -U sa -P "YourStrongPassword123" -C
Read-Host "Press Enter to close"
