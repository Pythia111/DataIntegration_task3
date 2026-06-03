package com.collegeC.net;

import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.List;

import com.collegeC.dao.CourseDAO;
import com.collegeC.dao.ChoiceDAO;
import com.collegeC.entity.Course;
import com.collegeC.xml.XMLBuilder;

public class LocalHttpServer {

    public static void startServer() {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress(8083), 0);

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

            // 接口2：处理跨院选课请求（来自集成服务器转发）
            server.createContext("/api/local/enroll", new HttpHandler() {
                @Override
                public void handle(HttpExchange exchange) throws IOException {
                    if ("POST".equals(exchange.getRequestMethod())) {
                        InputStream is = exchange.getRequestBody();
                        byte[] bytes = new byte[is.available()];
                        is.read(bytes);
                        String reqXml = new String(bytes, StandardCharsets.UTF_8);

                        // 解析请求XML获取学号和课程编号
                        String sno = extractTag(reqXml, "sid");
                        String cno = extractTag(reqXml, "cid");

                        ChoiceDAO choiceDAO = new ChoiceDAO();
                        boolean success = choiceDAO.enroll(sno, cno);

                        String respXml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                                + "<response><status>" + (success ? "SUCCESS" : "FAIL")
                                + "</status><message>"
                                + (success ? "选课成功" : "选课失败，可能已选过该课程")
                                + "</message></response>";

                        byte[] response = respXml.getBytes(StandardCharsets.UTF_8);
                        exchange.getResponseHeaders().set("Content-Type", "application/xml; charset=UTF-8");
                        exchange.sendResponseHeaders(200, response.length);
                        OutputStream os = exchange.getResponseBody();
                        os.write(response);
                        os.close();
                    }
                }
            });

            // 接口3：处理跨院退选课请求（来自集成服务器转发）
            server.createContext("/api/local/drop", new HttpHandler() {
                @Override
                public void handle(HttpExchange exchange) throws IOException {
                    if ("POST".equals(exchange.getRequestMethod())) {
                        InputStream is = exchange.getRequestBody();
                        byte[] bytes = new byte[is.available()];
                        is.read(bytes);
                        String reqXml = new String(bytes, StandardCharsets.UTF_8);

                        String sno = extractTag(reqXml, "sid");
                        String cno = extractTag(reqXml, "cid");

                        ChoiceDAO choiceDAO = new ChoiceDAO();
                        boolean success = choiceDAO.drop(sno, cno);

                        String respXml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                                + "<response><status>" + (success ? "SUCCESS" : "FAIL")
                                + "</status><message>"
                                + (success ? "退选成功" : "退选失败，未找到该选课记录")
                                + "</message></response>";

                        byte[] response = respXml.getBytes(StandardCharsets.UTF_8);
                        exchange.getResponseHeaders().set("Content-Type", "application/xml; charset=UTF-8");
                        exchange.sendResponseHeaders(200, response.length);
                        OutputStream os = exchange.getResponseBody();
                        os.write(response);
                        os.close();
                    }
                }
            });

            // 接口4：获取本院统计信息
            server.createContext("/api/local/statistics", new HttpHandler() {
                @Override
                public void handle(HttpExchange exchange) throws IOException {
                    try (java.sql.Connection conn = com.collegeC.util.DatabaseConnection.getConnection()) {
                        int studentCount = 0, courseCount = 0, choiceCount = 0;
                        java.sql.ResultSet rs;

                        rs = conn.createStatement().executeQuery("SELECT COUNT(*) FROM StudentC");
                        if (rs.next()) studentCount = rs.getInt(1);

                        rs = conn.createStatement().executeQuery("SELECT COUNT(*) FROM CourseC");
                        if (rs.next()) courseCount = rs.getInt(1);

                        rs = conn.createStatement().executeQuery("SELECT COUNT(*) FROM CourseChoiceC");
                        if (rs.next()) choiceCount = rs.getInt(1);

                        String xmlResp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                                + "<statistics><college name=\"C\">"
                                + "<students>" + studentCount + "</students>"
                                + "<courses>" + courseCount + "</courses>"
                                + "<choices>" + choiceCount + "</choices>"
                                + "</college></statistics>";

                        byte[] response = xmlResp.getBytes(StandardCharsets.UTF_8);
                        exchange.getResponseHeaders().set("Content-Type", "application/xml; charset=UTF-8");
                        exchange.sendResponseHeaders(200, response.length);
                        OutputStream os = exchange.getResponseBody();
                        os.write(response);
                        os.close();
                    } catch (Exception e) {
                        e.printStackTrace();
                        String err = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><error>" + e.getMessage() + "</error>";
                        byte[] response = err.getBytes(StandardCharsets.UTF_8);
                        exchange.sendResponseHeaders(500, response.length);
                        OutputStream os = exchange.getResponseBody();
                        os.write(response);
                        os.close();
                    }
                }
            });

            server.setExecutor(null);
            server.start();
            System.out.println("学院C本地服务器已启动，监听端口 8083...");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static String extractTag(String xml, String tagName) {
        String startTag = "<" + tagName + ">";
        String endTag = "</" + tagName + ">";
        int start = xml.indexOf(startTag);
        int end = xml.indexOf(endTag);
        if (start >= 0 && end > start) {
            return xml.substring(start + startTag.length(), end);
        }
        return "";
    }
}
