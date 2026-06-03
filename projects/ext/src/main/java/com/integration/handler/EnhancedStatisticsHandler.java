package com.integration.handler;

import com.integration.service.StatisticsService;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.logging.Logger;

/**
 * Enhanced statistics handler that returns properly aggregated global statistics
 * with totals, summary, and timestamp, validated against statistics.xsd.
 *
 * Replaces or complements the basic StatisticsHandler from member5.
 */
public class EnhancedStatisticsHandler implements HttpHandler {

    private static final Logger LOGGER = Logger.getLogger(EnhancedStatisticsHandler.class.getName());

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
            sendResponse(exchange, 405, buildErrorXml("Method Not Allowed"));
            return;
        }

        LOGGER.info("Enhanced statistics request received");
        String statisticsXml = StatisticsService.buildGlobalStatisticsXml();
        sendResponse(exchange, 200, statisticsXml);
    }

    private String buildErrorXml(String message) {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<error>" + escapeXml(message) + "</error>";
    }

    private String escapeXml(String s) {
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
