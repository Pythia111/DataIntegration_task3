-- 上传到助教统一 MySQL (hw4) 的数据脚本（路线1）
-- 目标表：hw4.student / hw4.course / hw4.sc
-- 注意：该脚本生成 A/B/C 三个院系的数据，各 50 学生、10 课程、250 选课。
-- 使用前请修改 @GROUP_NO 为你们的小组号（数字或字符串，以助教要求为准）。

SET @GROUP_NO := '16';

-- 为避免重复插入：先删除本组数据（按 group_no 匹配）
DELETE FROM sc     WHERE group_no = @GROUP_NO;
DELETE FROM course WHERE group_no = @GROUP_NO;
DELETE FROM student WHERE group_no = @GROUP_NO;

-- 生成序列 1..50 / 1..10
WITH RECURSIVE seq50(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq50 WHERE n < 50
),
seq10(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq10 WHERE n < 10
)
-- A 学生
INSERT INTO student(student_id, student_name, gender, department, account, password, group_no, dept_no)
SELECT
  CONCAT('A', LPAD(n, 3, '0')) AS student_id,
  CONCAT('学生A', LPAD(n, 3, '0')) AS student_name,
  IF(n % 2 = 0, 'F', 'M') AS gender,
  '学院A' AS department,
  CONCAT('A', LPAD(n, 3, '0')) AS account,
  CONCAT('a', LPAD(n, 3, '0'), '00') AS password,
  @GROUP_NO AS group_no,
  'A' AS dept_no
FROM seq50;

WITH RECURSIVE seq10(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq10 WHERE n < 10
)
-- A 课程
INSERT INTO course(course_id, course_name, credit, teacher_name, location, share_flag, class_hours, practice_hours, group_no, dept_no)
SELECT
  CONCAT('A', 100 + n) AS course_id,
  CONCAT('A课程', LPAD(n, 2, '0')) AS course_name,
  '3' AS credit,
  CONCAT('A教师', n) AS teacher_name,
  CONCAT('A教室-', n) AS location,
  IF(n % 3 = 0, 'N', 'Y') AS share_flag,
  '48' AS class_hours,
  '0'  AS practice_hours,
  @GROUP_NO AS group_no,
  'A' AS dept_no
FROM seq10;

WITH RECURSIVE seq50(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq50 WHERE n < 50
),
seq5(k) AS (
  SELECT 0
  UNION ALL
  SELECT k + 1 FROM seq5 WHERE k < 4
)
-- A 选课（每生 5 门课，循环分配 10 门课）
INSERT INTO sc(course_id, student_id, score, group_no, dept_no)
SELECT
  CONCAT('A', 101 + ((n - 1 + k) % 10)) AS course_id,
  CONCAT('A', LPAD(n, 3, '0')) AS student_id,
  NULL AS score,
  @GROUP_NO AS group_no,
  'A' AS dept_no
FROM seq50 CROSS JOIN seq5;

-- B 学生/课程/选课
WITH RECURSIVE seq50(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq50 WHERE n < 50
)
INSERT INTO student(student_id, student_name, gender, department, account, password, group_no, dept_no)
SELECT
  CONCAT('B', LPAD(n, 3, '0')),
  CONCAT('学生B', LPAD(n, 3, '0')),
  IF(n % 2 = 0, 'F', 'M'),
  '学院B',
  CONCAT('B', LPAD(n, 3, '0')),
  CONCAT('b', LPAD(n, 3, '0'), '00'),
  @GROUP_NO,
  'B'
FROM seq50;

WITH RECURSIVE seq10(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq10 WHERE n < 10
)
INSERT INTO course(course_id, course_name, credit, teacher_name, location, share_flag, class_hours, practice_hours, group_no, dept_no)
SELECT
  CONCAT('B', 100 + n),
  CONCAT('B课程', LPAD(n, 2, '0')),
  '3',
  CONCAT('B教师', n),
  CONCAT('B教室-', n),
  IF(n % 3 = 0, 'N', 'Y'),
  '48',
  '0',
  @GROUP_NO,
  'B'
FROM seq10;

WITH RECURSIVE seq50(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq50 WHERE n < 50
),
seq5(k) AS (
  SELECT 0
  UNION ALL
  SELECT k + 1 FROM seq5 WHERE k < 4
)
INSERT INTO sc(course_id, student_id, score, group_no, dept_no)
SELECT
  CONCAT('B', 101 + ((n - 1 + k) % 10)),
  CONCAT('B', LPAD(n, 3, '0')),
  NULL,
  @GROUP_NO,
  'B'
FROM seq50 CROSS JOIN seq5;

-- C 学生/课程/选课
WITH RECURSIVE seq50(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq50 WHERE n < 50
)
INSERT INTO student(student_id, student_name, gender, department, account, password, group_no, dept_no)
SELECT
  CONCAT('C', LPAD(n, 3, '0')),
  CONCAT('学生C', LPAD(n, 3, '0')),
  IF(n % 2 = 0, 'F', 'M'),
  '学院C',
  CONCAT('C', LPAD(n, 3, '0')),
  CONCAT('c', LPAD(n, 3, '0'), '00'),
  @GROUP_NO,
  'C'
FROM seq50;

WITH RECURSIVE seq10(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq10 WHERE n < 10
)
INSERT INTO course(course_id, course_name, credit, teacher_name, location, share_flag, class_hours, practice_hours, group_no, dept_no)
SELECT
  CONCAT('C', 100 + n),
  CONCAT('C课程', LPAD(n, 2, '0')),
  '3',
  CONCAT('C教师', n),
  CONCAT('C教室-', n),
  IF(n % 3 = 0, 'N', 'Y'),
  '48',
  '0',
  @GROUP_NO,
  'C'
FROM seq10;

WITH RECURSIVE seq50(n) AS (
  SELECT 1
  UNION ALL
  SELECT n + 1 FROM seq50 WHERE n < 50
),
seq5(k) AS (
  SELECT 0
  UNION ALL
  SELECT k + 1 FROM seq5 WHERE k < 4
)
INSERT INTO sc(course_id, student_id, score, group_no, dept_no)
SELECT
  CONCAT('C', 101 + ((n - 1 + k) % 10)),
  CONCAT('C', LPAD(n, 3, '0')),
  NULL,
  @GROUP_NO,
  'C'
FROM seq50 CROSS JOIN seq5;
