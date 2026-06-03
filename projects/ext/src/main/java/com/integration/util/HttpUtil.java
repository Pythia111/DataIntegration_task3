package com.integration.util;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.SocketTimeoutException;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.logging.Logger;

public class HttpUtil {

    private static final Logger LOGGER = Logger.getLogger(HttpUtil.class.getName());

    /**
     * HTTP GET with configurable timeout.
     */
    public static String httpGet(String urlStr) {
        return httpGet(urlStr, 10000, 10000);
    }

    public static String httpGet(String urlStr, int connectTimeout, int readTimeout) {
        try {
            URL url = new URL(urlStr);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(connectTimeout);
            conn.setReadTimeout(readTimeout);
            conn.setRequestProperty("Accept", "application/xml");

            int code = conn.getResponseCode();
            if (code == 200) {
                return readAll(conn.getInputStream());
            } else {
                LOGGER.warning("GET " + urlStr + " returned HTTP " + code);
                return null;
            }
        } catch (Exception e) {
            LOGGER.warning("GET " + urlStr + " failed: " + e.getMessage());
            return null;
        }
    }

    /**
     * HTTP GET with automatic retry on failure.
     */
    public static String httpGetWithRetry(String urlStr, int maxRetries, long retryDelayMs) {
        Exception lastException = null;
        for (int attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                URL url = new URL(urlStr);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(10000);
                conn.setReadTimeout(10000);
                conn.setRequestProperty("Accept", "application/xml");

                int code = conn.getResponseCode();
                if (code == 200) {
                    return readAll(conn.getInputStream());
                } else {
                    LOGGER.warning("GET " + urlStr + " returned HTTP " + code + " (attempt " + attempt + "/" + maxRetries + ")");
                    lastException = new RuntimeException("HTTP " + code);
                }
            } catch (SocketTimeoutException e) {
                lastException = e;
                LOGGER.warning("GET " + urlStr + " timeout (attempt " + attempt + "/" + maxRetries + "): " + e.getMessage());
            } catch (Exception e) {
                lastException = e;
                LOGGER.warning("GET " + urlStr + " failed (attempt " + attempt + "/" + maxRetries + "): " + e.getMessage());
            }

            if (attempt < maxRetries) {
                try { Thread.sleep(retryDelayMs); } catch (InterruptedException ignored) {}
            }
        }
        LOGGER.severe("GET " + urlStr + " exhausted all " + maxRetries + " retries: "
                + (lastException != null ? lastException.getMessage() : "unknown error"));
        return null;
    }

    /**
     * HTTP POST with XML body and configurable timeout.
     */
    public static String httpPostXml(String urlStr, String xmlBody) {
        return httpPostXml(urlStr, xmlBody, 10000, 10000);
    }

    public static String httpPostXml(String urlStr, String xmlBody, int connectTimeout, int readTimeout) {
        try {
            URL url = new URL(urlStr);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/xml; charset=UTF-8");
            conn.setRequestProperty("Accept", "application/xml");
            conn.setDoOutput(true);
            conn.setConnectTimeout(connectTimeout);
            conn.setReadTimeout(readTimeout);

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = xmlBody.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            int code = conn.getResponseCode();
            InputStream is = (code >= 200 && code < 300) ? conn.getInputStream() : conn.getErrorStream();
            if (is != null) {
                return readAll(is);
            }
            return null;
        } catch (Exception e) {
            LOGGER.warning("POST " + urlStr + " failed: " + e.getMessage());
            return null;
        }
    }

    /**
     * HTTP POST with retry mechanism.
     */
    public static String httpPostXmlWithRetry(String urlStr, String xmlBody, int maxRetries, long retryDelayMs) {
        Exception lastException = null;
        for (int attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                URL url = new URL(urlStr);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/xml; charset=UTF-8");
                conn.setRequestProperty("Accept", "application/xml");
                conn.setDoOutput(true);
                conn.setConnectTimeout(10000);
                conn.setReadTimeout(10000);

                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = xmlBody.getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                }

                int code = conn.getResponseCode();
                InputStream is = (code >= 200 && code < 300) ? conn.getInputStream() : conn.getErrorStream();
                if (is != null) {
                    return readAll(is);
                }
                lastException = new RuntimeException("HTTP " + code + " with no body");
            } catch (SocketTimeoutException e) {
                lastException = e;
                LOGGER.warning("POST " + urlStr + " timeout (attempt " + attempt + "/" + maxRetries + "): " + e.getMessage());
            } catch (Exception e) {
                lastException = e;
                LOGGER.warning("POST " + urlStr + " failed (attempt " + attempt + "/" + maxRetries + "): " + e.getMessage());
            }

            if (attempt < maxRetries) {
                try { Thread.sleep(retryDelayMs); } catch (InterruptedException ignored) {}
            }
        }
        LOGGER.severe("POST " + urlStr + " exhausted all " + maxRetries + " retries: "
                + (lastException != null ? lastException.getMessage() : "unknown error"));
        return null;
    }

    private static String readAll(InputStream is) throws Exception {
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
