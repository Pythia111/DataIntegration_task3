package com.integration;

import com.integration.server.IntegrationServer;

public class Main {
    public static void main(String[] args) {
        int port = 8080;
        if (args.length > 0) {
            try {
                port = Integer.parseInt(args[0]);
            } catch (NumberFormatException e) {
                System.err.println("Invalid port, using default 8080");
            }
        }
        System.out.println("============================================");
        System.out.println("  集成服务器 (Integration Server)");
        System.out.println("  监听端口: " + port);
        System.out.println("============================================");
        IntegrationServer.start(port);
    }
}
