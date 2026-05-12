<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/Students">
    <students version="1.0">
      <xsl:for-each select="student">
        <student>
          <id><xsl:value-of select="学号"/></id>
          <name><xsl:value-of select="姓名"/></name>
          <sex><xsl:value-of select="性别"/></sex>
          <major><xsl:value-of select="专业"/></major>
          <college>B</college>
          <xsl:if test="密码">
            <account><xsl:value-of select="密码"/></account>
          </xsl:if>
        </student>
      </xsl:for-each>
    </students>
  </xsl:template>
</xsl:stylesheet>
