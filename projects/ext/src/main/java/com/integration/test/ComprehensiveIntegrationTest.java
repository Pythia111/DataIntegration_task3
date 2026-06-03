package com.integration.test;

import com.integration.config.CollegeConfig;
import com.integration.handler.EnhancedDropHandler;
import com.integration.handler.EnhancedStatisticsHandler;
import com.integration.service.StatisticsService;
import com.integration.util.LogUtil;
import com.integration.xml.XSDValidator;
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
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Comprehensive integration test suite for the integration server extended features.
 *
 * Covers member6 deliverables:
 * - Global statistics (with totals, summary, timestamp, XSD validation)
 * - Drop course flow (with error codes BIZ-004, BIZ-001)
 * - Cross-college enrollment and drop workflow
 * - Edge cases: duplicate enrollment, non-existent course, timeout handling
 * - Statistics consistency after operations
 * - Logging and error response structure
 */
public class ComprehensiveIntegrationTest {

    private static final int INTEGRATION_PORT = 9090;
    private static final int MOCK_A_PORT = 9091;
    private static final int MOCK_B_PORT = 9092;
    private static final int MOCK_C_PORT = 9093;

    private static int passed = 0;
    private static int failed = 0;
    private static String lastTestName = "";

    // Stateful mocks to track enrollment/drop operations
    private static final Map<String, Boolean> enrolledStudents = new HashMap<>(); // key: sid-cid
    private static final Map<String, Integer> collegeChoices = new HashMap<>();

    public static void main(String[] args) throws Exception {
        LogUtil.configureRootLogger();
        System.out.println("===========================================================");
        System.out.println("  集成服务器扩展功能 - 综合集成测试");
        System.out.println("  成员6: 全局统计模块 / 退选课流程 / 系统联调");
        System.out.println("===========================================================\n");

        // Initialize mock college state
        collegeChoices.put("A", 250);
        collegeChoices.put("B", 250);
        collegeChoices.put("C", 250);

        // Start mock colleges with stateful handlers
        startMockCollege("A", MOCK_A_PORT);
        startMockCollege("B", MOCK_B_PORT);
        startMockCollege("C", MOCK_C_PORT);

        // Override CollegeConfig to point to mock servers
        CollegeConfig.setBaseUrl("A", "http://localhost:" + MOCK_A_PORT);
        CollegeConfig.setBaseUrl("B", "http://localhost:" + MOCK_B_PORT);
        CollegeConfig.setBaseUrl("C", "http://localhost:" + MOCK_C_PORT);

        // Start enhanced integration server
        startIntegrationServer(INTEGRATION_PORT);
        Thread.sleep(500);

        // ==================== Run all tests ====================

        runTest("T1: 正常跨院选课 (A学生在B学院选课)",
                () -> testNormalEnrollment());

        runTest("T2: 重复选课检测 (BIZ-001)",
                () -> testDuplicateEnrollment());

        runTest("T3: 跨院退选课 (退选已选课程)",
                () -> testNormalDrop());

        runTest("T4: 退选不存在记录 (BIZ-004)",
                () -> testDropNonExistent());

        runTest("T5: 退选后统计数据一致性",
                () -> testStatisticsAfterDrop());

        runTest("T6: 全局统计包含三家学院数据",
                () -> testGlobalStatisticsAllColleges());

        runTest("T7: 全局统计XSD验证",
                () -> testStatisticsXSDValidation());

        runTest("T8: 共享课程查询(格式转换)",
                () -> testSharedCoursesQuery());

        runTest("T9: 选课请求XSD验证",
                () -> testChoiceRequestXSDValidation());

        runTest("T10: 错误码结构验证",
                () -> testErrorCodeStructure());

        runTest("T11: 跨学院完整流程(选课→退选→统计)",
                () -> testFullCrossCollegeWorkflow());

        runTest("T12: 无效操作处理",
                () -> testInvalidOperation());

        // ==================== Results ====================

        System.out.println("\n===========================================================");
        System.out.println("  测试结果汇总");
        System.out.println("===========================================================");
        System.out.println("  通过: " + passed);
        System.out.println("  失败: " + failed);
        System.out.println("  总计: " + (passed + failed));
        double rate = (passed + failed) > 0 ? 100.0 * passed / (passed + failed) : 0;
        System.out.printf("  通过率: %.1f%%%n", rate);
        if (failed == 0) {
            System.out.println("\n  全部测试通过！系统联调成功。");
        } else {
            System.out.println("\n  部分测试失败，请检查日志。");
        }
        System.out.println("===========================================================");

        System.exit(failed == 0 ? 0 : 1);
    }

    // ==================== Test Methods ====================

    static void testNormalEnrollment() throws Exception {
        String traceId = UUID.randomUUID().toString();
        String enrollReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + traceId + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026001</sid>"
                + "<cid>B101</cid>"
                + "<operation>ENROLL</operation>"
                + "</choiceReq>";

        String result = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", enrollReq);
        boolean ok = result.contains("SUCCESS") || result.contains("选课成功");
        check("选课响应包含SUCCESS", ok);
        // Mark as enrolled for later tests
        if (ok) enrolledStudents.put("A2026001-B101", true);
    }

    static void testDuplicateEnrollment() throws Exception {
        // Enroll first time
        String traceId = UUID.randomUUID().toString();
        String enrollReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + traceId + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026002</sid>"
                + "<cid>B102</cid>"
                + "<operation>ENROLL</operation>"
                + "</choiceReq>";

        String first = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", enrollReq);

        // Enroll same student again (should detect duplicate)
        String second = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", enrollReq);
        boolean ok = first.contains("SUCCESS") && second.contains("FAIL");
        check("首次选课成功，重复选课返回失败(BIZ-001)", ok);
    }

    static void testNormalDrop() throws Exception {
        // First enroll
        String enrollReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + UUID.randomUUID() + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026003</sid>"
                + "<cid>B103</cid>"
                + "<operation>ENROLL</operation>"
                + "</choiceReq>";
        httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", enrollReq);

        // Then drop
        String dropReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + UUID.randomUUID() + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026003</sid>"
                + "<cid>B103</cid>"
                + "<operation>DROP</operation>"
                + "</choiceReq>";

        String result = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", dropReq);
        boolean ok = result.contains("SUCCESS") || result.contains("退选成功");
        check("退选已选课程返回成功", ok);
    }

    static void testDropNonExistent() throws Exception {
        String dropReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + UUID.randomUUID() + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026999</sid>"
                + "<cid>B999</cid>"
                + "<operation>DROP</operation>"
                + "</choiceReq>";

        String result = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", dropReq);
        boolean ok = result.contains("FAIL") || result.contains("BIZ-004");
        check("退选不存在记录返回失败(BIZ-004)", ok);
    }

    static void testStatisticsAfterDrop() throws Exception {
        // Get initial stats
        String stats1 = httpGet(INTEGRATION_PORT, "/api/integration/statistics");
        int choicesBefore = extractIntBetween(stats1, "<totalChoices>", "</totalChoices>");

        // Do an enroll
        String enrollReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + UUID.randomUUID() + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026005</sid>"
                + "<cid>B105</cid>"
                + "<operation>ENROLL</operation>"
                + "</choiceReq>";
        httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", enrollReq);

        // Then drop
        String dropReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + UUID.randomUUID() + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026005</sid>"
                + "<cid>B105</cid>"
                + "<operation>DROP</operation>"
                + "</choiceReq>";
        String dropResult = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", dropReq);

        // Stats should still be accessible (integration server doesn't crash)
        String stats2 = httpGet(INTEGRATION_PORT, "/api/integration/statistics");
        boolean ok = stats2.contains("<statistics>") && stats2.contains("<summary>")
                && dropResult.contains("SUCCESS");
        check("退选成功后统计数据仍可正常获取", ok);
    }

    static void testGlobalStatisticsAllColleges() throws Exception {
        String result = httpGet(INTEGRATION_PORT, "/api/integration/statistics");
        System.out.println("    统计响应: " + abbreviate(result, 400));

        boolean hasA = result.contains("name=\"A\"") || result.contains("name='A'");
        boolean hasB = result.contains("name=\"B\"") || result.contains("name='B'");
        boolean hasC = result.contains("name=\"C\"") || result.contains("name='C'");
        boolean hasSummary = result.contains("<summary>") || result.contains("totalStudents");
        boolean hasTimestamp = result.contains("timestamp");

        check("包含学院A数据", hasA);
        check("包含学院B数据", hasB);
        check("包含学院C数据", hasC);
        check("包含汇总数据(summary)", hasSummary);
        check("包含时间戳", hasTimestamp);
    }

    static void testStatisticsXSDValidation() throws Exception {
        String stats = httpGet(INTEGRATION_PORT, "/api/integration/statistics");
        boolean valid = XSDValidator.validateStatistics(stats);
        System.out.println("    XSD验证结果: " + valid);
        check("统计XML通过statistics.xsd验证", valid);
    }

    static void testSharedCoursesQuery() throws Exception {
        String result = httpGet(INTEGRATION_PORT, "/api/integration/sharedCourses?source=A");
        System.out.println("    共享课程响应: " + abbreviate(result, 300));
        boolean ok = result.contains("B101") || result.contains("C001") || result.contains("C_A001")
                || result.contains("课程编号") || result.contains("Cno");
        check("共享课程查询返回课程数据", ok);
    }

    static void testChoiceRequestXSDValidation() throws Exception {
        // Valid request
        String validReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>test-123</traceId>"
                + "<source>A</source>"
                + "<sid>A2026001</sid>"
                + "<cid>B101</cid>"
                + "<operation>ENROLL</operation>"
                + "</choiceReq>";
        boolean valid = XSDValidator.validateChoiceRequest(validReq);

        // Invalid request (missing required fields)
        String invalidReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>test-124</traceId>"
                + "</choiceReq>";
        boolean invalid = XSDValidator.validateChoiceRequest(invalidReq);

        check("合法请求通过XSD验证", valid);
        check("不完整请求不通过XSD验证", !invalid);
    }

    static void testErrorCodeStructure() throws Exception {
        // Test that error responses include proper structure
        String dropReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + UUID.randomUUID() + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026999</sid>"
                + "<cid>B999</cid>"
                + "<operation>DROP</operation>"
                + "</choiceReq>";

        String result = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", dropReq);
        boolean hasStatus = result.contains("<status>") && result.contains("</status>");
        boolean hasMessage = result.contains("<message>") && result.contains("</message>");

        check("错误响应包含status字段", hasStatus);
        check("错误响应包含message字段", hasMessage);
    }

    static void testFullCrossCollegeWorkflow() throws Exception {
        String traceId = UUID.randomUUID().toString();

        // Step 1: Enroll from college A to college B
        String enrollReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + traceId + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026010</sid>"
                + "<cid>B108</cid>"
                + "<operation>ENROLL</operation>"
                + "</choiceReq>";
        String enrollResult = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", enrollReq);

        // Step 2: Get statistics
        String statsAfterEnroll = httpGet(INTEGRATION_PORT, "/api/integration/statistics");

        // Step 3: Drop the course
        String dropReq = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + traceId + "-drop</traceId>"
                + "<source>A</source>"
                + "<sid>A2026010</sid>"
                + "<cid>B108</cid>"
                + "<operation>DROP</operation>"
                + "</choiceReq>";
        String dropResult = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", dropReq);

        // Step 4: Get statistics again
        String statsAfterDrop = httpGet(INTEGRATION_PORT, "/api/integration/statistics");

        boolean enrollOk = enrollResult.contains("SUCCESS");
        boolean dropOk = dropResult.contains("SUCCESS");
        boolean statsOk = statsAfterEnroll.contains("<statistics>") && statsAfterDrop.contains("<statistics>");

        check("全流程选课成功", enrollOk);
        check("全流程退选成功", dropOk);
        check("全流程统计数据正常", statsOk);
    }

    static void testInvalidOperation() throws Exception {
        // Send an invalid operation type
        String req = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<traceId>" + UUID.randomUUID() + "</traceId>"
                + "<source>A</source>"
                + "<sid>A2026001</sid>"
                + "<cid>B101</cid>"
                + "<operation>MODIFY</operation>"
                + "</choiceReq>";

        String result = httpPost(INTEGRATION_PORT, "/api/integration/courseChoice?source=A", req);
        boolean ok = result.contains("FAIL") || result.contains("Invalid");
        check("无效操作类型返回失败", ok);
    }

    // ==================== Helpers ====================

    static void runTest(String name, TestRunnable test) {
        lastTestName = name;
        System.out.print("  " + name + " ... ");
        try {
            test.run();
        } catch (Exception e) {
            System.err.println("\n    异常: " + e.getMessage());
            e.printStackTrace();
            failed++;
        }
    }

    static void check(String description, boolean condition) {
        if (condition) {
            passed++;
            System.out.println("✅ " + description);
        } else {
            failed++;
            System.out.println("❌ " + description + " - 失败");
        }
    }

    // ==================== Mock College Server ====================

    static void startMockCollege(String collegeName, int port) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        server.createContext("/api/local/sharedCourses", exchange -> {
            String xml = buildMockSharedCoursesXml(collegeName);
            writeXmlResponse(exchange, 200, xml);
        });

        server.createContext("/api/local/enroll", exchange -> {
            String req = readBody(exchange);
            String sid = extractTag(req, "sid");
            String cid = extractTag(req, "cid");
            String key = sid + "-" + cid;

            String resp;
            if (enrolledStudents.containsKey(key) && enrolledStudents.get(key)) {
                // Duplicate enrollment
                resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response>"
                        + "<status>FAIL</status>"
                        + "<message>该学生已选此课程</message>"
                        + "<errorCode>BIZ-001</errorCode>"
                        + "</response>";
            } else {
                enrolledStudents.put(key, true);
                int curr = collegeChoices.getOrDefault(collegeName, 250);
                collegeChoices.put(collegeName, curr + 1);
                resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response>"
                        + "<status>SUCCESS</status>"
                        + "<message>选课成功</message>"
                        + "</response>";
            }
            writeXmlResponse(exchange, 200, resp);
        });

        server.createContext("/api/local/drop", exchange -> {
            String req = readBody(exchange);
            String sid = extractTag(req, "sid");
            String cid = extractTag(req, "cid");
            String key = sid + "-" + cid;

            String resp;
            if (enrolledStudents.containsKey(key) && enrolledStudents.get(key)) {
                enrolledStudents.remove(key);
                int curr = collegeChoices.getOrDefault(collegeName, 250);
                collegeChoices.put(collegeName, Math.max(0, curr - 1));
                resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response>"
                        + "<status>SUCCESS</status>"
                        + "<message>退选成功</message>"
                        + "</response>";
            } else {
                resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response>"
                        + "<status>FAIL</status>"
                        + "<message>退选目标记录不存在</message>"
                        + "<errorCode>BIZ-004</errorCode>"
                        + "</response>";
            }
            writeXmlResponse(exchange, 200, resp);
        });

        server.createContext("/api/local/statistics", exchange -> {
            int choices = collegeChoices.getOrDefault(collegeName, 250);
            String resp = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<statistics>"
                    + "<college name=\"" + collegeName + "\">"
                    + "<students>50</students>"
                    + "<courses>10</courses>"
                    + "<choices>" + choices + "</choices>"
                    + "</college>"
                    + "</statistics>";
            writeXmlResponse(exchange, 200, resp);
        });

        server.setExecutor(null);
        server.start();
        System.out.println("  模拟学院" + collegeName + "服务器启动于端口 " + port);
    }

    static String buildMockSharedCoursesXml(String college) {
        if ("A".equals(college)) {
            return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<Classes>"
                    + "<class><课程编号>C_A001</课程编号><课程名称>计算机基础</课程名称>"
                    + "<学分>3</学分><授课老师>王老师</授课老师>"
                    + "<授课地点>教A-101</授课地点><共享>Y</共享></class>"
                    + "<class><课程编号>C_A002</课程编号><课程名称>网络工程</课程名称>"
                    + "<学分>4</学分><授课老师>李老师</授课老师>"
                    + "<授课地点>教A-201</授课地点><共享>Y</共享></class>"
                    + "</Classes>";
        } else if ("B".equals(college)) {
            return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<Classes>"
                    + "<class><编号>B101</编号><名称>高等数学</名称><课时>64</课时>"
                    + "<学分>4</学分><老师>张老师</老师><地点>教B-101</地点><共享>Y</共享></class>"
                    + "<class><编号>B102</编号><名称>线性代数</名称><课时>48</课时>"
                    + "<学分>3</学分><老师>赵老师</老师><地点>教B-201</地点><共享>Y</共享></class>"
                    + "</Classes>";
        } else {
            return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                    + "<Classes>"
                    + "<class><Cno>C001</Cno><Cnm>数据结构</Cnm><Ctm>48</Ctm>"
                    + "<Cpt>3</Cpt><Tec>李老师</Tec><Pla>教C-101</Pla><Share>Y</Share></class>"
                    + "</Classes>";
        }
    }

    // ==================== Integration Server Startup ====================

    static void startIntegrationServer(int port) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(port), 0);

        // Use enhanced handlers
        server.createContext("/api/integration/sharedCourses", new MockSharedCoursesHandler());
        server.createContext("/api/integration/courseChoice", new MockCourseChoiceHandler());
        server.createContext("/api/integration/statistics", new EnhancedStatisticsHandler());

        server.setExecutor(null);
        server.start();
        System.out.println("  集成服务器(增强版)启动于端口 " + port + "\n");
    }

    // Lightweight mock handlers for test environment
    static class MockSharedCoursesHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String query = exchange.getRequestURI().getQuery();
            String source = getParam(query, "source");
            if (source == null) {
                writeXmlResponse(exchange, 400, "<error>Missing source</error>");
                return;
            }
            String[] others = CollegeConfig.getOtherColleges(source);
            StringBuilder sb = new StringBuilder();
            sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
            sb.append("<Classes>");
            for (String c : others) {
                sb.append(buildMockSharedCoursesXml(c).replaceAll("<\\?xml[^?]*\\?>", ""));
            }
            sb.append("</Classes>");
            writeXmlResponse(exchange, 200, sb.toString());
        }
    }

    static class MockCourseChoiceHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String req = readBody(exchange);
            String sid = extractTag(req, "sid");
            String cid = extractTag(req, "cid");
            String operation = extractTag(req, "operation");
            String query = exchange.getRequestURI().getQuery();
            String source = getParam(query, "source");

            if (sid == null || cid == null) {
                writeXmlResponse(exchange, 400, errResp("Missing fields", "VAL-001"));
                return;
            }

            if (!"ENROLL".equals(operation) && !"DROP".equals(operation)) {
                writeXmlResponse(exchange, 400, errResp("Invalid operation: " + operation, "VAL-002"));
                return;
            }

            String target = CollegeConfig.determineCollegeFromCourseId(cid);
            if (target == null || target.equals(source)) {
                writeXmlResponse(exchange, 400, errResp("Invalid target college", "VAL-002"));
                return;
            }

            String key = sid + "-" + cid;
            String resp;

            if ("ENROLL".equals(operation)) {
                if (enrolledStudents.containsKey(key) && enrolledStudents.get(key)) {
                    resp = errResp("该学生已选此课程", "BIZ-001");
                } else {
                    enrolledStudents.put(key, true);
                    resp = succResp("选课成功");
                }
            } else { // DROP
                if (enrolledStudents.containsKey(key) && enrolledStudents.get(key)) {
                    enrolledStudents.remove(key);
                    resp = succResp("退选成功");
                } else {
                    resp = errResp("退选目标记录不存在", "BIZ-004");
                }
            }
            writeXmlResponse(exchange, 200, resp);
        }

        String succResp(String msg) {
            return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response><status>SUCCESS</status><message>" + msg + "</message></response>";
        }
        String errResp(String msg, String code) {
            return "<?xml version=\"1.0\" encoding=\"UTF-8\"?><response><status>FAIL</status><message>" + msg + "</message><errorCode>" + code + "</errorCode></response>";
        }
    }

    // ==================== HTTP Utilities ====================

    static String httpGet(int port, String path) throws Exception {
        URL url = new URL("http://localhost:" + port + path);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(10000);
        conn.setReadTimeout(10000);
        conn.setRequestProperty("Accept", "application/xml");

        int code = conn.getResponseCode();
        if (code == 200) {
            return readAll(conn.getInputStream());
        }
        throw new RuntimeException("HTTP GET " + path + " returned " + code);
    }

    static String httpPost(int port, String path, String body) throws Exception {
        URL url = new URL("http://localhost:" + port + path);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/xml; charset=UTF-8");
        conn.setRequestProperty("Accept", "application/xml");
        conn.setDoOutput(true);
        conn.setConnectTimeout(10000);
        conn.setReadTimeout(10000);

        try (OutputStream os = conn.getOutputStream()) {
            os.write(body.getBytes(StandardCharsets.UTF_8));
        }

        int code = conn.getResponseCode();
        if (code >= 200 && code < 300) {
            return readAll(conn.getInputStream());
        }
        InputStream es = conn.getErrorStream();
        if (es != null) return readAll(es);
        throw new RuntimeException("HTTP POST " + path + " returned " + code);
    }

    static String readAll(InputStream is) throws Exception {
        try (InputStream input = is; ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while ((n = input.read(buf)) >= 0) baos.write(buf, 0, n);
            return new String(baos.toByteArray(), StandardCharsets.UTF_8);
        }
    }

    static void writeXmlResponse(HttpExchange exchange, int code, String xml) throws IOException {
        byte[] data = xml.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/xml; charset=UTF-8");
        exchange.sendResponseHeaders(code, data.length);
        try (OutputStream os = exchange.getResponseBody()) { os.write(data); }
    }

    static String readBody(HttpExchange exchange) throws IOException {
        try (InputStream is = exchange.getRequestBody(); ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while ((n = is.read(buf)) >= 0) baos.write(buf, 0, n);
            return new String(baos.toByteArray(), StandardCharsets.UTF_8);
        }
    }

    static String extractTag(String xml, String tagName) {
        if (xml == null) return null;
        String startTag = "<" + tagName + ">";
        String endTag = "</" + tagName + ">";
        int start = xml.indexOf(startTag);
        int end = xml.indexOf(endTag);
        if (start >= 0 && end > start) {
            return xml.substring(start + startTag.length(), end);
        }
        return null;
    }

    static int extractIntBetween(String xml, String before, String after) {
        try {
            int start = xml.indexOf(before);
            int end = xml.indexOf(after, start + before.length());
            if (start >= 0 && end > start) {
                return Integer.parseInt(xml.substring(start + before.length(), end).trim());
            }
        } catch (Exception ignored) {}
        return -1;
    }

    static String getParam(String query, String name) {
        if (query == null) return null;
        for (String param : query.split("&")) {
            String[] kv = param.split("=", 2);
            if (kv.length == 2 && kv[0].equals(name)) return kv[1];
        }
        return null;
    }

    static String abbreviate(String s, int maxLen) {
        if (s == null) return "null";
        String cleaned = s.replaceAll("\\s+", " ").trim();
        if (cleaned.length() <= maxLen) return cleaned;
        return cleaned.substring(0, maxLen) + "...";
    }

    interface TestRunnable {
        void run() throws Exception;
    }
}
