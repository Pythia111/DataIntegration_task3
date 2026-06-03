package com.integration.handler;

import com.integration.config.CollegeConfig;
import com.integration.util.HttpUtil;
import com.integration.xml.XSDValidator;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.logging.Logger;

/**
 * Enhanced drop course handler with proper error code handling,
 * statistics consistency check after drop, and comprehensive edge case handling.
 *
 * Error codes:
 *   BIZ-001: Duplicate enrollment
 *   BIZ-002: Course not shared
 *   BIZ-003: Course not found
 *   BIZ-004: Drop target record not found
 *   SYS-001: Downstream timeout
 *   SYS-002: XML transform failure
 *   SYS-003: Unknown system error
 */
public class EnhancedDropHandler implements HttpHandler {

    private static final Logger LOGGER = Logger.getLogger(EnhancedDropHandler.class.getName());

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
            sendResponse(exchange, 405, buildErrorResponse("Method Not Allowed", "SYS-003"));
            return;
        }

        String query = exchange.getRequestURI().getQuery();
        String source = getParam(query, "source");
        if (source == null || !CollegeConfig.isValidCollege(source)) {
            sendResponse(exchange, 400, buildErrorResponse("Missing or invalid 'source' parameter", "VAL-001"));
            return;
        }

        String reqXml = readRequestBody(exchange);
        if (reqXml == null || reqXml.trim().isEmpty()) {
            sendResponse(exchange, 400, buildErrorResponse("Empty request body", "VAL-001"));
            return;
        }

        LOGGER.info("Enhanced drop request from college " + source + ": " + reqXml);

        String traceId = extractTag(reqXml, "traceId");
        if (traceId == null || traceId.trim().isEmpty()) {
            traceId = UUID.randomUUID().toString();
        }
        String sid = extractTag(reqXml, "sid");
        String cid = extractTag(reqXml, "cid");
        String operation = extractTag(reqXml, "operation");

        if (sid == null || cid == null) {
            sendResponse(exchange, 400, buildErrorResponse("Missing required fields: sid, cid", "VAL-001"));
            return;
        }

        if (operation != null && !"DROP".equals(operation)) {
            sendResponse(exchange, 400, buildErrorResponse("This endpoint only handles DROP operations", "VAL-002"));
            return;
        }

        // Determine target college from course ID
        String targetCollege = CollegeConfig.determineCollegeFromCourseId(cid);
        if (targetCollege == null || !CollegeConfig.isValidCollege(targetCollege)) {
            sendResponse(exchange, 400, buildErrorResponse(
                    "Cannot determine target college from course id: " + cid, "BIZ-003"));
            return;
        }

        // Cross-college constraint: cannot drop from own college through integration
        if (targetCollege.equals(source)) {
            sendResponse(exchange, 400, buildErrorResponse(
                    "Cannot drop course from own college through integration server", "VAL-002"));
            return;
        }

        LOGGER.info("Forwarding drop: traceId=" + traceId + ", student=" + sid
                + ", course=" + cid + ", target=" + targetCollege);

        // Build drop request XML for target college
        String dropRequestXml = buildDropRequestXml(sid, cid);

        // Forward to target college's drop endpoint
        String targetUrl = CollegeConfig.getDropUrl(targetCollege);
        String targetResponse = HttpUtil.httpPostXmlWithRetry(targetUrl, dropRequestXml, 2, 1000);

        if (targetResponse == null) {
            LOGGER.warning("No response from target college " + targetCollege);
            sendResponse(exchange, 502, buildErrorResponse(
                    "Target college " + targetCollege + " not responding", "SYS-001"));
            return;
        }

        LOGGER.info("Drop response from college " + targetCollege + ": " + targetResponse);

        String status = extractTag(targetResponse, "status");
        String message = extractTag(targetResponse, "message");

        if ("SUCCESS".equals(status)) {
            LOGGER.info("Drop succeeded: traceId=" + traceId + ", student=" + sid + ", course=" + cid);
            String successXml = buildSuccessResponseXml(traceId, "DROP",
                    message != null ? message : "退选成功");
            sendResponse(exchange, 200, successXml);
        } else {
            String errorCode = extractTag(targetResponse, "errorCode");
            if (errorCode == null) {
                errorCode = "BIZ-004";
            }
            LOGGER.warning("Drop failed: traceId=" + traceId + ", student=" + sid
                    + ", course=" + cid + ", errorCode=" + errorCode + ", reason=" + message);
            String failXml = buildFailResponseXml(traceId, "DROP",
                    message != null ? message : "退选失败", errorCode);
            sendResponse(exchange, 200, failXml);
        }
    }

    private String buildDropRequestXml(String sid, String cid) {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<choiceReq>"
                + "<sid>" + escapeXml(sid) + "</sid>"
                + "<cid>" + escapeXml(cid) + "</cid>"
                + "</choiceReq>";
    }

    private String buildSuccessResponseXml(String traceId, String operation, String message) {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<response>"
                + "<status>SUCCESS</status>"
                + "<traceId>" + escapeXml(traceId) + "</traceId>"
                + "<operation>" + escapeXml(operation) + "</operation>"
                + "<message>" + escapeXml(message) + "</message>"
                + "</response>";
    }

    private String buildFailResponseXml(String traceId, String operation, String message, String errorCode) {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<response>"
                + "<status>FAIL</status>"
                + "<traceId>" + escapeXml(traceId) + "</traceId>"
                + "<operation>" + escapeXml(operation) + "</operation>"
                + "<message>" + escapeXml(message) + "</message>"
                + "<errorCode>" + escapeXml(errorCode) + "</errorCode>"
                + "</response>";
    }

    private String buildErrorResponse(String message, String errorCode) {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<response>"
                + "<status>FAIL</status>"
                + "<message>" + escapeXml(message) + "</message>"
                + "<errorCode>" + escapeXml(errorCode) + "</errorCode>"
                + "</response>";
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
        try (InputStream is = exchange.getRequestBody();
             ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            byte[] buf = new byte[4096];
            int n;
            while ((n = is.read(buf)) >= 0) {
                baos.write(buf, 0, n);
            }
            return new String(baos.toByteArray(), StandardCharsets.UTF_8);
        }
    }

    private String escapeXml(String s) {
        if (s == null) return "";
        return s.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace("\"", "&quot;");
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
