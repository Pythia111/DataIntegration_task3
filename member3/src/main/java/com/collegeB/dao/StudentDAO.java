package com.collegeB.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

import com.collegeB.entity.Student;
import com.collegeB.util.DatabaseConnection;

public class StudentDAO {

    public String login(String acc, String passwd) {
        String sql = "SELECT ACC FROM AccountB WHERE ACC = ? AND PASSWD = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, acc);
            ps.setString(2, passwd);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return acc;
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public boolean isAdmin(String acc) {
        String sql = "SELECT NVL(LVL, 0) AS LVL FROM AccountB WHERE ACC = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, acc);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt("LVL") >= 1;
                }
            }
        } catch (Exception e) {
            // 兜底：按账号名判断
            e.printStackTrace();
        }
        return "admin".equalsIgnoreCase(acc);
    }

    public String getStudentSidByAccount(String acc) {
        String sql = "SELECT SID FROM AccountB WHERE ACC = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, acc);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    String sid = rs.getString("SID");
                    if (sid != null && !sid.trim().isEmpty()) {
                        return sid;
                    }
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return acc;
    }

    public Student getStudentBySid(String sid) {
        String sql = "SELECT * FROM StudentB WHERE SID = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, sid);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return new Student(
                            rs.getString("SID"),
                            rs.getString("SNAME"),
                            rs.getString("SEX"),
                            rs.getString("MAJOR"),
                            rs.getString("PASSWD"));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
}
