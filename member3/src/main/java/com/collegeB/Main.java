package com.collegeB;

import javax.swing.SwingUtilities;

import com.collegeB.gui.LoginFrame;
import com.collegeB.net.LocalHttpServer;

public class Main {
    public static void main(String[] args) {
        LocalHttpServer.startServer();

        SwingUtilities.invokeLater(() -> {
            try {
                javax.swing.UIManager.setLookAndFeel(javax.swing.UIManager.getSystemLookAndFeelClassName());
            } catch (Exception ignored) {
            }

            LoginFrame frame = new LoginFrame();
            frame.setVisible(true);
        });
    }
}
