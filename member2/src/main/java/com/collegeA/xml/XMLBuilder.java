package com.collegeA.xml;

import com.collegeA.entity.Course;
import com.collegeA.entity.CourseChoice;
import org.dom4j.Document;
import org.dom4j.DocumentHelper;
import org.dom4j.Element;
import org.dom4j.io.OutputFormat;
import org.dom4j.io.SAXReader;
import org.dom4j.io.XMLWriter;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class XMLBuilder {

    // 格式化本地课程 XML
    public static String buildLocalCoursesXML(List<Course> courses) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("Classes");
        for (Course c : courses) {
            Element clazz = root.addElement("class");
            clazz.addElement("课程编号").setText(c.getId());
            clazz.addElement("课程名称").setText(c.getName());
            clazz.addElement("学分").setText(c.getScore());
            clazz.addElement("授课老师").setText(c.getTeacher() != null ? c.getTeacher() : "");
            clazz.addElement("授课地点").setText(c.getLocation() != null ? c.getLocation() : "");
            clazz.addElement("共享").setText(c.getShare());
        }
        return docToString(doc);
    }

    // 构建跨院选课/退课请求的 XML
    public static String buildEnrollRequestXML(String studentId, String courseId, String operation) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("choiceReq");
        root.addElement("traceId").setText(UUID.randomUUID().toString());
        root.addElement("sid").setText(studentId);
        root.addElement("cid").setText(courseId);
        root.addElement("operation").setText(operation); // ENROLL 或 DROP
        return docToString(doc);
    }

    // 解析统一返回的课程XML为对象实体以供界面展示
    public static List<Course> parseSharedCoursesXML(String xml) {
        List<Course> list = new ArrayList<>();
        try {
            SAXReader reader = new SAXReader();
            Document doc = reader.read(new StringReader(xml));
            Element root = doc.getRootElement();
            for (Element clazz : root.elements("class")) {
                Course c = new Course();
                c.setId(clazz.elementText("课程编号"));
                c.setName(clazz.elementText("课程名称"));
                c.setScore(clazz.elementText("学分"));
                c.setTeacher(clazz.elementText("授课老师"));
                c.setLocation(clazz.elementText("授课地点"));
                c.setShare("Y"); // 获取的肯定是共享课程
                list.add(c);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
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
            return null;
        }
    }
}