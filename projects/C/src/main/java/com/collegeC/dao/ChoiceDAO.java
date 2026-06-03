package com.collegeC.dao;

import com.collegeC.entity.CourseChoice;
import com.collegeC.util.DatabaseConnection;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

public class ChoiceDAO {

    public boolean enroll(String sno, String cno) {
        String sql = "INSERT INTO CourseChoiceC (Cno, Sno, Grd) VALUES (?, ?, 0)";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cno);
            ps.setString(2, sno);
            return ps.executeUpdate() > 0;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean drop(String sno, String cno) {
        String sql = "DELETE FROM CourseChoiceC WHERE Cno = ? AND Sno = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cno);
            ps.setString(2, sno);
            return ps.executeUpdate() > 0;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public List<CourseChoice> getStudentSchedule(String sno) {
        List<CourseChoice> list = new ArrayList<>();
        String sql = "SELECT * FROM CourseChoiceC WHERE Sno = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, sno);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    list.add(new CourseChoice(
                            rs.getString("Sno"),
                            rs.getString("Cno"),
                            rs.getString("Grd")));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public boolean hasEnrolled(String sno, String cno) {
        String sql = "SELECT COUNT(*) FROM CourseChoiceC WHERE Cno = ? AND Sno = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cno);
            ps.setString(2, sno);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt(1) > 0;
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return false;
    }
}
