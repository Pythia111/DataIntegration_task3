package com.collegeB.entity;

public class Course {
    private String cid;
    private String cname;
    private String hours;
    private String credit;
    private String teacher;
    private String location;
    private String share;

    public Course() {
    }

    public Course(String cid, String cname, String hours, String credit, String teacher, String location, String share) {
        this.cid = cid;
        this.cname = cname;
        this.hours = hours;
        this.credit = credit;
        this.teacher = teacher;
        this.location = location;
        this.share = share;
    }

    public String getCid() {
        return cid;
    }

    public void setCid(String cid) {
        this.cid = cid;
    }

    public String getCname() {
        return cname;
    }

    public void setCname(String cname) {
        this.cname = cname;
    }

    public String getHours() {
        return hours;
    }

    public void setHours(String hours) {
        this.hours = hours;
    }

    public String getCredit() {
        return credit;
    }

    public void setCredit(String credit) {
        this.credit = credit;
    }

    public String getTeacher() {
        return teacher;
    }

    public void setTeacher(String teacher) {
        this.teacher = teacher;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getShare() {
        return share;
    }

    public void setShare(String share) {
        this.share = share;
    }

    @Override
    public String toString() {
        return "[" + cid + "] " + cname + " (学分:" + credit + " 课时:" + hours + " 老师:" + teacher + " 地点:" + location + ")";
    }
}
