package com.collegeA.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:sqlserver://127.0.0.1:1433;databaseName=CollegeA;encrypt=false;loginTimeout=5;";
    private static final String USER = "sa"; // 请在使用时替换为实际的SQL Server用户名
    private static final String PASSWORD = "YourStrongPassword123"; // 请在使用时替换为实际的密码

    public static Connection getConnection() {
        try {
            Class.forName("com.microsoft.sqlserver.jdbc.SQLServerDriver");
            return DriverManager.getConnection(URL, USER, PASSWORD);
        } catch (ClassNotFoundException | SQLException e) {
            e.printStackTrace();
            return null;
        }
    }
}