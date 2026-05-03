-- ============================================================
-- 学院B (Oracle) 数据库初始化脚本
-- 包含：建表、50名学生、10门课程、250条选课记录、10个账户
-- 说明：建议使用 UTF-8 / AL32UTF8 字符集的库，避免中文乱码
-- ============================================================

-- 1) 清理旧表（不存在则忽略）
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE CourseChoiceB';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE CourseB';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE StudentB';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
  EXECUTE IMMEDIATE 'DROP TABLE AccountB';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

-- 2) 建表
CREATE TABLE AccountB (
  ACC    VARCHAR2(12) PRIMARY KEY,
  PASSWD VARCHAR2(12) NOT NULL,
  LVL    NUMBER(2)    DEFAULT 0,
  SID    VARCHAR2(9)
);

CREATE TABLE StudentB (
  SID    VARCHAR2(9)  PRIMARY KEY,
  SNAME  VARCHAR2(10) NOT NULL,
  SEX    VARCHAR2(2)  NOT NULL,
  MAJOR  VARCHAR2(16) NOT NULL,
  PASSWD VARCHAR2(6)  NOT NULL
);

CREATE TABLE CourseB (
  CID      VARCHAR2(5)  PRIMARY KEY,
  CNAME    VARCHAR2(16) NOT NULL,
  HOURS    VARCHAR2(2)  NOT NULL,
  CREDIT   VARCHAR2(1)  NOT NULL,
  TEACHER  VARCHAR2(10) NOT NULL,
  LOCATION VARCHAR2(20) NOT NULL,
  SHARE    CHAR(1)      DEFAULT 'N'
);

CREATE TABLE CourseChoiceB (
  CID   VARCHAR2(5) NOT NULL,
  SID   VARCHAR2(9) NOT NULL,
  SCORE VARCHAR2(3) DEFAULT '0',
  CONSTRAINT PK_CourseChoiceB PRIMARY KEY (CID, SID),
  CONSTRAINT FK_CC_B_COURSE FOREIGN KEY (CID) REFERENCES CourseB(CID),
  CONSTRAINT FK_CC_B_STU    FOREIGN KEY (SID) REFERENCES StudentB(SID)
);


-- 3) 插入10门课程 (B101 ~ B110)
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B101', '高等数学', '64', '4', '张老师', '教B-101', 'Y');
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B102', '线性代数', '48', '3', '王老师', '教B-102', 'Y');
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B103', '大学物理', '64', '4', '李老师', '教B-103', 'N');
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B104', '程序设计', '48', '3', '赵老师', '教B-104', 'Y');
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B105', '数据结构', '48', '3', '陈老师', '教B-105', 'Y');
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B106', '数据库',   '48', '3', '刘老师', '教B-106', 'N');
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B107', '操作系统', '64', '4', '钱老师', '教B-107', 'Y');
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B108', '计算机网络', '48', '3', '孙老师', '教B-108', 'N');
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B109', '软件工程', '48', '3', '周老师', '教B-109', 'Y');
INSERT INTO CourseB (CID, CNAME, HOURS, CREDIT, TEACHER, LOCATION, SHARE) VALUES ('B110', '人工智能', '48', '3', '吴老师', '教B-110', 'Y');


-- 4) 插入50名学生 (B001 ~ B050)
DECLARE
  i NUMBER := 1;
  sid VARCHAR2(9);
  nm  VARCHAR2(10);
  sx  VARCHAR2(2);
  mj  VARCHAR2(16);
  pw  VARCHAR2(6);
BEGIN
  WHILE i <= 50 LOOP
    sid := 'B' || LPAD(i, 3, '0');
    nm  := '学生B_' || TO_CHAR(i);
    sx  := CASE WHEN MOD(i, 2) = 0 THEN '女' ELSE '男' END;
    mj  := CASE WHEN MOD(i, 3) = 0 THEN '计算机' WHEN MOD(i, 3) = 1 THEN '软工' ELSE '网安' END;
    pw  := LOWER(sid) || '00';
    INSERT INTO StudentB (SID, SNAME, SEX, MAJOR, PASSWD)
    VALUES (sid, nm, sx, mj, pw);
    i := i + 1;
  END LOOP;
END;
/


-- 5) 为每名学生选5门课 (50人 × 5 = 250条)
DECLARE
  i NUMBER := 1;
  sid VARCHAR2(9);
  k NUMBER;
  cid VARCHAR2(5);
  base NUMBER;
BEGIN
  WHILE i <= 50 LOOP
    sid := 'B' || LPAD(i, 3, '0');
    -- 让每个学生从不同起点循环选5门
    base := MOD(i-1, 10) + 101;
    k := 0;
    WHILE k < 5 LOOP
      cid := 'B' || TO_CHAR(base + k);
      IF base + k > 110 THEN
        cid := 'B' || TO_CHAR(101 + (base + k - 111));
      END IF;
      INSERT INTO CourseChoiceB (CID, SID, SCORE) VALUES (cid, sid, '0');
      k := k + 1;
    END LOOP;
    i := i + 1;
  END LOOP;
END;
/


-- 6) 插入10个账户 (1个管理员 + 9个学生)
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('admin', 'admin123', 1, NULL);
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('B001', 'b00100', 0, 'B001');
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('B002', 'b00200', 0, 'B002');
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('B003', 'b00300', 0, 'B003');
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('B004', 'b00400', 0, 'B004');
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('B005', 'b00500', 0, 'B005');
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('B006', 'b00600', 0, 'B006');
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('B007', 'b00700', 0, 'B007');
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('B008', 'b00800', 0, 'B008');
INSERT INTO AccountB (ACC, PASSWD, LVL, SID) VALUES ('B009', 'b00900', 0, 'B009');

COMMIT;
