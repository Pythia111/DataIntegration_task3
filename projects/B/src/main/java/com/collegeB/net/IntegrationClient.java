package com.collegeB.net;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public class IntegrationClient {

    private static final String INTEGRATION_SERVER_URL = "http://localhost:8080";

    public static String getSharedCoursesFromOtherColleges() {
        try {
            URL url = new URL(INTEGRATION_SERVER_URL + "/api/integration/sharedCourses?source=B");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(10000);
            conn.setReadTimeout(10000);

            if (conn.getResponseCode() == 200) {
                return readAll(conn.getInputStream());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public static String sendEnrollOrDropRequest(String xmlPayload) {
        try {
            URL url = new URL(INTEGRATION_SERVER_URL + "/api/integration/courseChoice?source=B");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/xml");
            conn.setDoOutput(true);
            conn.setConnectTimeout(10000);
            conn.setReadTimeout(10000);

            try (OutputStream os = conn.getOutputStream()) {
                byte[] input = xmlPayload.getBytes(StandardCharsets.UTF_8);
                os.write(input, 0, input.length);
            }

            if (conn.getResponseCode() == 200) {
                return readAll(conn.getInputStream());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public static String getGlobalStatistics() {
        try {
            URL url = new URL(INTEGRATION_SERVER_URL + "/api/integration/statistics");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setConnectTimeout(10000);
            conn.setReadTimeout(10000);

            if (conn.getResponseCode() == 200) {
                return readAll(conn.getInputStream());
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
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
