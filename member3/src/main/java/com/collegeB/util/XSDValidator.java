package com.collegeB.util;

import java.io.StringReader;

import javax.xml.XMLConstants;
import javax.xml.transform.Source;
import javax.xml.transform.stream.StreamSource;
import javax.xml.validation.Schema;
import javax.xml.validation.SchemaFactory;
import javax.xml.validation.Validator;

import org.xml.sax.SAXException;

public class XSDValidator {
    public static void validateXmlString(String xml, String xsdPath) throws Exception {
        SchemaFactory factory = SchemaFactory.newInstance(XMLConstants.W3C_XML_SCHEMA_NS_URI);
        Schema schema = factory.newSchema(new java.io.File(xsdPath));
        Validator validator = schema.newValidator();
        Source source = new StreamSource(new StringReader(xml));
        try {
            validator.validate(source);
        } catch (SAXException e) {
            throw new IllegalArgumentException("XSD校验失败: " + e.getMessage(), e);
        }
    }
}
