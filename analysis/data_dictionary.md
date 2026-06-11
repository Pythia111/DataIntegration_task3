# 数据字典
## 一、数据来源

### 1.1 数据库信息

| 项目 | 内容 |
|------|------|
| 主机 | 10.60.254.44 |
| 端口 | 3306 |
| 数据库名 | hw4 |
| 用户名 | root |
| 密码 | 123456 |
| 字符集 | utf8mb4 |

### 1.2 数据表概览

数据库包含三张核心表，每张表都包含 `group_no`（组号）和 `dept_no`（院系编号）字段，用于区分不同组和不同院系的数据。

| 表名 | 中文名 | 说明 | 主要用途 |
|------|--------|------|----------|
| student | 学生表 | 存储学生基本信息 | 学生管理、性别分布分析 |
| course | 课程表 | 存储课程基本信息 | 课程管理、学分分析、共享课程分析 |
| sc | 选课表 | 存储学生选课及成绩信息 | 选课关系、成绩分析 |

---

## 二、表结构详细说明

### 2.1 学生表 (student)

**表名**：`student`
**说明**：存储各组各院系的学生基本信息

| 字段名 | 数据类型 | 长度 | 约束 | 说明 | 取值示例 |
|--------|----------|------|------|------|----------|
| student_id | VARCHAR | 12 | NOT NULL | 学号（主键），唯一标识学生 | A001, B001, C001 |
| student_name | VARCHAR | 10 | NOT NULL | 学生姓名 | 张三, 李四 |
| gender | VARCHAR | 2 | | 性别 | M（男）/ F（女） |
| department | VARCHAR | 16 | | 院系名称 | 计算机学院, 信息学院 |
| account | VARCHAR | 10 | | 登录账号 | stu001 |
| password | VARCHAR | 6 | | 登录密码 | 123456 |
| group_no | VARCHAR | 10 | NOT NULL | 组号，标识数据所属的组 | 1, 2, ..., 16 |
| dept_no | VARCHAR | 10 | NOT NULL | 院系编号 | A, B, C |

**数据特征**：
- 学号格式通常为：院系前缀 + 流水号（如A001-A050, B001-B050, C001-C050）
- 不同组的学号格式可能不同
- 性别分布预期接近1:1

**完整性约束**：
- 学号（student_id）为主键，不能重复
- 组号（group_no）和院系编号（dept_no）不能为空

---

### 2.2 课程表 (course)

**表名**：`course`
**说明**：存储各组各院系的课程基本信息

| 字段名 | 数据类型 | 长度 | 约束 | 说明 | 取值示例 |
|--------|----------|------|------|------|----------|
| course_id | VARCHAR | 8 | NOT NULL | 课程编号（主键），唯一标识课程 | A101, B101, C101 |
| course_name | VARCHAR | 16 | NOT NULL | 课程名称 | 数据结构, 计算机网络 |
| credit | VARCHAR | 2 | | 学分 | 3, 4, 2 |
| teacher_name | VARCHAR | 20 | | 授课教师姓名 | 王老师, 赵老师 |
| location | VARCHAR | 20 | | 上课地点 | 教1-101, 教2-202 |
| share_flag | CHAR | 1 | | 共享课程标志 | Y（是）/ N（否） |
| class_hours | VARCHAR | 10 | | 理论课时 | 48, 64 |
| practice_hours | VARCHAR | 10 | | 实验课时 | 16, 32 |
| group_no | VARCHAR | 10 | NOT NULL | 组号，标识数据所属的组 | 1, 2, ..., 16 |
| dept_no | VARCHAR | 10 | NOT NULL | 院系编号 | A, B, C |

**数据特征**：
- 课程编号格式通常为：院系前缀 + 课程流水号（如A101-A110）
- 学分通常为2-4学分
- 共享课程：share_flag='Y'表示该课程为跨院系共享课程
- 不同组的课程设计可能不同（学分、课时、共享比例等）

**完整性约束**：
- 课程编号（course_id）为主键，不能重复
- 组号（group_no）和院系编号（dept_no）不能为空

---

### 2.3 选课表 (sc)

**表名**：`sc`
**说明**：存储学生选课关系及成绩信息

| 字段名 | 数据类型 | 长度 | 约束 | 说明 | 取值示例 |
|--------|----------|------|------|------|----------|
| course_id | VARCHAR | 8 | NOT NULL | 课程编号（外键，关联course表） | A101, B101 |
| student_id | VARCHAR | 12 | NOT NULL | 学号（外键，关联student表） | A001, B001 |
| score | VARCHAR | 3 | | 成绩（0-100，可为NULL） | 85, 90, NULL |
| group_no | VARCHAR | 10 | NOT NULL | 组号，标识数据所属的组 | 1, 2, ..., 16 |
| dept_no | VARCHAR | 10 | NOT NULL | 院系编号 | A, B, C |

**数据特征**：
- 复合主键：(student_id, course_id)，同一学生不能重复选同一门课
- 成绩可能为NULL（表示未录入或未参加考试）
- 不同组的选课记录数量可能差异较大

**完整性约束**：
- student_id 必须存在于 student 表中
- course_id 必须存在于 course 表中
- (student_id, course_id) 组合唯一
- 组号（group_no）和院系编号（dept_no）不能为空

---

## 三、公共字段说明

### 3.1 group_no（组号）

- **类型**：VARCHAR(10)
- **说明**：标识数据所属的作业三小组编号
- **取值范围**：1-30（根据实际参与组数而定）
- **用途**：用于区分不同组的数据，进行组间对比分析

### 3.2 dept_no（院系编号）

- **类型**：VARCHAR(10)
- **说明**：标识数据所属的虚拟院系
- **取值范围**：A, B, C（分别代表学院A、学院B、学院C）
- **用途**：用于区分同一组内不同院系的数据，分析院系特征

---

## 四、数据关系

### 4.1 实体关系图（ER图）

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   student   │         │     sc      │         │   course    │
├─────────────┤         ├─────────────┤         ├─────────────┤
│ student_id* │◄────────┤ student_id* │         │ course_id*  │
│ student_name│         │ course_id*  │────────►│ course_name │
│ gender      │         │ score       │         │ credit      │
│ department  │         │ group_no    │         │ teacher_name│
│ account     │         │ dept_no     │         │ location    │
│ password    │         └─────────────┘         │ share_flag  │
│ group_no    │                                 │ class_hours │
│ dept_no     │                                 │ practice_hrs│
└─────────────┘                                 │ group_no    │
                                                │ dept_no     │
                                                └─────────────┘
```

### 4.2 表间关系说明

1. **student ← sc**：一个学生可以选修多门课程（1:N）
2. **course ← sc**：一门课程可以被多个学生选修（1:N）
3. **student ↔ course**：通过 sc 表实现多对多关系（M:N）

### 4.3 参照完整性

- sc.student_id 必须在 student.student_id 中存在
- sc.course_id 必须在 course.course_id 中存在
- 违反参照完整性的记录需要在数据清洗阶段标记或删除

---

## 五、数据质量说明

### 5.1 可能存在的数据质量问题

1. **缺失值问题**
   - 学生表：姓名、性别可能缺失
   - 课程表：教师姓名、上课地点可能缺失
   - 选课表：成绩字段普遍为NULL（作业三大部分组未录入成绩）

2. **重复值问题**
   - 学号、课程编号可能存在重复
   - 选课记录可能存在重复（同一学生重复选同一门课）

3. **格式不一致问题**
   - 不同组的学号格式可能不同（长度、前缀、编号规则）
   - 不同组的课程编号格式可能不同
   - 性别字段表示方式可能不统一（M/F, 男/女, Male/Female等）
   - 共享标志可能不统一（Y/N, 1/0, 是/否等）

4. **逻辑异常问题**
   - 选课记录指向不存在的学号或课程编号
   - 学分、课时为负数或异常值
   - 成绩超出0-100范围

5. **数量异常问题**
   - 某些组的学生数、课程数、选课数与预期差异较大
   - 某些院系数据完全缺失

### 5.2 数据预处理策略

1. **缺失值处理**
   - 关键字段（学号、课程编号、姓名、课程名）缺失：删除记录
   - 非关键字段缺失：保留NULL或填充默认值

2. **重复值处理**
   - 主键重复：标记为异常，保留第一条记录
   - 选课记录重复：去重，保留第一条记录

3. **格式统一**
   - 字符串字段：去除首尾空格、统一大小写
   - 性别字段：统一为 M/F
   - 共享标志：统一为 Y/N
   - 数值字段：转换为数值类型，无效值转为NULL

4. **参照完整性检查**
   - 检查 sc 表中的外键引用
   - 标记或删除引用不存在的记录

---

## 六、数据使用示例

### 6.1 查询本组（16号）学生数据

```sql
SELECT * FROM student WHERE group_no = '16';
```

### 6.2 查询本组学院A的课程数据

```sql
SELECT * FROM course WHERE group_no = '16' AND dept_no = 'A';
```

### 6.3 统计各组学生数量

```sql
SELECT group_no, COUNT(*) as student_count
FROM student
GROUP BY group_no
ORDER BY group_no;
```

### 6.4 查询共享课程

```sql
SELECT * FROM course WHERE share_flag = 'Y';
```

### 6.5 统计学生选课数量

```sql
SELECT student_id, COUNT(*) as course_count
FROM sc
GROUP BY student_id;
```

### 6.6 查询有成绩的选课记录

```sql
SELECT * FROM sc WHERE score IS NOT NULL;
```

---

## 七、注意事项

1. **字符编码**：所有数据文件使用 UTF-8 编码，导出CSV时建议使用 utf-8-sig 以便Excel正常打开中文

2. **数据类型**：数据库中部分数值字段（如credit, score）定义为VARCHAR类型，在Python中需要手动转换为数值类型

3. **NULL值处理**：
   - 数据库中的NULL值在Pandas中会转换为NaN
   - 在数据分析时需要注意NULL/NaN值的处理

4. **组号和院系编号**：
   - 这两个字段在所有表中都存在
   - 是进行数据分组和筛选的关键字段
   - 在数据合并时需要注意匹配这两个字段

5. **数据更新**：
   - 数据为作业三各组上传的历史数据，不会再更新
   - 本次分析使用的是数据快照

---

## 八、数据导出文件说明

### 8.1 原始数据文件

| 文件名 | 说明 | 生成脚本 |
|--------|------|----------|
| data/students.csv | 学生表原始数据 | fetch_data.py |
| data/courses.csv | 课程表原始数据 | fetch_data.py |
| data/sc.csv | 选课表原始数据 | fetch_data.py |

### 8.2 清洗后数据文件

| 文件名 | 说明 | 生成脚本 |
|--------|------|----------|
| data/cleaned/students_cleaned.csv | 学生表清洗后数据 | preprocess.py |
| data/cleaned/courses_cleaned.csv | 课程表清洗后数据 | preprocess.py |
| data/cleaned/sc_cleaned.csv | 选课表清洗后数据 | preprocess.py |

### 8.3 其他文件

| 文件名 | 说明 | 生成脚本 |
|--------|------|----------|
| data/preprocessing_report.md | 数据预处理报告 | preprocess.py |
