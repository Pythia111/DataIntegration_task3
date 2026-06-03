# DataIntegration_task3（路线1）

本仓库实现“基于 XML/XSD/XSLT 的异构教务数据集成”，包含 3 个学院端系统（A/B/C）与 1 个集成服务器（Integration）。

## 目录结构

- docs/：所有文档、报告、说明与 schema 设计材料
- projects/：所有可构建/可运行的 Maven 模块
  - projects/A：学院 A（SQL Server）
  - projects/B：学院 B（Oracle）
  - projects/C：学院 C（MySQL）
  - projects/integration：集成服务器（对外统一入口，端口默认 8080）
  - projects/ext：扩展/联调模块（可构建；非必需运行入口）
- scripts/：一键构建/一键启动脚本（Windows PowerShell）
- pom.xml：根聚合 pom（一次性构建全部模块）

## 快速上手（Windows / PowerShell）

### 1) 一键构建

在仓库根目录执行：

- `mvn -DskipTests clean package`

或使用脚本：

- `powershell -ExecutionPolicy Bypass -File .\scripts\build-all.ps1`

### 2) 启动（推荐顺序）

- 一键启动（会打开 4 个 PowerShell 窗口）：
  - `powershell -ExecutionPolicy Bypass -File .\scripts\start-all.ps1`

或手动逐个启动：

1. 集成服务器（8080）
   - `cd projects/integration`
   - `mvn exec:java -Dexec.args=8080`
2. 学院 A（8081，GUI）
   - `cd projects/A`
   - `mvn exec:java`
3. 学院 B（8082，GUI）
   - `cd projects/B`
   - `mvn exec:java`
4. 学院 C（8083，GUI）
   - `cd projects/C`
   - `mvn exec:java`

## 常用接口（助教检查）

- 课程共享：`GET /api/integration/sharedCourses?source={A|B|C}`
- 跨院选课/退选：`POST /api/integration/courseChoice?source={A|B|C}`（choiceReq XML，operation=ENROLL|DROP）
- 全局统计：`GET /api/integration/statistics`

## 更多文档

- 整合交付说明：[docs/交付说明.md](docs/交付说明.md)
- 可交付性清单（对照作业要求逐条核对）：[docs/可交付性清单.md](docs/可交付性清单.md)
- 作业要求原文：[docs/路线1作业要求.md](docs/路线1作业要求.md)
- 上传到助教 MySQL（hw4）说明：[docs/hw4/README.md](docs/hw4/README.md)
- 助教演示流程（启动 + 接口演示）：[docs/助教演示流程.md](docs/助教演示流程.md)

