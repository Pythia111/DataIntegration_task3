package com.collegeC.entity;

public class Student {
    private String sno;
    private String snm;
    private String sex;
    private String sde;
    private String pwd;

    public Student() {
    }

    public Student(String sno, String snm, String sex, String sde, String pwd) {
        this.sno = sno;
        this.snm = snm;
        this.sex = sex;
        this.sde = sde;
        this.pwd = pwd;
    }

    public String getSno() { return sno; }
    public void setSno(String sno) { this.sno = sno; }
    public String getSnm() { return snm; }
    public void setSnm(String snm) { this.snm = snm; }
    public String getSex() { return sex; }
    public void setSex(String sex) { this.sex = sex; }
    public String getSde() { return sde; }
    public void setSde(String sde) { this.sde = sde; }
    public String getPwd() { return pwd; }
    public void setPwd(String pwd) { this.pwd = pwd; }
}
