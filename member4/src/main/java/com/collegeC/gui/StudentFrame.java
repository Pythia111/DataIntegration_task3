package com.collegeC.gui;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

import com.collegeC.dao.ChoiceDAO;
import com.collegeC.dao.CourseDAO;
import com.collegeC.dao.StudentDAO;
import com.collegeC.entity.Course;
import com.collegeC.entity.CourseChoice;
import com.collegeC.net.IntegrationClient;
import com.collegeC.xml.XMLBuilder;

public class StudentFrame extends JFrame {
    private String username;
    private String studentId;

    public StudentFrame(String username) {
        this.username = username;
        StudentDAO studentDAO = new StudentDAO();
        this.studentId = studentDAO.getStudentSnoByAccount(username);

        setTitle("学院C - 学生端 (" + username + " | 学号: " + studentId + ")");
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

    private JPanel createLocalCoursePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = {"课程编号", "课程名称", "课时", "学分", "授课老师", "授课地点", "共享"};
        DefaultTableModel model = new DefaultTableModel(columns, 0);
        JTable table = new JTable(model);

        CourseDAO courseDAO = new CourseDAO();
        List<Course> courses = courseDAO.getAllLocalCourses();
        for (Course c : courses) {
            model.addRow(new Object[]{c.getCno(), c.getCnm(), c.getCtm(), c.getCpt(),
                    c.getTec(), c.getPla(), c.getShare()});
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
            String cno = (String) table.getValueAt(row, 0);
            ChoiceDAO choiceDAO = new ChoiceDAO();
            if (choiceDAO.enroll(studentId, cno)) {
                JOptionPane.showMessageDialog(this, "选课成功！请在'我的课表'中查看。");
            } else {
                JOptionPane.showMessageDialog(this, "选课失败，可能已经选过该课程。");
            }
        });

        return panel;
    }

    private JPanel createSharedCoursePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = {"课程编号", "课程名称", "课时", "学分", "授课老师", "授课地点", "开课学院"};
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
                // 根据课程编号前缀判断来源学院
                String source = "其他学院";
                String id = c.getCno();
                if (id.startsWith("A") || id.contains("_A")) source = "学院A";
                else if (id.startsWith("B") || id.contains("_B")) source = "学院B";

                model.addRow(new Object[]{c.getCno(), c.getCnm(), c.getCtm(), c.getCpt(),
                        c.getTec(), c.getPla(), source});
            }
            JOptionPane.showMessageDialog(this, "成功获取跨院共享课程！");
        });

        remoteSelectBtn.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row == -1) {
                JOptionPane.showMessageDialog(this, "请优先获取并选择一门跨院共享课程");
                return;
            }
            String cno = (String) table.getValueAt(row, 0);

            String reqXml = XMLBuilder.buildEnrollRequestXML(studentId, cno, "ENROLL");
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
        String[] columns = {"学生编号", "课程编号", "成绩", "开课学院"};
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
                String collegeName = "学院C"; // 默认本院
                String cno = c.getCno();
                if (cno.startsWith("A") || cno.contains("_A")) collegeName = "学院A";
                else if (cno.startsWith("B") || cno.contains("_B")) collegeName = "学院B";

                model.addRow(new Object[]{c.getSno(), c.getCno(), c.getGrd(), collegeName});
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
            String cno = (String) table.getValueAt(row, 1);
            String college = (String) table.getValueAt(row, 3);

            if ("学院C".equals(college)) {
                // 本院退课
                ChoiceDAO choiceDAO = new ChoiceDAO();
                if (choiceDAO.drop(studentId, cno)) {
                    JOptionPane.showMessageDialog(this, "本院退课成功！");
                    refreshData.run();
                } else {
                    JOptionPane.showMessageDialog(this, "本院退课失败。");
                }
            } else {
                // 跨院退课
                String reqXml = XMLBuilder.buildEnrollRequestXML(studentId, cno, "DROP");
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
}
