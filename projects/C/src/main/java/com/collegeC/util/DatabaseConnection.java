package com.collegeC.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String DEFAULT_URL = "jdbc:mysql://127.0.0.1:3306/CollegeC?useSSL=false&serverTimezone=UTC&characterEncoding=utf8";
    private static final String DEFAULT_USER = "root";
    private static final String DEFAULT_PASSWORD = "123456";

    private static String getProp(String key, String def) {
        String v = System.getProperty(key);
        return (v == null || v.trim().isEmpty()) ? def : v.trim();
    }

    public static Connection getConnection() {
        try {
            Class.forName("com.mysql.cj.jdbc.Driver");
            String url = getProp("collegeC.db.url", DEFAULT_URL);
            String user = getProp("collegeC.db.user", DEFAULT_USER);
            String password = getProp("collegeC.db.password", DEFAULT_PASSWORD);
            return DriverManager.getConnection(url, user, password);
        } catch (ClassNotFoundException | SQLException e) {
            e.printStackTrace();
            return null;
        }
    }
}
