package com.collegeA.dao;

import com.collegeA.entity.Course;
import com.collegeA.util.DatabaseConnection;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

public class CourseDAO {

    public List<Course> getAllLocalCourses() {
        List<Course> list = new ArrayList<>();
        String sql = "SELECT * FROM CourseA";
        try (Connection conn = DatabaseConnection.getConnection();
                PreparedStatement ps = conn.prepareStatement(sql);
                ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                list.add(new Course(
                        rs.getString("课程编号"),
                        rs.getString("课程名称"),
                        rs.getString("学分"),
                        rs.getString("授课老师"),
                        rs.getString("授课地点"),
                        rs.getString("共享")));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public List<Course> getSharedCourses() {
        List<Course> list = new ArrayList<>();
        String sql = "SELECT * FROM CourseA WHERE 共享 = 'Y'";
        try (Connection conn = DatabaseConnection.getConnection();
                PreparedStatement ps = conn.prepareStatement(sql);
                ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                list.add(new Course(
                        rs.getString("课程编号"),
                        rs.getString("课程名称"),
                        rs.getString("学分"),
                        rs.getString("授课老师"),
                        rs.getString("授课地点"),
                        rs.getString("共享")));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public boolean updateShareFlag(String courseId, String flag) {
        String sql = "UPDATE CourseA SET 共享 = ? WHERE 课程编号 = ?";
        try (Connection conn = DatabaseConnection.getConnection();
                PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, flag);
            ps.setString(2, courseId);
            return ps.executeUpdate() > 0;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }
}