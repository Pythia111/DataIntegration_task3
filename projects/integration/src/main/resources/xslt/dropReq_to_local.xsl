<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/choiceReq">
    <choices version="1.0">
      <choice>
        <sid><xsl:value-of select="sid"/></sid>
        <cid><xsl:value-of select="cid"/></cid>
        <requestCollege><xsl:value-of select="source"/></requestCollege>
        <ownerCollege>
          <xsl:choose>
            <xsl:when test="starts-with(cid, 'C_A') or starts-with(cid, 'A')">A</xsl:when>
            <xsl:when test="starts-with(cid, 'B')">B</xsl:when>
            <xsl:when test="starts-with(cid, 'C')">C</xsl:when>
            <xsl:otherwise>UNKNOWN</xsl:otherwise>
          </xsl:choose>
        </ownerCollege>
        <operation>DROP</operation>
        <status>PENDING</status>
        <traceId><xsl:value-of select="traceId"/></traceId>
      </choice>
    </choices>
  </xsl:template>
</xsl:stylesheet>
