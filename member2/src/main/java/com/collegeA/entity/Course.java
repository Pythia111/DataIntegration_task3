package com.collegeA.entity;

public class Course {
    private String id;
    private String name;
    private String score;
    private String teacher;
    private String location;
    private String share;

    public Course() {
    }

    public Course(String id, String name, String score, String teacher, String location, String share) {
        this.id = id;
        this.name = name;
        this.score = score;
        this.teacher = teacher;
        this.location = location;
        this.share = share;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getScore() {
        return score;
    }

    public void setScore(String score) {
        this.score = score;
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
        return "[" + id + "] " + name + " (学分:" + score + " 老师:" + teacher + " 地点:" + location + ")";
    }
}