package com.integration.config;

import java.util.HashMap;
import java.util.Map;

public class CollegeConfig {

    private static final Map<String, String> COLLEGE_URLS = new HashMap<>();
    private static final Map<String, Integer> COLLEGE_PORTS = new HashMap<>();

    static {
        COLLEGE_URLS.put("A", "http://localhost:8081");
        COLLEGE_URLS.put("B", "http://localhost:8082");
        COLLEGE_URLS.put("C", "http://localhost:8083");
        COLLEGE_PORTS.put("A", 8081);
        COLLEGE_PORTS.put("B", 8082);
        COLLEGE_PORTS.put("C", 8083);
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
}
