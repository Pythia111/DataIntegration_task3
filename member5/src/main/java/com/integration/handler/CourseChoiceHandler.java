package com.integration.handler;

import com.integration.config.CollegeConfig;
import com.integration.util.HttpUtil;
import com.integration.xml.XSDValidator;
import com.integration.xml.XSLTTransformer;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import org.dom4j.Document;
import org.dom4j.DocumentHelper;
import org.dom4j.Element;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.SAXReader;
import org.dom4j.io.XMLWriter;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.StringReader;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.util.logging.Logger;

public class CourseChoiceHandler implements HttpHandler {

    private static final Logger LOGGER = Logger.getLogger(CourseChoiceHandler.class.getName());

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
            sendResponse(exchange, 405, buildResponseXml("FAIL", "Method Not Allowed"));
            return;
        }

        String query = exchange.getRequestURI().getQuery();
        String source = getParam(query, "source");
        if (source == null || !CollegeConfig.isValidCollege(source)) {
            sendResponse(exchange, 400, buildResponseXml("FAIL", "Missing or invalid 'source' parameter"));
            return;
        }

        String reqXml = readRequestBody(exchange);
        if (reqXml == null || reqXml.trim().isEmpty()) {
            sendResponse(exchange, 400, buildResponseXml("FAIL", "Empty request body"));
            return;
        }

        LOGGER.info("Received courseChoice request from college " + source + ": " + reqXml);

        boolean validReq = XSDValidator.validateChoiceRequest(reqXml);
        if (!validReq) {
            LOGGER.warning("Choice request XSD validation failed");
        }

        String traceId = extractTag(reqXml, "traceId");
        String sid = extractTag(reqXml, "sid");
        String cid = extractTag(reqXml, "cid");
        String operation = extractTag(reqXml, "operation");

        if (sid == null || cid == null || operation == null) {
            sendResponse(exchange, 400, buildResponseXml("FAIL", "Missing required fields: sid, cid, operation"));
            return;
        }

        if (!"ENROLL".equals(operation) && !"DROP".equals(operation)) {
            sendResponse(exchange, 400, buildResponseXml("FAIL", "Invalid operation: " + operation + ". Use ENROLL or DROP."));
            return;
        }

        String targetCollege = determineTargetCollege(cid);
        if (targetCollege == null || !CollegeConfig.isValidCollege(targetCollege)) {
            sendResponse(exchange, 400, buildResponseXml("FAIL", "Cannot determine target college from course id: " + cid));
            return;
        }

        if (targetCollege.equals(source)) {
            sendResponse(exchange, 400, buildResponseXml("FAIL", "Cannot " + operation.toLowerCase() + " course from own college through integration server"));
            return;
        }

        LOGGER.info("Forwarding " + operation + " request: student=" + sid + ", course=" + cid + ", target=" + targetCollege);

        String localReqXml = buildLocalEnrollDropXml(sid, cid);
        String targetUrl;

        if ("ENROLL".equals(operation)) {
            targetUrl = CollegeConfig.getEnrollUrl(targetCollege);
        } else {
            targetUrl = CollegeConfig.getDropUrl(targetCollege);
        }

        String targetResponse = HttpUtil.httpPostXml(targetUrl, localReqXml);

        if (targetResponse == null) {
            LOGGER.warning("No response from target college " + targetCollege);
            sendResponse(exchange, 502, buildResponseXml("FAIL", "Target college " + targetCollege + " not responding"));
            return;
        }

        LOGGER.info("Response from college " + targetCollege + ": " + targetResponse);

        String status = extractTag(targetResponse, "status");
        String message = extractTag(targetResponse, "message");

        if ("SUCCESS".equals(status)) {
            LOGGER.info(operation + " succeeded: student=" + sid + ", course=" + cid);
            sendResponse(exchange, 200, buildResponseXml("SUCCESS", message != null ? message : operation + " succeeded"));
        } else {
            LOGGER.warning(operation + " failed: student=" + sid + ", course=" + cid + ", reason=" + message);
            sendResponse(exchange, 200, buildResponseXml("FAIL", message != null ? message : operation + " failed"));
        }
    }

    private String determineTargetCollege(String courseId) {
        if (courseId == null) return null;
        String upper = courseId.toUpperCase();
        if (upper.startsWith("C_A") || upper.startsWith("A")) return "A";
        if (upper.startsWith("B")) return "B";
        if (upper.startsWith("C")) return "C";
        return null;
    }

    private String buildLocalEnrollDropXml(String sid, String cid) {
        try {
            Document doc = DocumentHelper.createDocument();
            Element root = doc.addElement("choiceReq");
            root.addElement("sid").setText(sid);
            root.addElement("cid").setText(cid);
            StringWriter sw = new StringWriter();
            OutputFormat format = OutputFormat.createPrettyPrint();
            format.setEncoding("UTF-8");
            XMLWriter writer = new XMLWriter(sw, format);
            writer.write(doc);
            return sw.toString();
        } catch (Exception e) {
            return "<choiceReq><sid>" + sid + "</sid><cid>" + cid + "</cid></choiceReq>";
        }
    }

    private String buildResponseXml(String status, String message) {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<response><status>"
                + status + "</status><message>" + (message != null ? message : "")
                + "</message></response>";
    }

    private String extractTag(String xml, String tagName) {
        String startTag = "<" + tagName + ">";
        String endTag = "</" + tagName + ">";
        int start = xml.indexOf(startTag);
        int end = xml.indexOf(endTag);
        if (start >= 0 && end > start) {
            return xml.substring(start + startTag.length(), end);
        }
        return null;
    }

    private String getParam(String query, String name) {
        if (query == null) return null;
        for (String param : query.split("&")) {
            String[] kv = param.split("=", 2);
            if (kv.length == 2 && kv[0].equals(name)) {
                return kv[1];
            }
        }
        return null;
    }

    private String readRequestBody(HttpExchange exchange) throws IOException {
        try (InputStream is = exchange.getRequestBody(); ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while ((n = is.read(buf)) >= 0) {
                baos.write(buf, 0, n);
            }
            return new String(baos.toByteArray(), StandardCharsets.UTF_8);
        }
    }

    private void sendResponse(HttpExchange exchange, int statusCode, String xml) throws IOException {
        byte[] response = xml.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/xml; charset=UTF-8");
        exchange.sendResponseHeaders(statusCode, response.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(response);
        }
    }
}
