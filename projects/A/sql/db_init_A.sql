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
(N'C_A001', N'Data Structures', N'4', N'Prof. Zhang', N'Bldg A101', N'Y'),
(N'C_A002', N'Discrete Math', N'3', N'Prof. Wang', N'Bldg A102', N'Y'),
(N'C_A003', N'Database Principles', N'4', N'Prof. Li', N'Bldg A103', N'Y'),
(N'C_A004', N'Operating Systems', N'3', N'Prof. Zhao', N'Bldg A104', N'N'),
(N'C_A005', N'Compiler Design', N'4', N'Prof. Chen', N'Bldg A105', N'N'),
(N'C_A006', N'Software Engineering', N'3', N'Prof. Liu', N'Bldg A106', N'Y'),
(N'C_A007', N'Computer Networks', N'4', N'Prof. Qian', N'Bldg A107', N'N'),
(N'C_A008', N'Algorithm Design', N'3', N'Prof. Sun', N'Bldg A108', N'Y'),
(N'C_A009', N'Artificial Intelligence', N'4', N'Prof. Zhou', N'Bldg A109', N'Y'),
(N'C_A010', N'Assembly Language', N'3', N'Prof. Wu', N'Bldg A110', N'N');

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
