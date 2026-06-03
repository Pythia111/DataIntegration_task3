package com.collegeB.entity;

public class Student {
    private String sid;
    private String sname;
    private String sex;
    private String major;
    private String passwd;

    public Student() {
    }

    public Student(String sid, String sname, String sex, String major, String passwd) {
        this.sid = sid;
        this.sname = sname;
        this.sex = sex;
        this.major = major;
        this.passwd = passwd;
    }

    public String getSid() {
        return sid;
    }

    public void setSid(String sid) {
        this.sid = sid;
    }

    public String getSname() {
        return sname;
    }

    public void setSname(String sname) {
        this.sname = sname;
    }

    public String getSex() {
        return sex;
    }

    public void setSex(String sex) {
        this.sex = sex;
    }

    public String getMajor() {
        return major;
    }

    public void setMajor(String major) {
        this.major = major;
    }

    public String getPasswd() {
        return passwd;
    }

    public void setPasswd(String passwd) {
        this.passwd = passwd;
    }
}
