package com.collegeC.dao;

import com.collegeC.entity.Course;
import com.collegeC.util.DatabaseConnection;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

public class CourseDAO {

    public List<Course> getAllLocalCourses() {
        List<Course> list = new ArrayList<>();
        String sql = "SELECT * FROM CourseC";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                list.add(new Course(
                        rs.getString("Cno"),
                        rs.getString("Cnm"),
                        rs.getString("Ctm"),
                        rs.getString("Cpt"),
                        rs.getString("Tec"),
                        rs.getString("Pla"),
                        rs.getString("Share")));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public List<Course> getSharedCourses() {
        List<Course> list = new ArrayList<>();
        String sql = "SELECT * FROM CourseC WHERE Share = 'Y'";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                list.add(new Course(
                        rs.getString("Cno"),
                        rs.getString("Cnm"),
                        rs.getString("Ctm"),
                        rs.getString("Cpt"),
                        rs.getString("Tec"),
                        rs.getString("Pla"),
                        rs.getString("Share")));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public boolean updateShareFlag(String cno, String flag) {
        String sql = "UPDATE CourseC SET Share = ? WHERE Cno = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, flag);
            ps.setString(2, cno);
            return ps.executeUpdate() > 0;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public Course getCourseById(String cno) {
        String sql = "SELECT * FROM CourseC WHERE Cno = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, cno);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return new Course(
                            rs.getString("Cno"),
                            rs.getString("Cnm"),
                            rs.getString("Ctm"),
                            rs.getString("Cpt"),
                            rs.getString("Tec"),
                            rs.getString("Pla"),
                            rs.getString("Share"));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
}
