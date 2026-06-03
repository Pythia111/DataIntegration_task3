package com.collegeA.util;

import org.dom4j.Document;
import org.dom4j.DocumentHelper;
import org.dom4j.Element;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.SAXReader;
import org.dom4j.io.XMLWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.Writer;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;

public class XMLHandler {

    // 生成XML的示例实现，基于文档提供的示例
    public static void generateXMLFromResultSet(ResultSet rs, String rootName, String elementName, String outputPath) {
        try {
            ResultSetMetaData rsmd = rs.getMetaData();
            int count = rsmd.getColumnCount();
            String[] columnName = new String[count];
            for (int i = 1; i <= count; i++) {
                columnName[i - 1] = rsmd.getColumnName(i);
            }

            Document doc = DocumentHelper.createDocument();
            Element root = doc.addElement(rootName);

            while (rs.next()) {
                Element emp = root.addElement(elementName);
                for (int i = 1; i <= count; i++) {
                    Element column = emp.addElement(columnName[i - 1]);
                    Object obj = rs.getObject(i);
                    column.setText(obj != null ? obj.toString() : "");
                }
            }

            Writer w = new FileWriter(new File(outputPath));
            OutputFormat opf = OutputFormat.createPrettyPrint();
            opf.setEncoding("UTF-8");
            XMLWriter xw = new XMLWriter(w, opf);
            xw.write(doc);
            xw.close();
            w.close();
            System.out.println("XML Generated at: " + outputPath);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // 解析XML示例
    public static void parseXML(String inputPath) {
        try {
            SAXReader saxReader = new SAXReader();
            Document document = saxReader.read(new File(inputPath));
            Element root = document.getRootElement();
            System.out.println("Root element: " + root.getName());

            // 此处可扩展以读取具体内容
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}