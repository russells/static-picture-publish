<?xml version="1.0"?> <!-- -*- mode:sgml; indent-tabs-mode:nil -*- -->

<!-- Image display for static-picture-publish. -->
<!-- Russell Steicke, 2006 -->
<!-- http://adelie.cx/static-picture-publish -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

  <xsl:output method="html"/>

  <xsl:param name="imagePageExtension">.xml</xsl:param>

  <xsl:template match="/picinfo">
    <html>
      <head>
        <title>
          <xsl:if test="string-length(title) != 0">
            <xsl:value-of select="title" />
            <xsl:text> - </xsl:text>
          </xsl:if>
          <xsl:if test="string-length(this/name) != 0">
            <xsl:value-of select="this/name"/>
          </xsl:if>
          <xsl:if test="string-length(this/ext) != 0">
            <xsl:value-of select="this/ext"/>
          </xsl:if>
        </title>
        <xsl:element name="link">
          <xsl:attribute name="rel">
            <xsl:text>stylesheet</xsl:text>
          </xsl:attribute>
          <xsl:attribute name="type">
            <xsl:text>text/css</xsl:text>
          </xsl:attribute>
          <xsl:attribute name="href">
            <xsl:value-of select="@css" />
          </xsl:attribute>
        </xsl:element>
      </head>
      <body>
        <table class="links-table">
          <tr>
            <td class="links-table-cell prev">
              <xsl:choose>
                <xsl:when test="string-length(prev/name) != 0">
                  <xsl:element name="a">
                    <xsl:attribute name="href">
                      <xsl:value-of select="prev/name"/>
                      <xsl:value-of select="$imagePageExtension"/>
                    </xsl:attribute>
                    <xsl:text>&lt;&lt; </xsl:text>
                    <xsl:value-of select="prev/name"/>
                    <xsl:value-of select="prev/ext"/>
                  </xsl:element>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:choose>
                    <xsl:when test="$imagePageExtension = '.xml'">
                      <xsl:text>-</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:text disable-output-escaping="yes">&amp;nbsp;</xsl:text>
                    </xsl:otherwise>
                  </xsl:choose>
                </xsl:otherwise>
              </xsl:choose>
            </td>
            <td class="links-table-cell this">
              <xsl:choose>
                <xsl:when test="$imagePageExtension = '.xml'">
                  <xsl:element name="a">
                    <xsl:attribute name="href">
                      <xsl:text>index.xml#</xsl:text>
                      <xsl:value-of select="/picinfo/this/name"/>
                      <xsl:value-of select="/picinfo/this/ext"/>
                    </xsl:attribute>
                    <xsl:text>Index</xsl:text>
                  </xsl:element>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:element name="a">
                    <xsl:attribute name="href">
                      <xsl:text>.#</xsl:text>
                      <xsl:value-of select="/picinfo/this/name"/>
                      <xsl:value-of select="/picinfo/this/ext"/>
                    </xsl:attribute>
                    <xsl:text>Index</xsl:text>
                  </xsl:element>
                </xsl:otherwise>
              </xsl:choose>
            </td>
            <td class="links-table-cell next">
              <xsl:choose>
                <xsl:when test="string-length(next/name) != 0">
                  <xsl:element name="a">
                    <xsl:attribute name="href">
                      <xsl:value-of select="next/name"/>
                      <xsl:value-of select="$imagePageExtension"/>
                    </xsl:attribute>
                    <xsl:value-of select="next/name"/>
                    <xsl:value-of select="next/ext"/>
                    <xsl:text> &gt;&gt;</xsl:text>
                  </xsl:element>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:choose>
                    <xsl:when test="$imagePageExtension = '.xml'">
                      <xsl:text>-</xsl:text>
                    </xsl:when>
                    <xsl:otherwise>
                      <xsl:text disable-output-escaping="yes">&amp;nbsp;</xsl:text>
                    </xsl:otherwise>
                  </xsl:choose>
                </xsl:otherwise>
              </xsl:choose>
              <!-- <xsl:text>&amp;nbsp;</xsl:text> -->
            </td>
          </tr>
        </table>
        <span class="page-title">
          <xsl:if test="string-length(title) != 0">
            <xsl:value-of select="title" />
            <xsl:text> - </xsl:text>
          </xsl:if>
          <xsl:value-of select="this/name"/>
          <xsl:value-of select="this/ext"/>
        </span>
        <div class="picinfo">
          <xsl:element name="a">
            <xsl:attribute name="href">
              <xsl:value-of select="this/name"/>
              <xsl:text>-full</xsl:text>
              <xsl:value-of select="this/ext"/>
            </xsl:attribute>
            <xsl:element name="img">
              <xsl:attribute name="src">
                <xsl:value-of select="this/name"/>
                <xsl:value-of select="this/ext"/>
              </xsl:attribute>
              <xsl:attribute name="alt">
                <xsl:value-of select="this/name"/>
                <xsl:value-of select="this/ext"/>
              </xsl:attribute>
              <xsl:attribute name="width">
                <xsl:value-of select="this/size/@width" />
              </xsl:attribute>
              <xsl:attribute name="height">
                <xsl:value-of select="this/size/@height" />
              </xsl:attribute>
            </xsl:element>
          </xsl:element>
          <xsl:if test="string-length(this/comment) != 0">
            <div class="imagecomment-image">
              <xsl:value-of select="this/comment" />
            </div>
          </xsl:if>
          <div class="fullpicinfo">
            <xsl:text>Full size: </xsl:text>
            <xsl:element name="a">
              <xsl:attribute name="href">
                <xsl:value-of select="this/name"/>
                <xsl:text>-full</xsl:text>
                <xsl:value-of select="this/ext"/>
              </xsl:attribute>
              <xsl:text>View</xsl:text>
            </xsl:element>
            <xsl:text> or </xsl:text>
            <xsl:element name="a">
              <xsl:attribute name="href">
                <xsl:value-of select="this/name"/>
                <xsl:text>-download</xsl:text>
                <xsl:value-of select="this/ext"/>
              </xsl:attribute>
              <xsl:text>download</xsl:text>
            </xsl:element>
          </div>
        </div>
        <div class="footer">
          <xsl:text>Generated by </xsl:text>
          <xsl:element name="a">
            <xsl:attribute name="href">
              <xsl:text>http://adelie.cx/static-picture-publish/</xsl:text>
            </xsl:attribute>
            <xsl:text>static-picture-publish</xsl:text>
          </xsl:element>
          <xsl:text> </xsl:text>
          <xsl:value-of select="@version"/>
        </div>
      </body>
    </html>
  </xsl:template>

</xsl:stylesheet>

<!-- arch-tag: 2d073797-f8f7-4165-b5a6-32a6141b0669
-->

