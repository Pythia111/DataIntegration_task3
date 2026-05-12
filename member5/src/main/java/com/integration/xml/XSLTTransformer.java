package com.integration.xml;

import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamSource;
import javax.xml.transform.stream.StreamResult;
import java.io.InputStream;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

public class XSLTTransformer {

    private static final Logger LOGGER = Logger.getLogger(XSLTTransformer.class.getName());

    private static final Map<String, String> XSLT_MAP = new HashMap<>();

    static {
        XSLT_MAP.put("classA_to_unified", "/xslt/classA_to_unified.xsl");
        XSLT_MAP.put("classB_to_unified", "/xslt/classB_to_unified.xsl");
        XSLT_MAP.put("classC_to_unified", "/xslt/classC_to_unified.xsl");
        XSLT_MAP.put("unified_to_classA", "/xslt/unified_to_classA.xsl");
        XSLT_MAP.put("unified_to_classB", "/xslt/unified_to_classB.xsl");
        XSLT_MAP.put("unified_to_classC", "/xslt/unified_to_classC.xsl");
        XSLT_MAP.put("studentA_to_unified", "/xslt/studentA_to_unified.xsl");
        XSLT_MAP.put("studentB_to_unified", "/xslt/studentB_to_unified.xsl");
        XSLT_MAP.put("studentC_to_unified", "/xslt/studentC_to_unified.xsl");
        XSLT_MAP.put("unified_to_studentA", "/xslt/unified_to_studentA.xsl");
        XSLT_MAP.put("unified_to_studentB", "/xslt/unified_to_studentB.xsl");
        XSLT_MAP.put("unified_to_studentC", "/xslt/unified_to_studentC.xsl");
        XSLT_MAP.put("enrollReq_to_local", "/xslt/enrollReq_to_local.xsl");
        XSLT_MAP.put("dropReq_to_local", "/xslt/dropReq_to_local.xsl");
    }

    public static String transform(String xmlContent, String xsltKey) {
        String xsltPath = XSLT_MAP.get(xsltKey);
        if (xsltPath == null) {
            LOGGER.warning("Unknown XSLT key: " + xsltKey);
            return xmlContent;
        }
        try {
            InputStream xsltStream = XSLTTransformer.class.getResourceAsStream(xsltPath);
            if (xsltStream == null) {
                LOGGER.warning("XSLT file not found: " + xsltPath);
                return xmlContent;
            }

            TransformerFactory factory = TransformerFactory.newInstance();
            StreamSource xsltSource = new StreamSource(xsltStream);
            Transformer transformer = factory.newTransformer(xsltSource);

            StreamSource xmlSource = new StreamSource(new StringReader(xmlContent));
            StringWriter writer = new StringWriter();
            StreamResult result = new StreamResult(writer);

            transformer.transform(xmlSource, result);

            LOGGER.info("XSLT transform succeeded for key: " + xsltKey);
            return writer.toString();
        } catch (Exception e) {
            LOGGER.warning("XSLT transform failed for key " + xsltKey + ": " + e.getMessage());
            return xmlContent;
        }
    }

    public static String localCourseToUnified(String xmlContent, String college) {
        return transform(xmlContent, "class" + college + "_to_unified");
    }

    public static String unifiedCourseToLocal(String xmlContent, String college) {
        return transform(xmlContent, "unified_to_class" + college);
    }

    public static String localStudentToUnified(String xmlContent, String college) {
        return transform(xmlContent, "student" + college + "_to_unified");
    }

    public static String unifiedStudentToLocal(String xmlContent, String college) {
        return transform(xmlContent, "unified_to_student" + college);
    }

    public static String enrollReqToLocal(String xmlContent) {
        return transform(xmlContent, "enrollReq_to_local");
    }

    public static String dropReqToLocal(String xmlContent) {
        return transform(xmlContent, "dropReq_to_local");
    }
}
