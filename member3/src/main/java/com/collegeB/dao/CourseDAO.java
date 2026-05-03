package com.collegeB.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.ArrayList;
import java.util.List;

import com.collegeB.entity.Course;
import com.collegeB.util.DatabaseConnection;

public class CourseDAO {

    public List<Course> getAllLocalCourses() {
        List<Course> list = new ArrayList<>();
        String sql = "SELECT * FROM CourseB ORDER BY CID";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                list.add(new Course(
                        rs.getString("CID"),
                        rs.getString("CNAME"),
                        rs.getString("HOURS"),
                        rs.getString("CREDIT"),
                        rs.getString("TEACHER"),
                        rs.getString("LOCATION"),
                        rs.getString("SHARE")));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public List<Course> getSharedCourses() {
        List<Course> list = new ArrayList<>();
        String sql = "SELECT * FROM CourseB WHERE SHARE = 'Y' ORDER BY CID";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                list.add(new Course(
                        rs.getString("CID"),
                        rs.getString("CNAME"),
                        rs.getString("HOURS"),
                        rs.getString("CREDIT"),
                        rs.getString("TEACHER"),
                        rs.getString("LOCATION"),
                        rs.getString("SHARE")));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public boolean updateShareFlag(String cid, String flag) {
        String sql = "UPDATE CourseB SET SHARE = ? WHERE CID = ?";
        try (Connection conn = DatabaseConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, flag);
            ps.setString(2, cid);
            return ps.executeUpdate() > 0;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }
}
