<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/Classes">
    <classes version="1.0">
      <xsl:for-each select="class">
        <class>
          <id><xsl:value-of select="Cno"/></id>
          <name><xsl:value-of select="Cnm"/></name>
          <time><xsl:value-of select="Ctm"/></time>
          <score><xsl:value-of select="Cpt"/></score>
          <teacher><xsl:value-of select="Tec"/></teacher>
          <location><xsl:value-of select="Pla"/></location>
          <college>C</college>
          <share><xsl:value-of select="Share"/></share>
        </class>
      </xsl:for-each>
    </classes>
  </xsl:template>
</xsl:stylesheet>
