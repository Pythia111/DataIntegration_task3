package com.collegeA.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String DEFAULT_URL = "jdbc:jtds:sqlserver://localhost:1433/CollegeA;instance=SQLEXPRESS;useNTLMv2=true;";
    private static final String DEFAULT_USER = "sa";
    private static final String DEFAULT_PASSWORD = "YourStrongPassword123";

    private static String getProp(String key, String def) {
        String v = System.getProperty(key);
        return (v == null || v.trim().isEmpty()) ? def : v.trim();
    }

    public static Connection getConnection() {
        try {
            Class.forName("net.sourceforge.jtds.jdbc.Driver");
            String url = getProp("collegeA.db.url", DEFAULT_URL);
            String user = getProp("collegeA.db.user", DEFAULT_USER);
            String password = getProp("collegeA.db.password", DEFAULT_PASSWORD);
            return DriverManager.getConnection(url, user, password);
        } catch (ClassNotFoundException | SQLException e) {
            e.printStackTrace();
            return null;
        }
    }
}