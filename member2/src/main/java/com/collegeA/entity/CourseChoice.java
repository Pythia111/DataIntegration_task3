package com.collegeA.entity;

public class CourseChoice {
    private String studentId;
    private String courseId;
    private String score;

    public CourseChoice() {
    }

    public CourseChoice(String studentId, String courseId, String score) {
        this.studentId = studentId;
        this.courseId = courseId;
        this.score = score;
    }

    public String getStudentId() {
        return studentId;
    }

    public void setStudentId(String studentId) {
        this.studentId = studentId;
    }

    public String getCourseId() {
        return courseId;
    }

    public void setCourseId(String courseId) {
        this.courseId = courseId;
    }

    public String getScore() {
        return score;
    }

    public void setScore(String score) {
        this.score = score;
    }
}