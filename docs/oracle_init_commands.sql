-- ============================================================
-- Oracle XE - 创建 COLLEGEB 用户并初始化（安装完成后执行）
-- 前提：Oracle XE 已安装，SYS 密码为 Oracle123!
-- ============================================================

-- 步骤1：用 sqlplus 手动连接并创建用户
-- sqlplus sys/Oracle123!@XEPDB1 as sysdba

-- 在 sqlplus 中逐条执行以下命令：
ALTER SESSION SET CONTAINER=XEPDB1;
CREATE USER COLLEGEB IDENTIFIED BY CollegeB123;
GRANT CONNECT, RESOURCE, DBA TO COLLEGEB;
GRANT UNLIMITED TABLESPACE TO COLLEGEB;
EXIT;

-- 步骤2：用 COLLEGEB 用户执行初始化脚本
-- sqlplus COLLEGEB/CollegeB123@XEPDB1
-- @E:\SE3-2\dataIntegration\DataIntegration_task3\projects\B\sql\init_B.sql
-- EXIT;
