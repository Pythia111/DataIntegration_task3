# 上传到助教 MySQL（hw4）说明

你附件里的文档要求的是“统一 MySQL（hw4）三张表：student/course/sc，并补充 group_no + dept_no”。

当前项目的本地数据库是 A(SQL Server)/B(Oracle)/C(MySQL) 三套异构库，用于作业3功能运行；它们的表结构不等同于 hw4 的统一表结构。

因此，要满足该硬性要求，需要额外执行一次“上传到 hw4”的插入脚本。

## 1) 连接信息（来自助教文档）

- Host：10.60.254.44
- Port：3306
- DB：hw4
- User：root
- Pass：123456

## 2) 使用步骤

1. 用 MySQL 客户端执行脚本（任选一种）：

- MySQL Workbench：选择 `hw4` schema，直接运行整个脚本
- 命令行：
  - `mysql -h 10.60.254.44 -P 3306 -u root -p hw4 < upload_hw4.sql`

脚本会：
- 先按 `group_no` 删除本组旧数据
- 再插入 A/B/C 三个院系的数据（各 50 学生、10 课程、250 选课）

说明：本仓库已将 `group_no` 固定为 `16`。

## 3) 你需要确认的点（助教硬性检查常见项）

- 三张表都有插入记录（student/course/sc）
- `group_no` 填写正确
- `dept_no` 为 A/B/C
- 数据量满足：
  - 每院：50 学生、10 课程、250 选课

