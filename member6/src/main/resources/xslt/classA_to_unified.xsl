<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/Classes">
    <classes version="1.0">
      <xsl:for-each select="class">
        <class>
          <id><xsl:value-of select="课程编号"/></id>
          <name><xsl:value-of select="课程名称"/></name>
          <score><xsl:value-of select="学分"/></score>
          <teacher><xsl:value-of select="授课老师"/></teacher>
          <location><xsl:value-of select="授课地点"/></location>
          <college>A</college>
          <share><xsl:value-of select="共享"/></share>
        </class>
      </xsl:for-each>
    </classes>
  </xsl:template>
</xsl:stylesheet>
