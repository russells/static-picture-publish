<?xml version="1.0"?> <!-- -*- mode:sgml; indent-tabs-mode:nil -*- -->

<!-- Directory display for static-picture-publish. -->
<!-- Russell Steicke, 2006 -->
<!-- http://adelie.cx/static-picture-publish -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!--
Enabling these extra output attributes results in firefox (at least) not
being able to display the translated html.

  <xsl:output method="xml" omit-xml-declaration="yes"
  doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
  doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>
-->
  <xsl:output method="html"/>

  <xsl:template match="*"/>

  <!-- Can we pass this in as a stylesheet argument? -->
  <xsl:param name="nTableCells">4</xsl:param>

  <xsl:template match="/picturedir">
    <html>
      <head>
        <title>
          <xsl:if test="string-length(@name) != 0">
            <xsl:value-of select="@name"/>
          </xsl:if>
          <xsl:if test="string-length(@path) != 0">
            <xsl:if test="string-length(@name) != 0">
              <xsl:text>: </xsl:text>
            </xsl:if>
          </xsl:if>
          <xsl:if test="string-length(@path) != 0">
            <xsl:value-of select="@path"/>
          </xsl:if>
        </title>
        <xsl:if test="string-length(@css) != 0">
          <xsl:element name="link">
            <xsl:attribute name="rel">
              <xsl:text>stylesheet</xsl:text>
            </xsl:attribute>
            <xsl:attribute name="type">
              <xsl:text>text/css</xsl:text>
            </xsl:attribute>
            <xsl:attribute name="href">
              <xsl:value-of select="@css"/>
            </xsl:attribute>
          </xsl:element>
        </xsl:if>
      </head>
      <body>
        <div class="picturedir">
          <xsl:apply-templates/>
        </div>
        <div class="footer">
          <xsl:text>Powered by </xsl:text>
          <xsl:element name="a">
            <xsl:attribute name="href">
              <xsl:text>http://adelie.cx/static-picture-publish/</xsl:text>
            </xsl:attribute>
            <xsl:attribute name="target">
              <xsl:text>_blank</xsl:text>
            </xsl:attribute>
            <xsl:text>SPP</xsl:text>
          </xsl:element>
          <xsl:text> </xsl:text>
          <xsl:value-of select="@version"/>
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="updir">
    <div class="updir">
      <xsl:text>[</xsl:text>
      <xsl:element name="a">
        <xsl:attribute name="href">..</xsl:attribute>
        <xsl:text>Up...</xsl:text>
      </xsl:element>
      <xsl:text>]</xsl:text>
    </div>
    <!-- xsl:apply-templates/ -->
  </xsl:template>

  <xsl:template match="/picturedir/dirs">
    <xsl:for-each select="dir[ position() mod 3 = 1 ]">
      <div class="dir-row">
        <xsl:for-each select=". | following-sibling::dir[position()&lt;3]">
          <xsl:call-template name="dirtemplate">
            <xsl:with-param name="p"><xsl:value-of select="position()"/></xsl:with-param>
          </xsl:call-template>
        </xsl:for-each>
      </div>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="dirtemplate">
    <xsl:param name="p">0</xsl:param>
    <xsl:element name="div">
      <xsl:attribute name="class">
        <xsl:text>dir dircol</xsl:text><xsl:value-of select="$p"/>
      </xsl:attribute>
      <xsl:element name="a">
        <xsl:attribute name="href">
          <xsl:value-of select="name"/>
        </xsl:attribute>
        <xsl:value-of select="path"/><xsl:text>/</xsl:text>
      </xsl:element>
    </xsl:element>
    <!-- <xsl:apply-templates/ -->
  </xsl:template>

  <xsl:template match="/picturedir/images">
    <table class="thumbnail-table">
      <xsl:attribute name="summary">
        <xsl:text>Thumbnails!</xsl:text>
      </xsl:attribute>
      <xsl:for-each select="image[ position() mod $nTableCells = 1 ]">
        <tr class="thumbnail-table-row">
          <xsl:for-each select=". | following-sibling::image[position()&lt;$nTableCells]">
            <xsl:call-template name="imagetemplate">
              <!-- <xsl:with-param name="p"><xsl:value-of select="position()"/></xsl:with-param> -->
            </xsl:call-template>
          </xsl:for-each>
        </tr>
      </xsl:for-each>
    </table>
  </xsl:template>


  <xsl:template name="imagetemplate">
    <xsl:element name="td">
      <xsl:attribute name="class">
        <xsl:text>thumbnail-table-cell</xsl:text>
      </xsl:attribute>
      <xsl:element name="div">
        <xsl:attribute name="class">
          <xsl:text>thumbnail-image</xsl:text>
        </xsl:attribute>
        <xsl:element name="a">
          <xsl:attribute name="href">
            <xsl:value-of select="name"/>
            <xsl:text>.xml</xsl:text>
          </xsl:attribute>
          <xsl:element name="img">
            <xsl:attribute name="src">
              <xsl:value-of select="name"/>
              <xsl:text>-thumb</xsl:text>
              <xsl:value-of select="ext"/>
            </xsl:attribute>
            <xsl:attribute name="alt">
              <xsl:value-of select="name"/>
              <xsl:value-of select="ext"/>
            </xsl:attribute>
            <xsl:attribute name="class">
              <xsl:text>image</xsl:text>
            </xsl:attribute>
          </xsl:element>
        </xsl:element>
      </xsl:element>
      <xsl:element name="p">
        <xsl:attribute name="class">
          <xsl:text>thumbnail-text</xsl:text>
        </xsl:attribute>
        <xsl:element name="a">
          <xsl:attribute name="href">
            <xsl:value-of select="name"/>
            <xsl:text>.xml</xsl:text>
          </xsl:attribute>
          <xsl:value-of select="name"/>
        </xsl:element>
      </xsl:element>
    </xsl:element>
    <!-- xsl:apply-templates/ -->
  </xsl:template>

</xsl:stylesheet>

<!-- arch-tag: ca508c04-650d-4965-bb7f-b40d0538b849
-->

