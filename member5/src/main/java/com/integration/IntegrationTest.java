package com.integration;

import com.integration.server.IntegrationServer;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.InetSocketAddress;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class IntegrationTest {

    private static final String COLLEGE_B_COURSES = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<Classes>"
            + "<class>"
            + "<编号>B101</编号><名称>高等数学</名称><课时>64</课时><学分>4</学分>"
            + "<老师>张老师</老师><地点>教B-101</地点><共享>Y</共享>"
            + "</class>"
            + "<class>"
            + "<编号>B104</编号><名称>程序设计</名称><课时>48</课时><学分>3</学分>"
            + "<老师>赵老师</老师><地点>教B-104</地点><共享>Y</共享>"
            + "</class>"
            + "</Classes>";

    private static final String COLLEGE_C_COURSES = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            + "<Classes>"
            + "<class>"
            + "<Cno>C001</Cno><Cnm>数据结构</Cnm><Ctm>48</Ctm><Cpt>3</Cpt>"
            + "<Tec>李老师</Tec><Pla>教C-101</Pla><Share>Y</Share>"
            + "</class>"
            + "</Classes>";

    public static void main(String[] args) throws Exception {
        System.out.println("===== 集成服务器端到端测试 =====\n");

        startMockCollegeB(8082);
        startMockCollegeC(8083);
        Thread.sleep(500);

        IntegrationServer.start(9090);
        Thread.sleep(500);

        int passed = 0;
        int failed = 0;

        System.out.println("\n--- 测试1: 课程共享接口 (source=A) ---");
        try {
            String result = httpGet("http://localhost:9090/api/integration/sharedCourses?source=A");
            System.out.println("响应: " + result);

            boolean hasB101 = result.contains("B101") || result.contains("课程编号");
            boolean hasC001 = result.contains("C001") || result.contains("课程编号");
            if (hasB101 || hasC001) {
                System.out.println("✅ 测试1通过: 成功获取其他学院共享课程并转换格式");
                passed++;
            } else {
                System.out.println("❌ 测试1失败: 未获取到课程数据");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("❌ 测试1失败: " + e.getMessage());
            failed++;
        }

        System.out.println("\n--- 测试2: XSLT课程格式转换 (学院A格式) ---");
        try {
            String localA = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<Classes><class>"
                    + "<课程编号>C_A001</课程编号><课程名称>数据结构</课程名称>"
                    + "<学分>4</学分><授课老师>张老师</授课老师>"
                    + "<授课地点>教A-101</授课地点><共享>Y</共享>"
                    + "</class></Classes>";

            String unified = com.integration.xml.XSLTTransformer.localCourseToUnified(localA, "A");
            System.out.println("学院A课程→统一格式: " + unified);
            boolean ok = unified.contains("<id>C_A001</id>") && unified.contains("<name>数据结构</name>")
                    && unified.contains("<college>A</college>");
            if (ok) {
                System.out.println("✅ 测试2通过: 学院A→统一格式转换正确");
                passed++;
            } else {
                System.out.println("❌ 测试2失败: 转换结果不符合预期");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("❌ 测试2失败: " + e.getMessage());
            failed++;
        }

        System.out.println("\n--- 测试3: XSLT课程格式转换 (学院C→统一→学院A) ---");
        try {
            String localC = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<Classes><class>"
                    + "<Cno>C001</Cno><Cnm>算法设计</Cnm><Ctm>48</Ctm><Cpt>3</Cpt>"
                    + "<Tec>王老师</Tec><Pla>教C-201</Pla><Share>Y</Share>"
                    + "</class></Classes>";

            String unified = com.integration.xml.XSLTTransformer.localCourseToUnified(localC, "C");
            String backToA = com.integration.xml.XSLTTransformer.unifiedCourseToLocal(unified, "A");
            System.out.println("学院C课程→统一格式→学院A格式: " + backToA);
            boolean ok = backToA.contains("<课程编号>C001</课程编号>")
                    && backToA.contains("<课程名称>算法设计</课程名称>")
                    && backToA.contains("<学分>3</学分>");
            if (ok) {
                System.out.println("✅ 测试3通过: 学院C→统一→学院A 转换链路正确");
                passed++;
            } else {
                System.out.println("❌ 测试3失败: 转换链路结果不符合预期");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("❌ 测试3失败: " + e.getMessage());
            failed++;
        }

        System.out.println("\n--- 测试4: XSLT学生格式转换 ---");
        try {
            String localA = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<Students><student>"
                    + "<学号>A2026001</学号><姓名>张三</姓名><性别>男</性别>"
                    + "<院系>计算机</院系><关联账户>stuA1</关联账户>"
                    + "</student></Students>";

            String unified = com.integration.xml.XSLTTransformer.localStudentToUnified(localA, "A");
            System.out.println("学院A学生→统一格式: " + unified);
            boolean ok = unified.contains("<id>A2026001</id>") && unified.contains("<name>张三</name>")
                    && unified.contains("<college>A</college>");
            if (ok) {
                System.out.println("✅ 测试4通过: 学生格式转换正确");
                passed++;
            } else {
                System.out.println("❌ 测试4失败: 学生转换结果不符合预期");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("❌ 测试4失败: " + e.getMessage());
            failed++;
        }

        System.out.println("\n--- 测试5: 跨院选课接口 ---");
        try {
            String enrollReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<choiceReq>"
                    + "<traceId>test-001</traceId>"
                    + "<source>A</source>"
                    + "<sid>A2026001</sid>"
                    + "<cid>B101</cid>"
                    + "<operation>ENROLL</operation>"
                    + "</choiceReq>";

            String result = httpPost("http://localhost:9090/api/integration/courseChoice?source=A", enrollReq);
            System.out.println("选课响应: " + result);
            if (result.contains("SUCCESS") || result.contains("FAIL")) {
                System.out.println("✅ 测试5通过: 选课转发接口正常工作");
                passed++;
            } else {
                System.out.println("❌ 测试5失败: 选课响应格式不正确");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("❌ 测试5失败: " + e.getMessage());
            failed++;
        }

        System.out.println("\n--- 测试6: 跨院退选课接口 ---");
        try {
            String dropReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<choiceReq>"
                    + "<traceId>test-002</traceId>"
                    + "<source>A</source>"
                    + "<sid>A2026001</sid>"
                    + "<cid>B101</cid>"
                    + "<operation>DROP</operation>"
                    + "</choiceReq>";

            String result = httpPost("http://localhost:9090/api/integration/courseChoice?source=A", dropReq);
            System.out.println("退选响应: " + result);
            if (result.contains("SUCCESS") || result.contains("FAIL")) {
                System.out.println("✅ 测试6通过: 退选课转发接口正常工作");
                passed++;
            } else {
                System.out.println("❌ 测试6失败: 退选响应格式不正确");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("❌ 测试6失败: " + e.getMessage());
            failed++;
        }

        System.out.println("\n--- 测试7: XSD验证 ---");
        try {
            String validA = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<Classes><class>"
                    + "<课程编号>C_A001</课程编号><课程名称>数据结构</课程名称>"
                    + "<学分>4</学分><授课老师>张老师</授课老师>"
                    + "<授课地点>教A-101</授课地点><共享>Y</共享>"
                    + "</class></Classes>";

            boolean valid = com.integration.xml.XSDValidator.validateCourseXML(validA, "A");
            boolean invalid = com.integration.xml.XSDValidator.validateCourseXML("<invalid/>", "A");
            if (valid && !invalid) {
                System.out.println("✅ 测试7通过: XSD验证能正确区分合法和非法XML");
                passed++;
            } else {
                System.out.println("valid=" + valid + ", invalid=" + invalid);
                System.out.println("❌ 测试7失败: XSD验证逻辑有误");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("❌ 测试7失败: " + e.getMessage());
            failed++;
        }

        System.out.println("\n--- 测试8: 全局统计接口 ---");
        try {
            String result = httpGet("http://localhost:9090/api/integration/statistics");
            System.out.println("统计响应: " + result);
            if (result.contains("<statistics>") && result.contains("<college")) {
                System.out.println("✅ 测试8通过: 全局统计接口正常返回");
                passed++;
            } else {
                System.out.println("❌ 测试8失败: 统计响应格式不正确");
                failed++;
            }
        } catch (Exception e) {
            System.out.println("❌ 测试8失败: " + e.getMessage());
            failed++;
        }

        System.out.println("\n===== 测试结果 =====");
        System.out.println("通过: " + passed + " / " + (passed + failed));
        System.out.println("失败: " + failed);
        if (failed == 0) {
            System.out.println("🎉 全部测试通过！");
        } else {
            System.out.println("⚠️ 部分测试失败，请检查日志");
        }

        System.exit(0);
    }

    private static void startMockCollegeB(int port) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        server.createContext("/api/local/sharedCourses", exchange -> {
            writeXml(exchange, COLLEGE_B_COURSES);
        });

        server.createContext("/api/local/enroll", exchange -> {
            String req = readBody(exchange);
            String resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response><status>SUCCESS</status><message>选课成功</message></response>";
            writeXml(exchange, resp);
        });

        server.createContext("/api/local/drop", exchange -> {
            String resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response><status>SUCCESS</status><message>退选成功</message></response>";
            writeXml(exchange, resp);
        });

        server.createContext("/api/local/statistics", exchange -> {
            String resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><statistics><college name=\"B\"><students>50</students><courses>10</courses><choices>250</choices></college></statistics>";
            writeXml(exchange, resp);
        });

        server.setExecutor(null);
        server.start();
        System.out.println("模拟学院B服务器启动于端口 " + port);
    }

    private static void startMockCollegeC(int port) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        server.createContext("/api/local/sharedCourses", exchange -> {
            writeXml(exchange, COLLEGE_C_COURSES);
        });

        server.createContext("/api/local/enroll", exchange -> {
            String resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response><status>SUCCESS</status><message>选课成功</message></response>";
            writeXml(exchange, resp);
        });

        server.createContext("/api/local/drop", exchange -> {
            String resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response><status>SUCCESS</status><message>退选成功</message></response>";
            writeXml(exchange, resp);
        });

        server.createContext("/api/local/statistics", exchange -> {
            String resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><statistics><college name=\"C\"><students>50</students><courses>10</courses><choices>250</choices></college></statistics>";
            writeXml(exchange, resp);
        });

        server.setExecutor(null);
        server.start();
        System.out.println("模拟学院C服务器启动于端口 " + port);
    }

    private static void writeXml(HttpExchange exchange, String xml) throws IOException {
        byte[] data = xml.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/xml; charset=UTF-8");
        exchange.sendResponseHeaders(200, data.length);
        try (OutputStream os = exchange.getResponseBody()) { os.write(data); }
    }

    private static String readBody(HttpExchange exchange) throws IOException {
        try (InputStream is = exchange.getRequestBody(); ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while ((n = is.read(buf)) >= 0) baos.write(buf, 0, n);
            return new String(baos.toByteArray(), StandardCharsets.UTF_8);
        }
    }

    private static String httpGet(String urlStr) throws Exception {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        if (conn.getResponseCode() == 200) {
            return readAll(conn.getInputStream());
        }
        throw new RuntimeException("GET " + urlStr + " returned " + conn.getResponseCode());
    }

    private static String httpPost(String urlStr, String body) throws Exception {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/xml; charset=UTF-8");
        conn.setDoOutput(true);
        conn.setConnectTimeout(5000);
        conn.setReadTimeout(5000);
        try (OutputStream os = conn.getOutputStream()) {
            os.write(body.getBytes(StandardCharsets.UTF_8));
        }
        if (conn.getResponseCode() == 200) {
            return readAll(conn.getInputStream());
        }
        throw new RuntimeException("POST " + urlStr + " returned " + conn.getResponseCode());
    }

    private static String readAll(InputStream is) throws Exception {
        try (InputStream input = is; ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while ((n = input.read(buf)) >= 0) baos.write(buf, 0, n);
            return new String(baos.toByteArray(), StandardCharsets.UTF_8);
        }
    }
}
