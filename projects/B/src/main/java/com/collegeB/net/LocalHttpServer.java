package com.collegeB.net;

import com.collegeB.dao.ChoiceDAO;
import com.collegeB.dao.CourseDAO;
import com.collegeB.entity.Course;
import com.collegeB.util.DatabaseConnection;
import com.collegeB.xml.XMLBuilder;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.ResultSet;
import java.util.List;

public class LocalHttpServer {

    public static void startServer() {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress(8082), 0);

            server.createContext("/api/local/sharedCourses", new HttpHandler() {
                @Override
                public void handle(HttpExchange exchange) throws IOException {
                    CourseDAO dao = new CourseDAO();
                    List<Course> shared = dao.getSharedCourses();
                    String xmlResp = XMLBuilder.buildLocalCoursesXML(shared);
                    writeXml(exchange, 200, xmlResp);
                }
            });

            server.createContext("/api/local/enroll", new HttpHandler() {
                @Override
                public void handle(HttpExchange exchange) throws IOException {
                    if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                        exchange.sendResponseHeaders(405, -1);
                        return;
                    }

                    String reqXml = readAll(exchange.getRequestBody());
                    String sid = extractTag(reqXml, "sid");
                    String cid = extractTag(reqXml, "cid");

                    ChoiceDAO choiceDAO = new ChoiceDAO();
                    boolean success = choiceDAO.enroll(sid, cid);

                    String respXml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                            + "<response><status>" + (success ? "SUCCESS" : "FAIL")
                            + "</status><message>"
                            + (success ? "选课成功" : "选课失败，可能已选过该课程")
                            + "</message></response>";
                    writeXml(exchange, 200, respXml);
                }
            });

            server.createContext("/api/local/drop", new HttpHandler() {
                @Override
                public void handle(HttpExchange exchange) throws IOException {
                    if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                        exchange.sendResponseHeaders(405, -1);
                        return;
                    }

                    String reqXml = readAll(exchange.getRequestBody());
                    String sid = extractTag(reqXml, "sid");
                    String cid = extractTag(reqXml, "cid");

                    ChoiceDAO choiceDAO = new ChoiceDAO();
                    boolean success = choiceDAO.drop(sid, cid);

                    String respXml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                            + "<response><status>" + (success ? "SUCCESS" : "FAIL")
                            + "</status><message>"
                            + (success ? "退选成功" : "退选失败，未找到该选课记录")
                            + "</message></response>";
                    writeXml(exchange, 200, respXml);
                }
            });

            server.createContext("/api/local/statistics", new HttpHandler() {
                @Override
                public void handle(HttpExchange exchange) throws IOException {
                    try (Connection conn = DatabaseConnection.getConnection()) {
                        int studentCount = 0, courseCount = 0, choiceCount = 0;
                        ResultSet rs;

                        rs = conn.createStatement().executeQuery("SELECT COUNT(*) FROM StudentB");
                        if (rs.next()) studentCount = rs.getInt(1);
                        rs.close();

                        rs = conn.createStatement().executeQuery("SELECT COUNT(*) FROM CourseB");
                        if (rs.next()) courseCount = rs.getInt(1);
                        rs.close();

                        rs = conn.createStatement().executeQuery("SELECT COUNT(*) FROM CourseChoiceB");
                        if (rs.next()) choiceCount = rs.getInt(1);
                        rs.close();

                        String xmlResp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                                + "<statistics><college name=\"B\">"
                                + "<students>" + studentCount + "</students>"
                                + "<courses>" + courseCount + "</courses>"
                                + "<choices>" + choiceCount + "</choices>"
                                + "</college></statistics>";
                        writeXml(exchange, 200, xmlResp);
                    } catch (Exception e) {
                        e.printStackTrace();
                        String err = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><error>" + e.getMessage() + "</error>";
                        writeXml(exchange, 500, err);
                    }
                }
            });

            server.setExecutor(null);
            server.start();
            System.out.println("学院B本地服务器已启动，监听端口 8082...");
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

    private static void writeXml(HttpExchange exchange, int statusCode, String xml) throws IOException {
        if (xml == null) {
            xml = "";
        }
        byte[] response = xml.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/xml; charset=UTF-8");
        exchange.sendResponseHeaders(statusCode, response.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(response);
        }
    }

    private static String readAll(InputStream is) throws IOException {
        try (InputStream input = is; ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while ((n = input.read(buf)) >= 0) {
                baos.write(buf, 0, n);
            }
            return new String(baos.toByteArray(), StandardCharsets.UTF_8);
        }
    }
}
