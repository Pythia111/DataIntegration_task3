package com.integration.config;

import java.util.HashMap;
import java.util.Map;

public class CollegeConfig {

    private static final String DEFAULT_HOST = "localhost";
    private static final int DEFAULT_PORT_A = 8081;
    private static final int DEFAULT_PORT_B = 8082;
    private static final int DEFAULT_PORT_C = 8083;

    private static final Map<String, String> COLLEGE_URLS = new HashMap<>();
    private static final Map<String, Integer> COLLEGE_PORTS = new HashMap<>();

    static {
        COLLEGE_URLS.put("A", resolveUrl("A", DEFAULT_PORT_A));
        COLLEGE_URLS.put("B", resolveUrl("B", DEFAULT_PORT_B));
        COLLEGE_URLS.put("C", resolveUrl("C", DEFAULT_PORT_C));
        COLLEGE_PORTS.put("A", resolveInt("integration.college.A.port", DEFAULT_PORT_A));
        COLLEGE_PORTS.put("B", resolveInt("integration.college.B.port", DEFAULT_PORT_B));
        COLLEGE_PORTS.put("C", resolveInt("integration.college.C.port", DEFAULT_PORT_C));
    }

    /** Resolve base URL: system property > default. */
    private static String resolveUrl(String college, int defaultPort) {
        String key = "integration.college." + college + ".url";
        String prop = System.getProperty(key);
        if (prop != null && !prop.trim().isEmpty()) {
            return prop.trim();
        }
        String host = System.getProperty("integration.college.host", DEFAULT_HOST);
        int port = resolveInt("integration.college." + college + ".port", defaultPort);
        return "http://" + host + ":" + port;
    }

    private static int resolveInt(String key, int defaultValue) {
        String prop = System.getProperty(key);
        if (prop != null && !prop.trim().isEmpty()) {
            try {
                return Integer.parseInt(prop.trim());
            } catch (NumberFormatException ignored) {}
        }
        return defaultValue;
    }

    public static String getBaseUrl(String college) {
        return COLLEGE_URLS.get(college);
    }

    public static String getSharedCoursesUrl(String college) {
        return COLLEGE_URLS.get(college) + "/api/local/sharedCourses";
    }

    public static String getEnrollUrl(String college) {
        return COLLEGE_URLS.get(college) + "/api/local/enroll";
    }

    public static String getDropUrl(String college) {
        return COLLEGE_URLS.get(college) + "/api/local/drop";
    }

    public static String getStatisticsUrl(String college) {
        return COLLEGE_URLS.get(college) + "/api/local/statistics";
    }

    public static boolean isValidCollege(String college) {
        return COLLEGE_URLS.containsKey(college);
    }

    public static String[] getAllColleges() {
        return new String[]{"A", "B", "C"};
    }

    public static String[] getOtherColleges(String source) {
        if ("A".equals(source)) return new String[]{"B", "C"};
        if ("B".equals(source)) return new String[]{"A", "C"};
        if ("C".equals(source)) return new String[]{"A", "B"};
        return new String[]{"A", "B", "C"};
    }

    /** Allow tests to override the base URL for a college. */
    public static void setBaseUrl(String college, String baseUrl) {
        COLLEGE_URLS.put(college, baseUrl);
        try {
            java.net.URL url = new java.net.URL(baseUrl);
            COLLEGE_PORTS.put(college, url.getPort());
        } catch (Exception ignored) {}
    }

    /** Reset URLs to defaults (based on current system properties). */
    public static void resetDefaults() {
        COLLEGE_URLS.put("A", resolveUrl("A", DEFAULT_PORT_A));
        COLLEGE_URLS.put("B", resolveUrl("B", DEFAULT_PORT_B));
        COLLEGE_URLS.put("C", resolveUrl("C", DEFAULT_PORT_C));
        COLLEGE_PORTS.put("A", resolveInt("integration.college.A.port", DEFAULT_PORT_A));
        COLLEGE_PORTS.put("B", resolveInt("integration.college.B.port", DEFAULT_PORT_B));
        COLLEGE_PORTS.put("C", resolveInt("integration.college.C.port", DEFAULT_PORT_C));
    }

    /**
     * Determine target college from course ID prefix.
     */
    public static String determineCollegeFromCourseId(String courseId) {
        if (courseId == null) return null;
        String upper = courseId.toUpperCase();
        if (upper.startsWith("C_A") || upper.startsWith("A")) return "A";
        if (upper.startsWith("B")) return "B";
        if (upper.startsWith("C")) return "C";
        return null;
    }
}
