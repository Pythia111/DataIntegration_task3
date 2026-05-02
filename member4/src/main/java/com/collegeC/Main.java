package com.collegeC;

import javax.swing.SwingUtilities;
import com.collegeC.gui.LoginFrame;
import com.collegeC.net.LocalHttpServer;

public class Main {
    public static void main(String[] args) {
        // 先启动本地HTTP服务器
        LocalHttpServer.startServer();

        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
                try {
                    javax.swing.UIManager.setLookAndFeel(javax.swing.UIManager.getSystemLookAndFeelClassName());
                } catch (Exception e) {
                }

                LoginFrame frame = new LoginFrame();
                frame.setVisible(true);
            }
        });
    }
}
