package com.collegeB.gui;

import javax.swing.*;
import java.awt.*;

import com.collegeB.dao.StudentDAO;

public class LoginFrame extends JFrame {
    private final JTextField userField;
    private final JPasswordField passField;
    private final JButton loginButton;

    public LoginFrame() {
        setTitle("学院B - 教务系统登录");
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

        loginButton.addActionListener(e -> {
            loginButton.setEnabled(false);
            loginButton.setText("连接数据库验证中...");
            new Thread(() -> {
                checkLogin();
                SwingUtilities.invokeLater(() -> {
                    loginButton.setEnabled(true);
                    loginButton.setText("登录 / Login");
                });
            }).start();
        });
    }

    private void checkLogin() {
        String user = userField.getText();
        String pass = new String(passField.getPassword());

        StudentDAO studentDAO = new StudentDAO();
        String result = studentDAO.login(user, pass);
        if (result != null) {
            boolean isAdmin = studentDAO.isAdmin(user);
            JOptionPane.showMessageDialog(null, "登录成功! 权限: " + (isAdmin ? "管理员" : "学生"));
            dispose();
            if (isAdmin) {
                new AdminFrame(user).setVisible(true);
            } else {
                new StudentFrame(user).setVisible(true);
            }
        } else {
            JOptionPane.showMessageDialog(this, "账户名或密码错误!");
        }
    }
}
