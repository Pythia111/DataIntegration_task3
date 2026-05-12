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

import java.io.IOException;
import java.io.OutputStream;
import java.io.StringReader;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Logger;

public class SharedCoursesHandler implements HttpHandler {

    private static final Logger LOGGER = Logger.getLogger(SharedCoursesHandler.class.getName());

    @Override
    public void handle(HttpExchange exchange) throws IOException {
        if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
            sendResponse(exchange, 405, "<error>Method Not Allowed</error>");
            return;
        }

        String query = exchange.getRequestURI().getQuery();
        String source = getParam(query, "source");
        if (source == null || !CollegeConfig.isValidCollege(source)) {
            sendResponse(exchange, 400, "<error>Missing or invalid 'source' parameter. Use A, B, or C.</error>");
            return;
        }

        LOGGER.info("Received sharedCourses request from college " + source);

        String[] otherColleges = CollegeConfig.getOtherColleges(source);
        List<Document> unifiedDocs = new ArrayList<>();

        for (String college : otherColleges) {
            try {
                String url = CollegeConfig.getSharedCoursesUrl(college);
                LOGGER.info("Fetching shared courses from college " + college + ": " + url);
                String localXml = HttpUtil.httpGet(url);

                if (localXml == null || localXml.trim().isEmpty()) {
                    LOGGER.warning("No response from college " + college);
                    continue;
                }

                boolean valid = XSDValidator.validateCourseXML(localXml, college);
                if (!valid) {
                    LOGGER.warning("XSD validation failed for college " + college + " courses XML");
                }

                String unifiedXml = XSLTTransformer.localCourseToUnified(localXml, college);
                if (unifiedXml != null && !unifiedXml.trim().isEmpty()) {
                    SAXReader reader = new SAXReader();
                    Document doc = reader.read(new StringReader(unifiedXml));
                    unifiedDocs.add(doc);
                    LOGGER.info("Successfully transformed college " + college + " courses to unified format");
                }
            } catch (Exception e) {
                LOGGER.warning("Error processing courses from college " + college + ": " + e.getMessage());
            }
        }

        if (unifiedDocs.isEmpty()) {
            String emptyXml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<classes version=\"1.0\"/>";
            String targetXml = XSLTTransformer.unifiedCourseToLocal(emptyXml, source);
            sendResponse(exchange, 200, targetXml != null ? targetXml : emptyXml);
            return;
        }

        Document merged = mergeUnifiedCourses(unifiedDocs);
        String mergedXml = docToString(merged);

        boolean validMerged = XSDValidator.validateUnifiedClass(mergedXml);
        if (!validMerged) {
            LOGGER.warning("Merged unified XML validation failed");
        }

        String targetXml = XSLTTransformer.unifiedCourseToLocal(mergedXml, source);
        sendResponse(exchange, 200, targetXml != null ? targetXml : mergedXml);
    }

    private Document mergeUnifiedCourses(List<Document> docs) {
        Document merged = DocumentHelper.createDocument();
        Element root = merged.addElement("classes");
        root.addAttribute("version", "1.0");

        for (Document doc : docs) {
            Element docRoot = doc.getRootElement();
            String nsUri = docRoot.getNamespaceURI();
            for (Element clazz : docRoot.elements("class")) {
                Element newClass = root.addElement("class");
                copyElementContent(clazz, newClass, nsUri);
            }
        }
        return merged;
    }

    private void copyElementContent(Element src, Element dest, String nsUri) {
        for (Element child : src.elements()) {
            String name = child.getName();
            String childNs = child.getNamespaceURI();
            if (childNs != null && !childNs.isEmpty() && !childNs.equals(nsUri)) {
                Element newChild = dest.addElement(name);
                newChild.setText(child.getText());
            } else {
                Element newChild = dest.addElement(name);
                newChild.setText(child.getText());
            }
        }
    }

    private String docToString(Document doc) {
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

    private void sendResponse(HttpExchange exchange, int statusCode, String xml) throws IOException {
        byte[] response = xml.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/xml; charset=UTF-8");
        exchange.sendResponseHeaders(statusCode, response.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(response);
        }
    }
}
