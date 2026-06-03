package com.collegeB.entity;

public class CourseChoice {
    private String sid;
    private String cid;
    private String score;

    public CourseChoice() {
    }

    public CourseChoice(String sid, String cid, String score) {
        this.sid = sid;
        this.cid = cid;
        this.score = score;
    }

    public String getSid() {
        return sid;
    }

    public void setSid(String sid) {
        this.sid = sid;
    }

    public String getCid() {
        return cid;
    }

    public void setCid(String cid) {
        this.cid = cid;
    }

    public String getScore() {
        return score;
    }

    public void setScore(String score) {
        this.score = score;
    }
}
