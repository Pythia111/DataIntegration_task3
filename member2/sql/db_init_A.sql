USE master;
GO

IF EXISTS (SELECT name FROM sys.databases WHERE name = N'CollegeA')
BEGIN
    ALTER DATABASE CollegeA SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE CollegeA;
END
GO

CREATE DATABASE CollegeA COLLATE Chinese_PRC_CI_AS;
GO
USE CollegeA;
GO

-- 表 3-2：院系 A 账户表结构
CREATE TABLE AccountA (
    账户名 NVARCHAR(20) PRIMARY KEY,
    密码 NVARCHAR(20),
    权限 NVARCHAR(10) -- 'STU' or 'ADMN'
);

-- 表 3-3：院系 A 学生表结构
CREATE TABLE StudentA (
    学号 NVARCHAR(12) PRIMARY KEY,
    姓名 NVARCHAR(50),
    性别 NVARCHAR(2),
    院系 NVARCHAR(50),
    关联账户 NVARCHAR(20) FOREIGN KEY REFERENCES AccountA(账户名)
);

-- 表 3-4：院系 A 课程表结构
CREATE TABLE CourseA (
    课程编号 NVARCHAR(20) PRIMARY KEY,
    课程名称 NVARCHAR(50),
    学分 NVARCHAR(10),
    授课老师 NVARCHAR(50),
    授课地点 NVARCHAR(50),
    共享 NVARCHAR(2) -- 'Y' or 'N'
);

-- 表 3-5：院系 A 选课表结构
CREATE TABLE CourseChoiceA (
    课程编号 NVARCHAR(20),
    学生编号 NVARCHAR(12),
    成绩 NVARCHAR(10),
    CONSTRAINT PK_CourseChoiceA PRIMARY KEY (课程编号, 学生编号)
);
GO

-- 插入管理员账户
INSERT INTO AccountA (账户名, 密码, 权限) VALUES (N'adminA', N'123456', N'ADMN');

-- 插入50个学生和它们的账户
DECLARE @i INT = 1;
WHILE @i <= 50
BEGIN
    DECLARE @account NVARCHAR(10) = N'stuA' + CAST(@i AS NVARCHAR(10));
    DECLARE @studentId NVARCHAR(12) = N'A2026' + RIGHT(N'000' + CAST(@i AS NVARCHAR(10)), 3);
    
    INSERT INTO AccountA (账户名, 密码, 权限) VALUES (@account, N'123456', N'STU');
    INSERT INTO StudentA (学号, 姓名, 性别, 院系, 关联账户) 
    VALUES (@studentId, N'学生A_' + CAST(@i AS NVARCHAR(10)), CASE WHEN @i % 2 = 0 THEN N'女' ELSE N'男' END, N'学院A', @account);
    
    SET @i = @i + 1;
END

-- 插入10门课程
INSERT INTO CourseA (课程编号, 课程名称, 学分, 授课老师, 授课地点, 共享) VALUES
(N'C_A001', N'数据结构', N'4', N'张老师', N'教A-101', N'Y'),
(N'C_A002', N'离散数学', N'3', N'王老师', N'教A-102', N'Y'),
(N'C_A003', N'数据库', N'4', N'李老师', N'教A-103', N'Y'),
(N'C_A004', N'操作系统', N'3', N'赵老师', N'教A-104', N'N'),
(N'C_A005', N'编译原理', N'4', N'陈老师', N'教A-105', N'N'),
(N'C_A006', N'软件工程', N'3', N'刘老师', N'教A-106', N'Y'),
(N'C_A007', N'计算机网络', N'4', N'钱老师', N'教A-107', N'N'),
(N'C_A008', N'算法设计', N'3', N'孙老师', N'教A-108', N'Y'),
(N'C_A009', N'人工智能', N'4', N'周老师', N'教A-109', N'Y'),
(N'C_A010', N'汇编语言', N'3', N'吴老师', N'教A-110', N'N');

-- 为每个学生插入5条选课记录
DECLARE @s INT = 1;
WHILE @s <= 50
BEGIN
    DECLARE @sid VARCHAR(12) = 'A2026' + RIGHT('000' + CAST(@s AS VARCHAR), 3);
    
    -- 每人固定选前5门课
    INSERT INTO CourseChoiceA (课程编号, 学生编号, 成绩) VALUES ('C_A001', @sid, '90');
    INSERT INTO CourseChoiceA (课程编号, 学生编号, 成绩) VALUES ('C_A002', @sid, '85');
    INSERT INTO CourseChoiceA (课程编号, 学生编号, 成绩) VALUES ('C_A003', @sid, '88');
    INSERT INTO CourseChoiceA (课程编号, 学生编号, 成绩) VALUES ('C_A004', @sid, '92');
    INSERT INTO CourseChoiceA (课程编号, 学生编号, 成绩) VALUES ('C_A005', @sid, '80');
    
    SET @s = @s + 1;
END
GO
