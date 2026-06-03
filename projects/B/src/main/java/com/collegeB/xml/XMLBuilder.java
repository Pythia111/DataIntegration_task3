package com.collegeB.xml;

import com.collegeB.entity.Course;
import com.collegeB.entity.CourseChoice;
import com.collegeB.entity.Student;
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

    // 学院B课程XML（本地格式：编号/名称/课时/学分/老师/地点/共享）
    public static String buildLocalCoursesXML(List<Course> courses) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("Classes");
        for (Course c : courses) {
            Element clazz = root.addElement("class");
            clazz.addElement("编号").setText(c.getCid());
            clazz.addElement("名称").setText(c.getCname());
            clazz.addElement("课时").setText(c.getHours());
            clazz.addElement("学分").setText(c.getCredit());
            clazz.addElement("老师").setText(c.getTeacher() != null ? c.getTeacher() : "");
            clazz.addElement("地点").setText(c.getLocation() != null ? c.getLocation() : "");
            clazz.addElement("共享").setText(c.getShare());
        }
        return docToString(doc);
    }

    // 学院B学生XML（本地格式：学号/姓名/性别/专业/密码(可选)）
    public static String buildLocalStudentsXML(List<Student> students) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("Students");
        for (Student s : students) {
            Element stu = root.addElement("student");
            stu.addElement("学号").setText(s.getSid());
            stu.addElement("姓名").setText(s.getSname());
            stu.addElement("性别").setText(s.getSex());
            stu.addElement("专业").setText(s.getMajor());
            if (s.getPasswd() != null) {
                stu.addElement("密码").setText(s.getPasswd());
            }
        }
        return docToString(doc);
    }

    // 学院B选课XML（本地格式：课程编号/学号/得分）
    public static String buildLocalChoicesXML(List<CourseChoice> choices) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("Choices");
        for (CourseChoice c : choices) {
            Element ch = root.addElement("choice");
            ch.addElement("课程编号").setText(c.getCid());
            ch.addElement("学号").setText(c.getSid());
            if (c.getScore() != null) {
                ch.addElement("得分").setText(c.getScore());
            }
        }
        return docToString(doc);
    }

    // 构建跨院选课/退课请求XML（发给集成服务器）
    public static String buildEnrollRequestXML(String sid, String cid, String operation) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("choiceReq");
        root.addElement("traceId").setText(UUID.randomUUID().toString());
        root.addElement("source").setText("B");
        root.addElement("sid").setText(sid);
        root.addElement("cid").setText(cid);
        root.addElement("operation").setText(operation);
        return docToString(doc);
    }

    // 解析共享课程（兼容统一字段与学院B本地字段）
    public static List<Course> parseSharedCoursesXML(String xml) {
        List<Course> list = new ArrayList<>();
        try {
            SAXReader reader = new SAXReader();
            Document doc = reader.read(new StringReader(xml));
            Element root = doc.getRootElement();
            for (Element clazz : root.elements("class")) {
                Course c = new Course();

                String cid = clazz.elementText("编号");
                if (cid == null) cid = clazz.elementText("id");
                if (cid == null) cid = clazz.elementText("课程编号");

                String cname = clazz.elementText("名称");
                if (cname == null) cname = clazz.elementText("name");
                if (cname == null) cname = clazz.elementText("课程名称");

                String hours = clazz.elementText("课时");
                if (hours == null) hours = clazz.elementText("time");
                if (hours == null) hours = clazz.elementText("classtime");

                String credit = clazz.elementText("学分");
                if (credit == null) credit = clazz.elementText("score");
                if (credit == null) credit = clazz.elementText("classscore");

                String teacher = clazz.elementText("老师");
                if (teacher == null) teacher = clazz.elementText("teacher");
                if (teacher == null) teacher = clazz.elementText("classteacher");

                String location = clazz.elementText("地点");
                if (location == null) location = clazz.elementText("location");
                if (location == null) location = clazz.elementText("classlocation");

                c.setCid(cid);
                c.setCname(cname);
                c.setHours(hours != null ? hours : "");
                c.setCredit(credit != null ? credit : "");
                c.setTeacher(teacher);
                c.setLocation(location);
                c.setShare("Y");
                list.add(c);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    public static String parseChoiceResponseXML(String xml) {
        try {
            SAXReader reader = new SAXReader();
            Document doc = reader.read(new StringReader(xml));
            Element root = doc.getRootElement();
            String status = root.elementText("status");
            String message = root.elementText("message");
            return status + ": " + (message != null ? message : "");
        } catch (Exception e) {
            return "解析响应失败: " + e.getMessage();
        }
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
