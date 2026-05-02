# 学院C系统开发说明

成员4 | 数据库：MySQL 8.0.41 | 端口：8083

## 一、系统概述

学院C教务系统基于 MySQL + Java Swing + DOM4J 实现，具备本地选课/退课、跨院选课/退课、课程共享管理、全局统计查看等功能，通过 HTTP + XML 与集成服务器通信。

## 二、项目结构

```
member4/
├── pom.xml                          # Maven配置（mysql-connector-java 8.0.28 + dom4j 2.1.3）
├── sql/
│   └── init.sql                     # 建库建表 + 全部初始数据
└── src/main/java/com/collegeC/
    ├── Main.java                    # 入口：启动本地HTTP服务器 + 登录窗口
    ├── entity/
    │   ├── Course.java              # 课程实体（Cno/Cnm/Ctm/Cpt/Tec/Pla/Share）
    │   ├── CourseChoice.java        # 选课实体（Sno/Cno/Grd）
    │   └── Student.java             # 学生实体（Sno/Snm/Sex/Sde/Pwd）
    ├── dao/
    │   ├── CourseDAO.java           # 课程查询 + 共享标记修改
    │   ├── ChoiceDAO.java           # 选课/退选/课表查询/重复检查
    │   └── StudentDAO.java          # 登录验证 + 学号查询
    ├── gui/
    │   ├── LoginFrame.java          # 登录窗口（学生/管理员）
    │   ├── StudentFrame.java        # 学生端（本校课程/跨院共享课程/我的课表）
    │   └── AdminFrame.java          # 管理员端（课程管理/全局统计）
    ├── net/
    │   ├── IntegrationClient.java   # HTTP客户端，向集成服务器(8080)发请求
    │   └── LocalHttpServer.java     # 本地HTTP服务(8083)，4个接口
    ├── util/
    │   ├── DatabaseConnection.java  # MySQL数据库连接
    │   └── XMLHandler.java          # XML通用工具
    └── xml/
        └── XMLBuilder.java          # 学院C格式XML生成与解析
```

## 三、数据库设计

数据库名：CollegeC，共4张表，字段名采用英文简写（与数据设计文档一致）。

### 3.1 账户表 AccountC

| 字段       | 类型        | 约束        | 说明   |
| ---------- | ----------- | ----------- | ------ |
| acc        | varchar(12) | primary key | 账户名 |
| passwd     | varchar(12) | not null    | 密码   |
| CreateDate | timestamp   | default now | 创建时间 |

- 共10条记录，1个管理员(admin/admin123)，9个学生账户(C001~C009，密码与学号对应)

### 3.2 学生表 StudentC

| 字段 | 类型        | 约束        | 说明   |
| ---- | ----------- | ----------- | ------ |
| Sno  | varchar(9)  | primary key | 学号   |
| Snm  | varchar(10) | not null    | 姓名   |
| Sex  | varchar(1)  | not null    | 性别   |
| Sde  | varchar(6)  | not null    | 院系   |
| Pwd  | char(6)     | not null    | 密码   |

- 共50名学生，学号 C001~C050，分布在计科/软工/网安三个专业

### 3.3 课程表 CourseC

| 字段  | 类型        | 约束        | 说明     |
| ----- | ----------- | ----------- | -------- |
| Cno   | char(4)     | primary key | 课程编号 |
| Cnm   | varchar(10) | not null    | 课程名称 |
| Ctm   | int         | not null    | 课时     |
| Cpt   | int         | not null    | 学分     |
| Tec   | varchar(20) | not null    | 授课教师 |
| Pla   | varchar(18) | not null    | 授课地点 |
| Share | char(1)     | default 'N' | 是否共享 |

- 共10门课程(C101~C110)，其中7门默认共享(Share=Y)

### 3.4 选课表 CourseChoiceC

| 字段 | 类型    | 约束                      | 说明 |
| ---- | ------- | ------------------------- | ---- |
| Cno  | char(4) | primary key, foreign key  | 课程编号 |
| Sno  | char(9) | primary key, foreign key  | 学号   |
| Grd  | int     | default 0                 | 成绩   |

- 共250条记录，每名学生选5门课

## 四、本地HTTP服务接口（端口8083）

供集成服务器调用，所有接口返回 `application/xml; charset=UTF-8`。

### 4.1 获取本院共享课程

- **路径**：`GET /api/local/sharedCourses`
- **说明**：返回学院C所有 Share='Y' 的课程，XML格式为学院C本地格式
- **响应示例**：
```xml
<Classes>
  <class>
    <Cno>C101</Cno>
    <Cnm>数据库原理</Cnm>
    <Ctm>64</Ctm>
    <Cpt>4</Cpt>
    <Tec>周教授</Tec>
    <Pla>教学楼C301</Pla>
    <Share>Y</Share>
  </class>
  ...
</Classes>
```

### 4.2 处理跨院选课请求

- **路径**：`POST /api/local/enroll`
- **请求体**：XML（包含 sid、cid 字段）
- **说明**：为外院学生在本院数据库中添加选课记录
- **响应示例**：
```xml
<response>
  <status>SUCCESS</status>
  <message>选课成功</message>
</response>
```

### 4.3 处理跨院退选课请求

- **路径**：`POST /api/local/drop`
- **请求体**：XML（包含 sid、cid 字段）
- **说明**：删除外院学生在本院的选课记录
- **响应示例**：
```xml
<response>
  <status>SUCCESS</status>
  <message>退选成功</message>
</response>
```

### 4.4 获取本院统计信息

- **路径**：`GET /api/local/statistics`
- **说明**：返回学院C的学生数、课程数、选课数
- **响应示例**：
```xml
<statistics>
  <college name="C">
    <students>50</students>
    <courses>10</courses>
    <choices>250</choices>
  </college>
</statistics>
```

## 五、与集成服务器的交互

学院C作为客户端向集成服务器(localhost:8080)发起以下请求：

| 功能         | 方法 | 路径                                       | 参数/请求体                          |
| ------------ | ---- | ------------------------------------------ | ------------------------------------ |
| 获取跨院共享课程 | GET  | `/api/integration/sharedCourses?source=C`  | 无                                   |
| 跨院选课/退课   | POST | `/api/integration/courseChoice?source=C`   | XML请求体（含source/sid/cid/operation） |
| 全局统计       | GET  | `/api/integration/statistics`              | 无                                   |

### 选课/退课请求XML格式

```xml
<choiceReq>
  <traceId>随机UUID</traceId>
  <source>C</source>
  <sid>C001</sid>
  <cid>A101</cid>
  <operation>ENROLL</operation>  <!-- ENROLL 或 DROP -->
</choiceReq>
```

## 六、XML格式说明

### 6.1 学院C本地课程XML元素映射

| 统一格式元素 | 学院C元素 | 数据库字段 |
 | ------------ | --------- | ---------- |
| id           | Cno       | Cno        |
| name         | Cnm       | Cnm        |
| time         | Ctm       | Ctm        |
| score        | Cpt       | Cpt        |
| teacher      | Tec       | Tec        |
| location     | Pla       | Pla        |

### 6.2 学院C本地学生XML元素映射

| 统一格式元素 | 学院C元素 | 数据库字段 |
 | ------------ | --------- | ---------- |
| id           | Sno       | Sno        |
| name         | Snm       | Snm        |
| sex          | Sex       | Sex        |
| major        | Sde       | Sde        |

### 6.3 学院C本地选课XML元素映射

| 统一格式元素 | 学院C元素 | 数据库字段 |
 | ------------ | --------- | ---------- |
| sid          | Sno       | Sno        |
| cid          | Cno       | Cno        |
| score        | Grd       | Grd        |

### 6.4 XML解析兼容性

XMLBuilder.parseSharedCoursesXML() 同时兼容学院C本地格式(Cno/Cnm/...)和统一格式(id/name/...)，在集成服务器XSLT转换未就绪时也能直接解析。

## 七、GUI功能说明

### 7.1 登录窗口

- 输入账户名和密码，验证AccountC表
- 账户名为"admin"进入管理员端，否则进入学生端

### 7.2 学生端（三个标签页）

| 标签页       | 功能                                                         |
| ------------ | ------------------------------------------------------------ |
| 本校课程     | 展示CourseC全部课程，支持选本校课程                          |
| 跨院共享课程 | 从集成服务器获取其他学院共享课程，支持跨院选课               |
| 我的课表     | 展示个人选课记录，支持退选（本院直接退，跨院通过集成服务器退） |

### 7.3 管理员端（两个标签页）

| 标签页       | 功能                                         |
| ------------ | -------------------------------------------- |
| 本地课程管理 | 展示全部课程，支持设置/取消课程共享标记     |
| 全局统计     | 从集成服务器获取三院统计数据（XML格式展示） |

## 八、数据库连接配置

文件：`src/main/java/com/collegeC/util/DatabaseConnection.java`

| 配置项   | 值                                                              |
| -------- | --------------------------------------------------------------- |
| URL      | jdbc:mysql://127.0.0.1:3306/CollegeC?useSSL=false&serverTimezone=UTC&characterEncoding=utf8 |
| 用户名   | root                                                            |
| 密码     | 123456                                                          |

## 九、运行方式

```bash
# 1. 初始化数据库（仅首次需要）
mysql -u root -p123456 < sql/init.sql

# 2. 编译
cd member4
mvn compile

# 3. 运行
mvn exec:java
```

启动后：
- 本地HTTP服务监听 **8083** 端口
- GUI登录窗口自动弹出
- 需集成服务器(8080)已启动才能使用跨院选课和全局统计功能
