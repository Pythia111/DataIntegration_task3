package com.collegeA.net;

import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;
import java.io.IOException;
import java.io.OutputStream;
import java.io.InputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.List;
import com.collegeA.dao.CourseDAO;
import com.collegeA.dao.ChoiceDAO;
import com.collegeA.entity.Course;
import com.collegeA.xml.XMLBuilder;

public class LocalHttpServer {

    public static void startServer() {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress(8081), 0);

            // 接口1：获取本院共享课程
            server.createContext("/api/local/sharedCourses", new HttpHandler() {
                @Override
                public void handle(HttpExchange exchange) throws IOException {
                    CourseDAO dao = new CourseDAO();
                    List<Course> shared = dao.getSharedCourses();
                    String xmlResp = XMLBuilder.buildLocalCoursesXML(shared);

                    byte[] response = xmlResp.getBytes(StandardCharsets.UTF_8);
                    exchange.getResponseHeaders().set("Content-Type", "application/xml; charset=UTF-8");
                    exchange.sendResponseHeaders(200, response.length);
                    OutputStream os = exchange.getResponseBody();
                    os.write(response);
                    os.close();
                }
            });

            // 其他接口（如处理被请求跨校选课、全局统计等）可以继续在此添加

            server.setExecutor(null);
            server.start();
            System.out.println("学院A本地服务器已启动，监听端口 8081...");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}