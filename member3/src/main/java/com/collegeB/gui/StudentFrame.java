package com.collegeB.gui;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

import com.collegeB.dao.ChoiceDAO;
import com.collegeB.dao.CourseDAO;
import com.collegeB.dao.StudentDAO;
import com.collegeB.entity.Course;
import com.collegeB.entity.CourseChoice;
import com.collegeB.net.IntegrationClient;
import com.collegeB.xml.XMLBuilder;

public class StudentFrame extends JFrame {
    private final String username;
    private final String studentId;

    public StudentFrame(String username) {
        this.username = username;
        StudentDAO studentDAO = new StudentDAO();
        this.studentId = studentDAO.getStudentSidByAccount(username);

        setTitle("学院B - 学生端 (" + this.username + " | 学号: " + studentId + ")");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        JTabbedPane tabbedPane = new JTabbedPane();
        tabbedPane.addTab("本校课程", createLocalCoursePanel());
        tabbedPane.addTab("跨院共享课程", createSharedCoursePanel());
        tabbedPane.addTab("我的课表", createMySchedulePanel());
        add(tabbedPane, BorderLayout.CENTER);
    }

    private JPanel createLocalCoursePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = {"课程编号", "课程名称", "课时", "学分", "老师", "地点", "共享"};
        DefaultTableModel model = new DefaultTableModel(columns, 0);
        JTable table = new JTable(model);

        CourseDAO courseDAO = new CourseDAO();
        List<Course> courses = courseDAO.getAllLocalCourses();
        for (Course c : courses) {
            model.addRow(new Object[]{c.getCid(), c.getCname(), c.getHours(), c.getCredit(), c.getTeacher(), c.getLocation(), c.getShare()});
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
            String cid = (String) table.getValueAt(row, 0);
            ChoiceDAO choiceDAO = new ChoiceDAO();
            if (choiceDAO.enroll(studentId, cid)) {
                JOptionPane.showMessageDialog(this, "选课成功！请在'我的课表'中查看。");
            } else {
                JOptionPane.showMessageDialog(this, "选课失败，可能已经选过该课程。");
            }
        });

        return panel;
    }

    private JPanel createSharedCoursePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = {"课程编号", "课程名称", "课时", "学分", "老师", "地点", "开课学院"};
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
            String xmlResponse = IntegrationClient.getSharedCoursesFromOtherColleges();
            if (xmlResponse == null || xmlResponse.isEmpty()) {
                JOptionPane.showMessageDialog(this, "未获取到数据，请确保集成服务器已在 localhost:8080 启动。");
                return;
            }
            List<Course> sharedCourses = XMLBuilder.parseSharedCoursesXML(xmlResponse);
            model.setRowCount(0);
            for (Course c : sharedCourses) {
                String source = guessCollegeByCourseId(c.getCid());
                model.addRow(new Object[]{c.getCid(), c.getCname(), c.getHours(), c.getCredit(), c.getTeacher(), c.getLocation(), source});
            }
            JOptionPane.showMessageDialog(this, "成功获取跨院共享课程！");
        });

        remoteSelectBtn.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row == -1) {
                JOptionPane.showMessageDialog(this, "请优先获取并选择一门跨院共享课程");
                return;
            }
            String cid = (String) table.getValueAt(row, 0);
            String reqXml = XMLBuilder.buildEnrollRequestXML(studentId, cid, "ENROLL");
            String respXml = IntegrationClient.sendEnrollOrDropRequest(reqXml);
            if (respXml != null) {
                String result = XMLBuilder.parseChoiceResponseXML(respXml);
                JOptionPane.showMessageDialog(this, "跨院选课结果: " + result);
            } else {
                JOptionPane.showMessageDialog(this, "请求失败，请确保集成服务器正常工作。");
            }
        });

        return panel;
    }

    private JPanel createMySchedulePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = {"学号", "课程编号", "得分", "开课学院"};
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
                String collegeName = guessCollegeByCourseId(c.getCid());
                model.addRow(new Object[]{c.getSid(), c.getCid(), c.getScore(), collegeName});
            }
        };
        refreshData.run();

        refreshBtn.addActionListener(e -> refreshData.run());

        dropBtn.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row == -1) {
                JOptionPane.showMessageDialog(this, "请选择一门要退的课程");
                return;
            }
            String cid = (String) table.getValueAt(row, 1);
            String college = (String) table.getValueAt(row, 3);

            if ("学院B".equals(college)) {
                ChoiceDAO choiceDAO = new ChoiceDAO();
                if (choiceDAO.drop(studentId, cid)) {
                    JOptionPane.showMessageDialog(this, "本院退课成功！");
                    refreshData.run();
                } else {
                    JOptionPane.showMessageDialog(this, "本院退课失败。");
                }
            } else {
                String reqXml = XMLBuilder.buildEnrollRequestXML(studentId, cid, "DROP");
                String respXml = IntegrationClient.sendEnrollOrDropRequest(reqXml);
                if (respXml != null) {
                    String result = XMLBuilder.parseChoiceResponseXML(respXml);
                    JOptionPane.showMessageDialog(this, "跨院退课结果: " + result);
                } else {
                    JOptionPane.showMessageDialog(this, "跨院退课请求失败，请确保集成服务器正常工作。");
                }
                refreshData.run();
            }
        });

        return panel;
    }

    private static String guessCollegeByCourseId(String id) {
        if (id == null) return "未知";
        String upper = id.toUpperCase();
        if (upper.contains("_A") || upper.startsWith("C_A") || upper.startsWith("A")) return "学院A";
        if (upper.contains("_B") || upper.startsWith("C_B") || upper.startsWith("B")) return "学院B";
        if (upper.contains("_C") || upper.startsWith("C_C") || upper.startsWith("C")) return "学院C";
        return "其他学院";
    }
}
