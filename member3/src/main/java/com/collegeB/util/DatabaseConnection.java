package com.collegeB.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    // 你可以根据本机Oracle实例修改为：
    // - XE:  jdbc:oracle:thin:@127.0.0.1:1521/XEPDB1
    // - 19c: jdbc:oracle:thin:@127.0.0.1:1521/ORCLPDB1
    private static final String URL = "jdbc:oracle:thin:@127.0.0.1:1521/XEPDB1";
    private static final String USER = "COLLEGEB";
    private static final String PASSWORD = "CollegeB123";

    public static Connection getConnection() {
        try {
            Class.forName("oracle.jdbc.OracleDriver");
            return DriverManager.getConnection(URL, USER, PASSWORD);
        } catch (ClassNotFoundException | SQLException e) {
            e.printStackTrace();
            return null;
        }
    }
}
