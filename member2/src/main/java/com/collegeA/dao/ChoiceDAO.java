package com.collegeA.dao;

import com.collegeA.entity.CourseChoice;
import com.collegeA.util.DatabaseConnection;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

public class ChoiceDAO {

    public boolean enroll(String studentId, String courseId) {
        String sql = "INSERT INTO CourseChoiceA (课程编号, 学生编号, 成绩) VALUES (?, ?, '')";
        try (Connection conn = DatabaseConnection.getConnection();
                PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, courseId);
            ps.setString(2, studentId);
            return ps.executeUpdate() > 0;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean drop(String studentId, String courseId) {
        String sql = "DELETE FROM CourseChoiceA WHERE 课程编号 = ? AND 学生编号 = ?";
        try (Connection conn = DatabaseConnection.getConnection();
                PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, courseId);
            ps.setString(2, studentId);
            return ps.executeUpdate() > 0;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public List<CourseChoice> getStudentSchedule(String studentId) {
        List<CourseChoice> list = new ArrayList<>();
        String sql = "SELECT * FROM CourseChoiceA WHERE 学生编号 = ?";
        try (Connection conn = DatabaseConnection.getConnection();
                PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, studentId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    list.add(new CourseChoice(
                            rs.getString("学生编号"),
                            rs.getString("课程编号"),
                            rs.getString("成绩")));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }
}