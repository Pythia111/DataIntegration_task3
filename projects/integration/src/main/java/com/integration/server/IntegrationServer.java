package com.integration.server;

import com.integration.handler.CourseChoiceHandler;
import com.integration.handler.SharedCoursesHandler;
import com.integration.handler.StatisticsHandler;
import com.sun.net.httpserver.HttpServer;

import java.net.InetSocketAddress;
import java.util.logging.Logger;

public class IntegrationServer {

    private static final Logger LOGGER = Logger.getLogger(IntegrationServer.class.getName());

    public static void start(int port) {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

            server.createContext("/api/integration/sharedCourses", new SharedCoursesHandler());
            server.createContext("/api/integration/courseChoice", new CourseChoiceHandler());
            server.createContext("/api/integration/statistics", new StatisticsHandler());

            server.setExecutor(null);
            server.start();

            LOGGER.info("Integration Server started on port " + port);
            System.out.println("集成服务器已启动，监听端口 " + port + " ...");
            System.out.println("接口列表:");
            System.out.println("  GET  /api/integration/sharedCourses?source={A|B|C}  - 获取其他学院共享课程");
            System.out.println("  POST /api/integration/courseChoice?source={A|B|C}    - 跨院选课/退选课");
            System.out.println("  GET  /api/integration/statistics                    - 全局统计信息");
        } catch (Exception e) {
            LOGGER.severe("Failed to start Integration Server: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
