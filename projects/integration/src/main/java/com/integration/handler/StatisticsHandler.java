package com.integration.handler;

import com.integration.service.StatisticsService;
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

        String statisticsXml = StatisticsService.buildGlobalStatisticsXml();
        sendResponse(exchange, 200, statisticsXml);
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
