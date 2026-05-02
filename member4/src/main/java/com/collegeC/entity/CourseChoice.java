package com.collegeC.entity;

public class CourseChoice {
    private String sno;
    private String cno;
    private String grd;

    public CourseChoice() {
    }

    public CourseChoice(String sno, String cno, String grd) {
        this.sno = sno;
        this.cno = cno;
        this.grd = grd;
    }

    public String getSno() { return sno; }
    public void setSno(String sno) { this.sno = sno; }
    public String getCno() { return cno; }
    public void setCno(String cno) { this.cno = cno; }
    public String getGrd() { return grd; }
    public void setGrd(String grd) { this.grd = grd; }
}
