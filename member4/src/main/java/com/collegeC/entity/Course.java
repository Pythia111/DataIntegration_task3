package com.collegeC.entity;

public class Course {
    private String cno;
    private String cnm;
    private String ctm;
    private String cpt;
    private String tec;
    private String pla;
    private String share;

    public Course() {
    }

    public Course(String cno, String cnm, String ctm, String cpt, String tec, String pla, String share) {
        this.cno = cno;
        this.cnm = cnm;
        this.ctm = ctm;
        this.cpt = cpt;
        this.tec = tec;
        this.pla = pla;
        this.share = share;
    }

    public String getCno() { return cno; }
    public void setCno(String cno) { this.cno = cno; }
    public String getCnm() { return cnm; }
    public void setCnm(String cnm) { this.cnm = cnm; }
    public String getCtm() { return ctm; }
    public void setCtm(String ctm) { this.ctm = ctm; }
    public String getCpt() { return cpt; }
    public void setCpt(String cpt) { this.cpt = cpt; }
    public String getTec() { return tec; }
    public void setTec(String tec) { this.tec = tec; }
    public String getPla() { return pla; }
    public void setPla(String pla) { this.pla = pla; }
    public String getShare() { return share; }
    public void setShare(String share) { this.share = share; }

    @Override
    public String toString() {
        return "[" + cno + "] " + cnm + " (学分:" + cpt + " 课时:" + ctm + " 老师:" + tec + " 地点:" + pla + ")";
    }
}
