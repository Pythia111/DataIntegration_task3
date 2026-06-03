package com.collegeB.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

import com.collegeB.entity.CourseChoice;
import com.collegeB.util.DatabaseConnection;

public class ChoiceDAO {

    public boolean enroll(String sid, String cid) {
        if (hasEnrolled(sid, cid)) {
            return false;
        }
        String sql = "INSERT INTO CourseChoiceB (CID, SID, SCORE) VALUES (?, ?, '0')";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cid);
            ps.setString(2, sid);
            return ps.executeUpdate() > 0;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean drop(String sid, String cid) {
        String sql = "DELETE FROM CourseChoiceB WHERE CID = ? AND SID = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cid);
            ps.setString(2, sid);
            return ps.executeUpdate() > 0;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public List<CourseChoice> getStudentSchedule(String sid) {
        List<CourseChoice> list = new ArrayList<>();
        String sql = "SELECT * FROM CourseChoiceB WHERE SID = ? ORDER BY CID";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, sid);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    list.add(new CourseChoice(
                            rs.getString("SID"),
                            rs.getString("CID"),
                            rs.getString("SCORE")));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public boolean hasEnrolled(String sid, String cid) {
        String sql = "SELECT COUNT(*) FROM CourseChoiceB WHERE CID = ? AND SID = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cid);
            ps.setString(2, sid);
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
