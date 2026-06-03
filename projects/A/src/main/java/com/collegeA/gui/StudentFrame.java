package com.collegeA.gui;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.util.List;

import com.collegeA.dao.ChoiceDAO;
import com.collegeA.dao.CourseDAO;
import com.collegeA.entity.Course;
import com.collegeA.entity.CourseChoice;
import com.collegeA.net.IntegrationClient;
import com.collegeA.util.DatabaseConnection;
import com.collegeA.xml.XMLBuilder;

public class StudentFrame extends JFrame {
    private String username;
    private String studentId;

    public StudentFrame(String username) {
        this.username = username;
        this.studentId = fetchStudentId(username);

        setTitle("学院A - 学生端 (" + username + " | 学号: " + studentId + ")");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        JTabbedPane tabbedPane = new JTabbedPane();

        // 1. 本校课程查询与选课
        tabbedPane.addTab("本校课程", createLocalCoursePanel());

        // 2. 跨院共享课程查询与选课
        tabbedPane.addTab("跨院共享课程", createSharedCoursePanel());

        // 3. 个人课表与退课
        tabbedPane.addTab("我的课表", createMySchedulePanel());

        add(tabbedPane, BorderLayout.CENTER);
    }

    private String fetchStudentId(String account) {
        try (Connection con = DatabaseConnection.getConnection();
                PreparedStatement ps = con.prepareStatement("SELECT 学号 FROM StudentA WHERE 关联账户=?")) {
            ps.setString(1, account);
            ResultSet rs = ps.executeQuery();
            if (rs.next())
                return rs.getString("学号");
        } catch (Exception e) {
            e.printStackTrace();
        }
        return "UNKNOWN";
    }

    private JPanel createLocalCoursePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = { "课程编号", "课程名称", "学分", "授课老师", "授课地点", "共享" };
        DefaultTableModel model = new DefaultTableModel(columns, 0);
        JTable table = new JTable(model);

        CourseDAO courseDAO = new CourseDAO();
        List<Course> courses = courseDAO.getAllLocalCourses();
        for (Course c : courses) {
            model.addRow(new Object[] { c.getId(), c.getName(), c.getScore(), c.getTeacher(), c.getLocation(),
                    c.getShare() });
        }

        panel.add(new JScrollPane(table), BorderLayout.CENTER);

        JPanel bottomPanel = new JPanel();
        JButton selectBtn = new JButton("选择本校课程");
        bottomPanel.add(selectBtn);
        panel.add(bottomPanel, BorderLayout.SOUTH);

        selectBtn.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row == -1) {
                JOptionPane.showMessageDialog(this, "请先选择一门课程");
                return;
            }
            String courseId = (String) table.getValueAt(row, 0);
            ChoiceDAO choiceDAO = new ChoiceDAO();
            if (choiceDAO.enroll(studentId, courseId)) {
                JOptionPane.showMessageDialog(this, "选课成功！请在'我的课表'中查看。");
            } else {
                JOptionPane.showMessageDialog(this, "选课失败，可能已经选过该课程。");
            }
        });

        return panel;
    }

    private JPanel createSharedCoursePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = { "课程编号", "课程名称", "学分", "授课老师", "授课地点", "目标学院" };
        DefaultTableModel model = new DefaultTableModel(columns, 0);
        JTable table = new JTable(model);

        panel.add(new JScrollPane(table), BorderLayout.CENTER);

        JPanel bottomPanel = new JPanel();
        JButton refreshBtn = new JButton("获取跨院共享课程");
        JButton remoteSelectBtn = new JButton("跨院选课");
        bottomPanel.add(refreshBtn);
        bottomPanel.add(remoteSelectBtn);
        panel.add(bottomPanel, BorderLayout.SOUTH);

        refreshBtn.addActionListener(e -> {
            // 通过HTTP请求集成服务器
            String xmlResponse = IntegrationClient.getSharedCoursesFromOtherColleges();
            if (xmlResponse == null || xmlResponse.isEmpty()) {
                JOptionPane.showMessageDialog(this, "未获取到数据，请确保集成服务器(成员5)已在 localhost:8080 启动。");
                return;
            }
            List<Course> sharedCourses = XMLBuilder.parseSharedCoursesXML(xmlResponse);
            model.setRowCount(0); // 清空
            for (Course c : sharedCourses) {
                String targetCollege = c.getId().contains("B") ? "学院B" : "学院C"; // 仅作示例推测
                model.addRow(new Object[] { c.getId(), c.getName(), c.getScore(), c.getTeacher(), c.getLocation(),
                        targetCollege });
            }
            JOptionPane.showMessageDialog(this, "成功获取跨院共享课程！");
        });

        remoteSelectBtn.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row == -1) {
                JOptionPane.showMessageDialog(this, "请优先获取并选择一门跨院共享课程");
                return;
            }
            String courseId = (String) table.getValueAt(row, 0);

            // 构造跨院选课XML
            String reqXml = XMLBuilder.buildEnrollRequestXML(studentId, courseId, "ENROLL");
            String respXml = IntegrationClient.sendEnrollOrDropRequest(reqXml);

            if (respXml != null) {
                JOptionPane.showMessageDialog(this, "集成服务器返回:\n" + respXml);
            } else {
                JOptionPane.showMessageDialog(this, "请求失败，请确保集成服务器正常工作。");
            }
        });

        return panel;
    }

    private JPanel createMySchedulePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = { "学生编号", "课程编号", "成绩", "开课学院" };
        DefaultTableModel model = new DefaultTableModel(columns, 0);
        JTable table = new JTable(model);
        panel.add(new JScrollPane(table), BorderLayout.CENTER);

        JPanel bottomPanel = new JPanel();
        JButton refreshBtn = new JButton("刷新课表");
        JButton dropBtn = new JButton("退选课程");
        bottomPanel.add(refreshBtn);
        bottomPanel.add(dropBtn);
        panel.add(bottomPanel, BorderLayout.SOUTH);

        Runnable refreshData = () -> {
            ChoiceDAO choiceDAO = new ChoiceDAO();
            List<CourseChoice> choices = choiceDAO.getStudentSchedule(studentId);
            model.setRowCount(0);
            for (CourseChoice c : choices) {
                String collegeName = "学院A"; // 默认本院
                if (c.getCourseId().startsWith("C_B"))
                    collegeName = "学院B";
                else if (c.getCourseId().startsWith("C_C"))
                    collegeName = "学院C";

                model.addRow(new Object[] { c.getStudentId(), c.getCourseId(), c.getScore(), collegeName });
            }
        };

        // 初始化加载数据
        refreshData.run();

        refreshBtn.addActionListener(e -> refreshData.run());

        dropBtn.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row == -1) {
                JOptionPane.showMessageDialog(this, "请选择一门要退的课程");
                return;
            }
            String courseId = (String) table.getValueAt(row, 1);

            // 如果是跨院的课程(示例判断: C_A 开头为本院，其余为外院)
            if (!courseId.startsWith("C_A")) {
                String reqXml = XMLBuilder.buildEnrollRequestXML(studentId, courseId, "DROP");
                String respXml = IntegrationClient.sendEnrollOrDropRequest(reqXml);
                JOptionPane.showMessageDialog(this, "发起了外院退课，集成服务器返回:\n" + respXml);
            } else {
                ChoiceDAO choiceDAO = new ChoiceDAO();
                if (choiceDAO.drop(studentId, courseId)) {
                    JOptionPane.showMessageDialog(this, "本院退课成功！");
                    refreshData.run();
                } else {
                    JOptionPane.showMessageDialog(this, "本院退课失败。");
                }
            }
            refreshData.run();
        });

        return panel;
    }
}