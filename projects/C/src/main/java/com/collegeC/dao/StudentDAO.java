package com.collegeC.dao;

import com.collegeC.entity.Student;
import com.collegeC.util.DatabaseConnection;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

public class StudentDAO {

    public Student getStudentBySno(String sno) {
        String sql = "SELECT * FROM StudentC WHERE Sno = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, sno);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return new Student(
                            rs.getString("Sno"),
                            rs.getString("Snm"),
                            rs.getString("Sex"),
                            rs.getString("Sde"),
                            rs.getString("Pwd"));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public String getStudentSnoByAccount(String acc) {
        String sql = "SELECT Sno FROM StudentC WHERE Sno = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, acc);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return rs.getString("Sno");
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "UNKNOWN";
    }

    public String login(String acc, String passwd) {
        String sql = "SELECT acc FROM AccountC WHERE acc = ? AND passwd = ?";
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
        return "admin".equals(acc);
    }
}
