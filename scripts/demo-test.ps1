# 助教演示 - API 集成测试脚本
# 前提：集成服务器运行在 localhost:8080，学院 A/B/C 运行在 8081/8082/8083

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  助教演示 - 集成接口测试" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 共享课程
Write-Host "1. 共享课程 (GET /api/integration/sharedCourses?source=A):" -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest "http://localhost:8080/api/integration/sharedCourses?source=A" -UseBasicParsing -TimeoutSec 10
    Write-Host "   [OK] Status: $($r.StatusCode)" -ForegroundColor Green
    Write-Host "   Response: $($r.Content)" -ForegroundColor Gray
} catch {
    Write-Host "   [FAIL] $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 2. 跨院选课 ENROLL
Write-Host "2. 跨院选课 ENROLL (POST /api/integration/courseChoice?source=A):" -ForegroundColor Yellow
$enrollXml = [xml]@"
<choiceReq>
  <traceId>demo-enroll-001</traceId>
  <source>A</source>
  <sid>A2026001</sid>
  <cid>B101</cid>
  <operation>ENROLL</operation>
</choiceReq>
"@
try {
    $r = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/integration/courseChoice?source=A" `
         -ContentType "application/xml" -Body ($enrollXml.OuterXml) -TimeoutSec 15
    Write-Host "   [OK]" -ForegroundColor Green
    Write-Host "   Response:" -ForegroundColor Gray
    Write-Host $r.OuterXml -ForegroundColor Gray
} catch {
    Write-Host "   [FAIL] $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 3. 跨院退选 DROP
Write-Host "3. 跨院退选 DROP (POST /api/integration/courseChoice?source=A):" -ForegroundColor Yellow
$dropXml = [xml]@"
<choiceReq>
  <traceId>demo-drop-001</traceId>
  <source>A</source>
  <sid>A2026001</sid>
  <cid>B101</cid>
  <operation>DROP</operation>
</choiceReq>
"@
try {
    $r = Invoke-RestMethod -Method Post -Uri "http://localhost:8080/api/integration/courseChoice?source=A" `
         -ContentType "application/xml" -Body ($dropXml.OuterXml) -TimeoutSec 15
    Write-Host "   [OK]" -ForegroundColor Green
    Write-Host "   Response:" -ForegroundColor Gray
    Write-Host $r.OuterXml -ForegroundColor Gray
} catch {
    Write-Host "   [FAIL] $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# 4. 全局统计
Write-Host "4. 全局统计 (GET /api/integration/statistics):" -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest "http://localhost:8080/api/integration/statistics" -UseBasicParsing -TimeoutSec 30
    Write-Host "   [OK] Status: $($r.StatusCode)" -ForegroundColor Green
    Write-Host "   Response:" -ForegroundColor Gray
    Write-Host $r.Content -ForegroundColor Gray
} catch {
    Write-Host "   [FAIL] $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  演示测试完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
