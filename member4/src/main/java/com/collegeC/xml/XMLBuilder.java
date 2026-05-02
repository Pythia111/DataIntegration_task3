package com.collegeC.xml;

import com.collegeC.entity.Course;
import com.collegeC.entity.CourseChoice;
import com.collegeC.entity.Student;
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

    // 生成学院C课程XML（学院C本地格式：Cno/Cnm/Ctm/Cpt/Tec/Pla/Share）
    public static String buildLocalCoursesXML(List<Course> courses) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("Classes");
        for (Course c : courses) {
            Element clazz = root.addElement("class");
            clazz.addElement("Cno").setText(c.getCno());
            clazz.addElement("Cnm").setText(c.getCnm());
            clazz.addElement("Ctm").setText(c.getCtm());
            clazz.addElement("Cpt").setText(c.getCpt());
            clazz.addElement("Tec").setText(c.getTec() != null ? c.getTec() : "");
            clazz.addElement("Pla").setText(c.getPla() != null ? c.getPla() : "");
            clazz.addElement("Share").setText(c.getShare());
        }
        return docToString(doc);
    }

    // 生成学院C学生XML（学院C本地格式：Sno/Snm/Sex/Sde）
    public static String buildLocalStudentsXML(List<Student> students) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("Students");
        for (Student s : students) {
            Element stu = root.addElement("student");
            stu.addElement("Sno").setText(s.getSno());
            stu.addElement("Snm").setText(s.getSnm());
            stu.addElement("Sex").setText(s.getSex());
            stu.addElement("Sde").setText(s.getSde());
        }
        return docToString(doc);
    }

    // 生成学院C选课XML（学院C本地格式：Sno/Cno/Grd）
    public static String buildLocalChoicesXML(List<CourseChoice> choices) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("Choices");
        for (CourseChoice c : choices) {
            Element ch = root.addElement("choice");
            ch.addElement("Sno").setText(c.getSno());
            ch.addElement("Cno").setText(c.getCno());
            ch.addElement("Grd").setText(c.getGrd());
        }
        return docToString(doc);
    }

    // 构建跨院选课/退课请求XML（统一格式，发送给集成服务器）
    public static String buildEnrollRequestXML(String sno, String cno, String operation) {
        Document doc = DocumentHelper.createDocument();
        Element root = doc.addElement("choiceReq");
        root.addElement("traceId").setText(UUID.randomUUID().toString());
        root.addElement("source").setText("C");
        root.addElement("sid").setText(sno);
        root.addElement("cid").setText(cno);
        root.addElement("operation").setText(operation); // ENROLL 或 DROP
        return docToString(doc);
    }

    // 解析集成服务器返回的课程XML（统一格式转回学院C字段名）
    public static List<Course> parseSharedCoursesXML(String xml) {
        List<Course> list = new ArrayList<>();
        try {
            SAXReader reader = new SAXReader();
            Document doc = reader.read(new StringReader(xml));
            Element root = doc.getRootElement();
            // 兼容统一格式(id/name/score/teacher/location)和学院C格式(Cno/Cnm/Cpt/Tec/Pla)
            for (Element clazz : root.elements("class")) {
                Course c = new Course();
                String cno = clazz.elementText("Cno");
                if (cno == null) cno = clazz.elementText("id");
                String cnm = clazz.elementText("Cnm");
                if (cnm == null) cnm = clazz.elementText("name");
                String cpt = clazz.elementText("Cpt");
                if (cpt == null) cpt = clazz.elementText("score");
                String ctm = clazz.elementText("Ctm");
                if (ctm == null) ctm = clazz.elementText("time");
                String tec = clazz.elementText("Tec");
                if (tec == null) tec = clazz.elementText("teacher");
                String pla = clazz.elementText("Pla");
                if (pla == null) pla = clazz.elementText("location");

                c.setCno(cno);
                c.setCnm(cnm);
                c.setCpt(cpt);
                c.setCtm(ctm);
                c.setTec(tec);
                c.setPla(pla);
                c.setShare("Y");
                list.add(c);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return list;
    }

    // 解析跨院选课响应XML
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
