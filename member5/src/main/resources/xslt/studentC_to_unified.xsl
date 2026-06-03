<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/Students">
    <students version="1.0">
      <xsl:for-each select="student">
        <student>
          <id><xsl:value-of select="Sno"/></id>
          <name><xsl:value-of select="Snm"/></name>
          <sex><xsl:value-of select="Sex"/></sex>
          <major><xsl:value-of select="Sde"/></major>
          <college>C</college>
          <xsl:if test="Pwd">
            <account><xsl:value-of select="Pwd"/></account>
          </xsl:if>
        </student>
      </xsl:for-each>
    </students>
  </xsl:template>
</xsl:stylesheet>
