package com.collegeA.gui;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import com.collegeA.util.DatabaseConnection;

public class LoginFrame extends JFrame {
    private JTextField userField;
    private JPasswordField passField;
    private JButton loginButton;

    public LoginFrame() {
        setTitle("学院A - 教务系统登录");
        setSize(350, 200);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new GridLayout(4, 1));

        JPanel p1 = new JPanel();
        p1.add(new JLabel("账户名:"));
        userField = new JTextField(15);
        p1.add(userField);

        JPanel p2 = new JPanel();
        p2.add(new JLabel("密   码:"));
        passField = new JPasswordField(15);
        p2.add(passField);

        JPanel p3 = new JPanel();
        loginButton = new JButton("登录 / Login");
        p3.add(loginButton);

        add(p1);
        add(p2);
        add(p3);

        loginButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                loginButton.setEnabled(false);
                loginButton.setText("连接数据库验证中...");

                // 使用新线程防止界面卡死
                new Thread(() -> {
                    checkLogin();
                    SwingUtilities.invokeLater(() -> {
                        loginButton.setEnabled(true);
                        loginButton.setText("登录 / Login");
                    });
                }).start();
            }
        });
    }

    private void checkLogin() {
        String user = userField.getText();
        String pass = new String(passField.getPassword());

        try (Connection con = DatabaseConnection.getConnection();
                PreparedStatement ps = con.prepareStatement("SELECT 权限 FROM AccountA WHERE 账户名=? AND 密码=?")) {

            ps.setString(1, user);
            ps.setString(2, pass);
            ResultSet rs = ps.executeQuery();

            if (rs.next()) {
                String role = rs.getString("权限");
                JOptionPane.showMessageDialog(null, "登录成功! 权限: " + role);
                dispose();
                if ("STU".equals(role)) {
                    new StudentFrame(user).setVisible(true);
                } else {
                    new AdminFrame(user).setVisible(true);
                }
            } else {
                JOptionPane.showMessageDialog(this, "账户名或密码错误!");
            }
        } catch (Exception ex) {
            ex.printStackTrace();
            JOptionPane.showMessageDialog(this, "数据库连接失败: " + ex.getMessage());
        }
    }
}