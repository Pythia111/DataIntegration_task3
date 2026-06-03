package com.integration.xml;

import javax.xml.XMLConstants;
import javax.xml.transform.Source;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;
import java.io.InputStream;
import java.io.StringReader;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;

public class XSDValidator {

    private static final Logger LOGGER = Logger.getLogger(XSDValidator.class.getName());

    private static final Map<String, String> XSD_MAP = new HashMap<>();

    static {
        XSD_MAP.put("studentA", "/xsd/local/studentA.xsd");
        XSD_MAP.put("studentB", "/xsd/local/studentB.xsd");
        XSD_MAP.put("studentC", "/xsd/local/studentC.xsd");
        XSD_MAP.put("classA", "/xsd/local/classA.xsd");
        XSD_MAP.put("classB", "/xsd/local/classB.xsd");
        XSD_MAP.put("classC", "/xsd/local/classC.xsd");
        XSD_MAP.put("choiceA", "/xsd/local/choiceA.xsd");
        XSD_MAP.put("choiceB", "/xsd/local/choiceB.xsd");
        XSD_MAP.put("choiceC", "/xsd/local/choiceC.xsd");
        XSD_MAP.put("formatStudent", "/xsd/unified/formatStudent.xsd");
        XSD_MAP.put("formatClass", "/xsd/unified/formatClass.xsd");
        XSD_MAP.put("formatClassChoice", "/xsd/unified/formatClassChoice.xsd");
        XSD_MAP.put("choiceReq", "/xsd/choiceReq.xsd");
        XSD_MAP.put("response", "/xsd/response.xsd");
    }

    public static boolean validate(String xmlContent, String xsdKey) {
        String xsdPath = XSD_MAP.get(xsdKey);
        if (xsdPath == null) {
            LOGGER.warning("Unknown XSD key: " + xsdKey);
            return false;
        }
        try {
            InputStream xsdStream = XSDValidator.class.getResourceAsStream(xsdPath);
            if (xsdStream == null) {
                LOGGER.warning("XSD file not found: " + xsdPath);
                return false;
            }

            SchemaFactory factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
            factory.setProperty(XMLConstants.ACCESS_EXTERNAL_DTD, "");
            factory.setProperty(XMLConstants.ACCESS_EXTERNAL_SCHEMA, "");

            Source schemaSource = new StreamSource(xsdStream);
            Schema schema = factory.newSchema(schemaSource);
            Validator validator = schema.newValidator();

            Source xmlSource = new StreamSource(new StringReader(xmlContent));
            validator.validate(xmlSource);

            LOGGER.info("XSD validation passed for key: " + xsdKey);
            return true;
        } catch (Exception e) {
            LOGGER.warning("XSD validation failed for key " + xsdKey + ": " + e.getMessage());
            return false;
        }
    }

    public static boolean validateCourseXML(String xmlContent, String college) {
        return validate(xmlContent, "class" + college);
    }

    public static boolean validateStudentXML(String xmlContent, String college) {
        return validate(xmlContent, "student" + college);
    }

    public static boolean validateChoiceXML(String xmlContent, String college) {
        return validate(xmlContent, "choice" + college);
    }

    public static boolean validateUnifiedClass(String xmlContent) {
        return validate(xmlContent, "formatClass");
    }

    public static boolean validateUnifiedStudent(String xmlContent) {
        return validate(xmlContent, "formatStudent");
    }

    public static boolean validateUnifiedChoice(String xmlContent) {
        return validate(xmlContent, "formatClassChoice");
    }

    public static boolean validateChoiceRequest(String xmlContent) {
        return validate(xmlContent, "choiceReq");
    }

    public static boolean validateResponse(String xmlContent) {
        return validate(xmlContent, "response");
    }
}
