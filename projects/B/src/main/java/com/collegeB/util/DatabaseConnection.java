package com.collegeB.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    // 你可以根据本机Oracle实例修改为：
    // - XE:  jdbc:oracle:thin:@127.0.0.1:1521/XEPDB1
    // - 19c: jdbc:oracle:thin:@127.0.0.1:1521/ORCLPDB1
    private static final String DEFAULT_URL = "jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521))(CONNECT_DATA=(SID=XE)))";
    private static final String DEFAULT_USER = "C##COLLEGEB";
    private static final String DEFAULT_PASSWORD = "CollegeB123";

    private static String getProp(String key, String def) {
        String v = System.getProperty(key);
        return (v == null || v.trim().isEmpty()) ? def : v.trim();
    }

    public static Connection getConnection() {
        try {
            Class.forName("oracle.jdbc.OracleDriver");
            String url = getProp("collegeB.db.url", DEFAULT_URL);
            String user = getProp("collegeB.db.user", DEFAULT_USER);
            String password = getProp("collegeB.db.password", DEFAULT_PASSWORD);
            return DriverManager.getConnection(url, user, password);
        } catch (ClassNotFoundException | SQLException e) {
            e.printStackTrace();
            return null;
        }
    }
}
