package com.integration.handler;

import com.integration.config.CollegeConfig;
import com.integration.util.HttpUtil;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.logging.Logger;

public class StatisticsHandler implements HttpHandler {

    private static final Logger LOGGER = Logger.getLogger(StatisticsHandler.class.getName());

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
            sendResponse(exchange, 405, "<error>Method Not Allowed</error>");
            return;
        }

        LOGGER.info("Received statistics request");

        StringBuilder sb = new StringBuilder();
        sb.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        sb.append("<statistics>");

        for (String college : CollegeConfig.getAllColleges()) {
            try {
                String url = CollegeConfig.getStatisticsUrl(college);
                String resp = HttpUtil.httpGet(url);
                if (resp != null && !resp.trim().isEmpty()) {
                    int start = resp.indexOf("<college ");
                    int end = resp.indexOf("</college>");
                    if (start >= 0 && end > start) {
                        String collegeXml = resp.substring(start, end + "</college>".length());
                        sb.append(collegeXml);
                    } else {
                        sb.append("<college name=\"").append(college).append("\">")
                                .append("<error>Invalid response format</error>")
                                .append("</college>");
                    }
                } else {
                    sb.append("<college name=\"").append(college).append("\">")
                            .append("<error>Not available</error>")
                            .append("</college>");
                }
            } catch (Exception e) {
                LOGGER.warning("Error getting statistics from college " + college + ": " + e.getMessage());
                sb.append("<college name=\"").append(college).append("\">")
                        .append("<error>").append(e.getMessage()).append("</error>")
                        .append("</college>");
            }
        }

        sb.append("</statistics>");
        sendResponse(exchange, 200, sb.toString());
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
