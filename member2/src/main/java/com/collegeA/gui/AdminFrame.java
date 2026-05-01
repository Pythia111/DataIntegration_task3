package com.collegeA.gui;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

import com.collegeA.dao.CourseDAO;
import com.collegeA.entity.Course;

public class AdminFrame extends JFrame {
    private String username;

    public AdminFrame(String username) {
        this.username = username;
        setTitle("学院A - 管理员端 (" + username + ")");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        JTabbedPane tabbedPane = new JTabbedPane();

        // 课程管理
        tabbedPane.addTab("本地课程管理", createCourseManagePanel());

        add(tabbedPane, BorderLayout.CENTER);
    }

    private JPanel createCourseManagePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = { "课程编号", "课程名称", "学分", "授课老师", "授课地点", "共享" };
        DefaultTableModel model = new DefaultTableModel(columns, 0);
        JTable table = new JTable(model);

        Runnable loadData = () -> {
            model.setRowCount(0);
            CourseDAO courseDAO = new CourseDAO();
            List<Course> courses = courseDAO.getAllLocalCourses();
            for (Course c : courses) {
                model.addRow(new Object[] { c.getId(), c.getName(), c.getScore(), c.getTeacher(), c.getLocation(),
                        c.getShare() });
            }
        };

        // 初始加载
        loadData.run();

        panel.add(new JScrollPane(table), BorderLayout.CENTER);

        JPanel bottomPanel = new JPanel();
        JButton setSharedBtn = new JButton("设置为共享(Y)");
        JButton setUnsharedBtn = new JButton("取消共享(N)");
        JButton refreshBtn = new JButton("刷新列表");
        bottomPanel.add(setSharedBtn);
        bottomPanel.add(setUnsharedBtn);
        bottomPanel.add(refreshBtn);
        panel.add(bottomPanel, BorderLayout.SOUTH);

        setSharedBtn.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row == -1) {
                JOptionPane.showMessageDialog(this, "请优先选择一门课程");
                return;
            }
            String courseId = (String) table.getValueAt(row, 0);
            CourseDAO courseDAO = new CourseDAO();
            if (courseDAO.updateShareFlag(courseId, "Y")) {
                JOptionPane.showMessageDialog(this, "设置共享成功！");
                loadData.run();
            } else {
                JOptionPane.showMessageDialog(this, "设置失败。");
            }
        });

        setUnsharedBtn.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row == -1) {
                JOptionPane.showMessageDialog(this, "请优先选择一门课程");
                return;
            }
            String courseId = (String) table.getValueAt(row, 0);
            CourseDAO courseDAO = new CourseDAO();
            if (courseDAO.updateShareFlag(courseId, "N")) {
                JOptionPane.showMessageDialog(this, "取消共享成功！");
                loadData.run();
            } else {
                JOptionPane.showMessageDialog(this, "取消失败。");
            }
        });

        refreshBtn.addActionListener(e -> loadData.run());

        return panel;
    }
}