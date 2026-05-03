package com.collegeB.gui;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

import com.collegeB.dao.CourseDAO;
import com.collegeB.entity.Course;
import com.collegeB.net.IntegrationClient;

public class AdminFrame extends JFrame {
    private final String username;

    public AdminFrame(String username) {
        this.username = username;
        setTitle("学院B - 管理员端 (" + this.username + ")");
        setSize(800, 600);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        JTabbedPane tabbedPane = new JTabbedPane();
        tabbedPane.addTab("本地课程管理", createCourseManagePanel());
        tabbedPane.addTab("全局统计", createStatisticsPanel());
        add(tabbedPane, BorderLayout.CENTER);
    }

    private JPanel createCourseManagePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        String[] columns = {"课程编号", "课程名称", "课时", "学分", "老师", "地点", "共享"};
        DefaultTableModel model = new DefaultTableModel(columns, 0);
        JTable table = new JTable(model);

        Runnable loadData = () -> {
            model.setRowCount(0);
            CourseDAO courseDAO = new CourseDAO();
            List<Course> courses = courseDAO.getAllLocalCourses();
            for (Course c : courses) {
                model.addRow(new Object[]{c.getCid(), c.getCname(), c.getHours(), c.getCredit(), c.getTeacher(), c.getLocation(), c.getShare()});
            }
        };
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
            String cid = (String) table.getValueAt(row, 0);
            CourseDAO courseDAO = new CourseDAO();
            if (courseDAO.updateShareFlag(cid, "Y")) {
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
            String cid = (String) table.getValueAt(row, 0);
            CourseDAO courseDAO = new CourseDAO();
            if (courseDAO.updateShareFlag(cid, "N")) {
                JOptionPane.showMessageDialog(this, "取消共享成功！");
                loadData.run();
            } else {
                JOptionPane.showMessageDialog(this, "取消失败。");
            }
        });

        refreshBtn.addActionListener(e -> loadData.run());

        return panel;
    }

    private JPanel createStatisticsPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        JTextArea textArea = new JTextArea();
        textArea.setEditable(false);
        textArea.setFont(new Font("Monospaced", Font.PLAIN, 14));
        panel.add(new JScrollPane(textArea), BorderLayout.CENTER);

        JPanel bottomPanel = new JPanel();
        JButton refreshBtn = new JButton("获取全局统计");
        bottomPanel.add(refreshBtn);
        panel.add(bottomPanel, BorderLayout.SOUTH);

        refreshBtn.addActionListener(e -> {
            String xmlResp = IntegrationClient.getGlobalStatistics();
            if (xmlResp == null || xmlResp.isEmpty()) {
                textArea.setText("未获取到数据，请确保集成服务器已在 localhost:8080 启动。");
                return;
            }
            textArea.setText("全局统计信息 (XML):\n\n" + xmlResp);
        });

        return panel;
    }
}
