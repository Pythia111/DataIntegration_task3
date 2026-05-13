package com.integration.service;

import com.integration.config.CollegeConfig;
import com.integration.util.HttpUtil;
import com.integration.xml.XSDValidator;
import org.dom4j.Document;
import org.dom4j.DocumentHelper;
import org.dom4j.Element;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.SAXReader;
import org.dom4j.io.XMLWriter;

import java.io.StringReader;
import java.io.StringWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.Logger;

public class StatisticsService {

    private static final Logger LOGGER = Logger.getLogger(StatisticsService.class.getName());

    public static class CollegeStats {
        public String collegeName;
        public int students;
        public int courses;
        public int choices;
        public boolean available;
        public String errorMessage;
    }

    /**
     * Fetch statistics from a single college.
     */
    public static CollegeStats fetchCollegeStats(String college) {
        CollegeStats stats = new CollegeStats();
        stats.collegeName = college;
        stats.available = false;

        try {
            String url = CollegeConfig.getStatisticsUrl(college);
            LOGGER.info("Fetching statistics from college " + college + ": " + url);
            String resp = HttpUtil.httpGetWithRetry(url, 3, 2000);

            if (resp == null || resp.trim().isEmpty()) {
                stats.errorMessage = "No response from college " + college;
                return stats;
            }

            SAXReader reader = new SAXReader();
            Document doc = reader.read(new StringReader(resp));
            Element root = doc.getRootElement();

            Element collegeEl = root.element("college");
            if (collegeEl == null) {
                stats.errorMessage = "Invalid statistics format from college " + college;
                return stats;
            }

            String studentsStr = collegeEl.elementText("students");
            String coursesStr = collegeEl.elementText("courses");
            String choicesStr = collegeEl.elementText("choices");

            stats.students = parseIntSafe(studentsStr);
            stats.courses = parseIntSafe(coursesStr);
            stats.choices = parseIntSafe(choicesStr);
            stats.available = true;

        } catch (Exception e) {
            stats.errorMessage = e.getMessage();
            LOGGER.warning("Failed to fetch statistics from college " + college + ": " + e.getMessage());
        }
        return stats;
    }

    /**
     * Aggregate statistics from all three colleges and build the unified XML response.
     */
    public static String buildGlobalStatisticsXml() {
        try {
            Document doc = DocumentHelper.createDocument();
            Element root = doc.addElement("statistics");

            int totalStudents = 0, totalCourses = 0, totalChoices = 0;

            for (String college : CollegeConfig.getAllColleges()) {
                CollegeStats stats = fetchCollegeStats(college);
                Element collegeEl = root.addElement("college");
                collegeEl.addAttribute("name", college);

                if (stats.available) {
                    collegeEl.addElement("students").setText(String.valueOf(stats.students));
                    collegeEl.addElement("courses").setText(String.valueOf(stats.courses));
                    collegeEl.addElement("choices").setText(String.valueOf(stats.choices));
                    totalStudents += stats.students;
                    totalCourses += stats.courses;
                    totalChoices += stats.choices;
                } else {
                    collegeEl.addElement("error").setText(
                            stats.errorMessage != null ? stats.errorMessage : "Not available");
                }
            }

            Element summary = root.addElement("summary");
            summary.addElement("totalStudents").setText(String.valueOf(totalStudents));
            summary.addElement("totalCourses").setText(String.valueOf(totalCourses));
            summary.addElement("totalChoices").setText(String.valueOf(totalChoices));

            SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss");
            root.addElement("timestamp").setText(sdf.format(new Date()));

            String xml = docToString(doc);

            boolean valid = XSDValidator.validateStatistics(xml);
            if (!valid) {
                LOGGER.warning("Generated statistics XML failed XSD validation");
            }

            return xml;
        } catch (Exception e) {
            LOGGER.severe("Failed to build global statistics: " + e.getMessage());
            return buildErrorStatisticsXml(e.getMessage());
        }
    }

    private static String buildErrorStatisticsXml(String error) {
        return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                + "<statistics>"
                + "<error>" + escapeXml(error) + "</error>"
                + "<timestamp>" + new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss").format(new Date()) + "</timestamp>"
                + "</statistics>";
    }

    private static String docToString(Document doc) {
        try {
            StringWriter sw = new StringWriter();
            OutputFormat format = OutputFormat.createPrettyPrint();
            format.setEncoding("UTF-8");
            XMLWriter writer = new XMLWriter(sw, format);
            writer.write(doc);
            return sw.toString();
        } catch (Exception e) {
            return "";
        }
    }

    private static int parseIntSafe(String s) {
        try {
            return Integer.parseInt(s.trim());
        } catch (Exception e) {
            return 0;
        }
    }

    private static String escapeXml(String s) {
        return s.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace("\"", "&quot;");
    }
}
