# ============================================================
# 演示恢复脚本 — 清除测试痕迹，恢复到可演示的初始状态
# 用法: powershell -ExecutionPolicy Bypass -File .\scripts\reset-for-demo.ps1
# ============================================================
param(
  [switch]$FullReinit,    # 完全重建所有数据库（慢，约2分钟）
  [switch]$NoStart         # 只清理数据，不启动服务
)

$ErrorActionPreference = "Stop"
$root = "E:\SE3-2\dataIntegration\DataIntegration_task3"
$mvn = "E:\SE2\software-programming2\apache-maven-3.9.9\apache-maven-3.9.9\bin\mvn.cmd"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  演示环境恢复脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Reset-CollegeA {
    Write-Host "[A] 清理 SQL Server 测试数据..." -ForegroundColor Yellow
    $sqlcmd = "C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\180\Tools\Binn\SQLCMD.EXE"
    & $sqlcmd -S ".\SQLEXPRESS" -E -C -Q "DELETE FROM CollegeA.dbo.CourseChoiceA WHERE 学生编号='A2026001' AND 课程编号='B101'" 2>&1 | Out-Null
    & $sqlcmd -S ".\SQLEXPRESS" -E -C -Q "DELETE FROM CollegeA.dbo.CourseChoiceA WHERE 学生编号='A2026001' AND 课程编号 LIKE 'B%'" 2>&1 | Out-Null
    & $sqlcmd -S ".\SQLEXPRESS" -E -C -Q "DELETE FROM CollegeA.dbo.CourseChoiceA WHERE 学生编号='A2026001' AND 课程编号 LIKE 'C%'" 2>&1 | Out-Null
    Write-Host "  College A 测试数据已清除" -ForegroundColor Green
}

function Reset-CollegeB {
    Write-Host "[B] 清理 Oracle 测试数据..." -ForegroundColor Yellow
    $env:ORACLE_HOME = "$root\dbhomeXE"
    $env:ORACLE_SID = "XE"
    $sql = @"
ALTER SESSION SET CURRENT_SCHEMA = C##COLLEGEB;
DELETE FROM CourseChoiceB WHERE SID='A2026001';
COMMIT;
EXIT;
"@
    $sql | Set-Content "$root\database\reset_B.sql" -Encoding ASCII
    & "$env:ORACLE_HOME\bin\sqlplus.exe" -S "sys/Oracle123! as sysdba" "@$root\database\reset_B.sql" 2>&1 | Out-Null
    Write-Host "  College B 测试数据已清除" -ForegroundColor Green
}

function Reset-CollegeC {
    Write-Host "[C] 清理 MySQL 测试数据..." -ForegroundColor Yellow
    $mysql = "D:\mysql\mysql-9.2.0-winx64\bin\mysql.exe"
    "USE CollegeC; DELETE FROM CourseChoiceC WHERE Sno='A2026001';" | & $mysql -u root -p123456 2>&1 | Out-Null
    Write-Host "  College C 测试数据已清除" -ForegroundColor Green
}

function Full-Reinit {
    Write-Host "`n=== 完全重建所有数据库 ===" -ForegroundColor Magenta
    
    Write-Host "[A] 重建 SQL Server CollegeA..." -ForegroundColor Yellow
    $sqlcmd = "C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\180\Tools\Binn\SQLCMD.EXE"
    & $sqlcmd -S ".\SQLEXPRESS" -E -C -Q "DROP DATABASE IF EXISTS CollegeA" 2>&1 | Out-Null
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    $content = Get-Content "$root\projects\A\sql\db_init_A.sql" -Raw -Encoding UTF8
    $content = $content -replace "COLLATE Chinese_PRC_CI_AS", ""
    [System.IO.File]::WriteAllText("$root\database\init_A.sql", $content, $utf8NoBom)
    & $sqlcmd -S ".\SQLEXPRESS" -E -C -f 65001 -i "$root\database\init_A.sql" 2>&1 | Out-Null
    Write-Host "  College A 重建完成 (50S/10C/250CC)" -ForegroundColor Green
    
    Write-Host "[B] 重建 Oracle CollegeB..." -ForegroundColor Yellow
    $env:ORACLE_HOME = "$root\dbhomeXE"
    $env:ORACLE_SID = "XE"
    & "$env:ORACLE_HOME\bin\sqlplus.exe" -S "sys/Oracle123! as sysdba" "@$root\database\cdb_setup.sql" 2>&1 | Out-Null
    & "$env:ORACLE_HOME\bin\sqlplus.exe" -S "sys/Oracle123! as sysdba" "@$root\database\insert_cdb.sql" 2>&1 | Out-Null
    # 补插入 B107/B109 及选课记录
    $fixSql = @"
ALTER SESSION SET CURRENT_SCHEMA = C##COLLEGEB;
ALTER TABLE CourseB MODIFY CNAME VARCHAR2(30);
ALTER TABLE CourseB MODIFY TEACHER VARCHAR2(20);
INSERT INTO CourseB VALUES ('B107', 'Operating Systems', '64', '4', 'Qian', 'BldgB-107', 'Y');
INSERT INTO CourseB VALUES ('B109', 'Software Engineering', '48', '3', 'Zhou', 'BldgB-109', 'Y');
COMMIT;
EXIT;
"@
    $fixSql | Set-Content "$root\database\fixB.sql" -Encoding ASCII
    & "$env:ORACLE_HOME\bin\sqlplus.exe" -S "sys/Oracle123! as sysdba" "@$root\database\fixB.sql" 2>&1 | Out-Null
    Write-Host "  College B 重建完成 (50S/10C/250CC)" -ForegroundColor Green
    
    Write-Host "[C] 重建 MySQL CollegeC..." -ForegroundColor Yellow
    $mysql = "D:\mysql\mysql-9.2.0-winx64\bin\mysql.exe"
    "DROP DATABASE IF EXISTS CollegeC;" | & $mysql -u root -p123456 2>&1 | Out-Null
    Get-Content "$root\projects\C\sql\init.sql" -Encoding UTF8 | & $mysql -u root -p123456 --default-character-set=utf8mb4 2>&1 | Out-Null
    Write-Host "  College C 重建完成 (50S/10C/250CC)" -ForegroundColor Green
    
    # 重新应用英文课程名修复
    & $sqlcmd -S ".\SQLEXPRESS" -E -C -Q "UPDATE CollegeA.dbo.CourseA SET 课程名称='Data Structures', 授课老师='Prof. Zhang', 授课地点='Bldg A101' WHERE 课程编号='C_A001'" 2>&1 | Out-Null
    foreach ($row in @(
        @("C_A002","Discrete Math","Prof. Wang","Bldg A102"),
        @("C_A003","Database Principles","Prof. Li","Bldg A103"),
        @("C_A004","Operating Systems","Prof. Zhao","Bldg A104"),
        @("C_A005","Compiler Design","Prof. Chen","Bldg A105"),
        @("C_A006","Software Engineering","Prof. Liu","Bldg A106"),
        @("C_A007","Computer Networks","Prof. Qian","Bldg A107"),
        @("C_A008","Algorithm Design","Prof. Sun","Bldg A108"),
        @("C_A009","Artificial Intelligence","Prof. Zhou","Bldg A109"),
        @("C_A010","Assembly Language","Prof. Wu","Bldg A110")
    )) {
        & $sqlcmd -S ".\SQLEXPRESS" -E -C -Q "UPDATE CollegeA.dbo.CourseA SET 课程名称='$($row[1])', 授课老师='$($row[2])', 授课地点='$($row[3])' WHERE 课程编号='$($row[0])'" 2>&1 | Out-Null
    }
    & $sqlcmd -S ".\SQLEXPRESS" -E -C -Q "UPDATE CollegeA.dbo.StudentA SET 姓名=CONCAT('StudentA_', RIGHT(学号,3))" 2>&1 | Out-Null
    
    # MySQL 课程英文名
    $mysqlFix = @"
USE CollegeC;
UPDATE CourseC SET Cnm='Database Principles', Tec='Prof. Zhou', Pla='Bldg C301' WHERE Cno='C101';
UPDATE CourseC SET Cnm='Operating Systems', Tec='Prof. Wu', Pla='Bldg C302' WHERE Cno='C102';
UPDATE CourseC SET Cnm='Compiler Design', Tec='Prof. Zheng', Pla='Bldg C303' WHERE Cno='C103';
UPDATE CourseC SET Cnm='Software Testing', Tec='Prof. Wang', Pla='Bldg C304' WHERE Cno='C104';
UPDATE CourseC SET Cnm='AI Fundamentals', Tec='Prof. Feng', Pla='Bldg C305' WHERE Cno='C105';
UPDATE CourseC SET Cnm='Info Security', Tec='Prof. Chen', Pla='Bldg C306' WHERE Cno='C106';
UPDATE CourseC SET Cnm='Mobile App Dev', Tec='Prof. Han', Pla='Bldg C307' WHERE Cno='C107';
UPDATE CourseC SET Cnm='Cloud Computing', Tec='Prof. Yang', Pla='Bldg C308' WHERE Cno='C108';
UPDATE CourseC SET Cnm='Internet of Things', Tec='Prof. Zhu', Pla='Bldg C309' WHERE Cno='C109';
UPDATE CourseC SET Cnm='Big Data Analytics', Tec='Prof. Qin', Pla='Bldg C310' WHERE Cno='C110';
UPDATE StudentC SET Snm=CONCAT('StudentC_', SUBSTRING(Sno,2,3));
"@
    $mysqlFix | & $mysql -u root -p123456 --default-character-set=utf8mb4 2>&1 | Out-Null
    Write-Host "  英文名修复完成" -ForegroundColor Green
}

# === 主流程 ===
Write-Host "正在停止所有 Java 进程..." -ForegroundColor Yellow
Get-Process java -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

if ($FullReinit) {
    Full-Reinit
} else {
    Write-Host "快速模式：仅清除测试选课记录" -ForegroundColor Yellow
    Reset-CollegeA
    Reset-CollegeB
    Reset-CollegeC
}

Write-Host "`n=== 数据清理完成 ===" -ForegroundColor Green
Write-Host "  College A (SQL Server): 50S/10C/250CC" -ForegroundColor Gray
Write-Host "  College B (Oracle):     50S/10C/250CC" -ForegroundColor Gray
Write-Host "  College C (MySQL):      50S/10C/250CC" -ForegroundColor Gray

if (-not $NoStart) {
    Write-Host "`n正在构建项目..." -ForegroundColor Yellow
    Set-Location $root
    & $mvn -DskipTests clean package 2>&1 | Select-Object -Last 3
    
    Write-Host "正在启动所有服务..." -ForegroundColor Yellow
    "integration","A","B","C" | ForEach-Object {
        $dir = "$root\projects\$_"
        Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoExit", "-Command", "Set-Location '$dir'; & '$mvn' exec:java") -WorkingDirectory $dir
        Write-Host "  [$_] 已启动" -ForegroundColor Green
    }
    
    Start-Sleep -Seconds 20
    Write-Host "`n=== 服务已启动，可以开始演示 ===" -ForegroundColor Cyan
    Write-Host "一键测试: powershell -ExecutionPolicy Bypass -File .\scripts\demo-test.ps1" -ForegroundColor White
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  恢复完成，环境就绪！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
