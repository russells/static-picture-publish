<?xml version="1.0"?>

<!-- Directory display for static-picture-publish. -->

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

  <xsl:template match="/picturedir">
    <html>
      <head>
        <title>
          <xsl:if test="string-length(@name) != 0">
            <xsl:value-of select="@name"/>
            <xsl:text>: </xsl:text>
          </xsl:if>
          <xsl:value-of select="index/@path"/>
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
        <div class="svn">
          <xsl:apply-templates/>
        </div>
        <div class="footer">
          <xsl:text>Powered by </xsl:text>
          <xsl:element name="a">
            <xsl:attribute name="href">
              <xsl:value-of select="@href"/>
            </xsl:attribute>
            <xsl:text>Subversion</xsl:text>
          </xsl:element>
          <xsl:text> </xsl:text>
          <xsl:value-of select="@version"/>
        </div>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="index">
    <div class="rev">
      <xsl:if test="string-length(@name) != 0">
        <xsl:value-of select="@name"/>
        <xsl:if test="string-length(@rev) != 0">
          <xsl:text> &#8212; </xsl:text>
        </xsl:if>
      </xsl:if>
      <xsl:if test="string-length(@rev) != 0">
        <xsl:text>Revision </xsl:text>
        <xsl:value-of select="@rev"/>
      </xsl:if>
    </div>
    <div class="path">
      <xsl:value-of select="@path"/>
    </div>
    <xsl:apply-templates select="updir"/>
    <xsl:apply-templates select="dir"/>
    <xsl:apply-templates select="file"/>
  </xsl:template>

  <xsl:template match="updir">
    <div class="updir">
      <xsl:text>[</xsl:text>
      <xsl:element name="a">
        <xsl:attribute name="href">..</xsl:attribute>
        <xsl:text>Parent Directory</xsl:text>
      </xsl:element>
      <xsl:text>]</xsl:text>
    </div>
    <!-- xsl:apply-templates/ -->
  </xsl:template>

  <xsl:template match="dir">
    <div class="dir">
      <xsl:element name="a">
        <xsl:attribute name="href">
          <xsl:value-of select="@href"/>
        </xsl:attribute>
        <xsl:value-of select="@name"/>
        <xsl:text>/</xsl:text>
      </xsl:element>
    </div>
    <!-- <xsl:apply-templates/ -->
  </xsl:template>

  <xsl:template match="image">
    <div class="thumbnail">
      <xsl:element name="div">
        <xsl:attribute name="class">
	  <xsl:text>thumbnailtext</xsl:text>
        </xsl:attribute>
        <xsl:element name="a">
          <xsl:attribute name="href">
            <xsl:value-of select="name"/>
	    <xsl:text>.xml</xsl:text>
          </xsl:attribute>
          <xsl:value-of select="name"/>
        </xsl:element>
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
	  </xsl:element>
        </xsl:element>
      </xsl:element>
    </div>
    <!-- xsl:apply-templates/ -->
  </xsl:template>

</xsl:stylesheet>

<!-- arch-tag: ca508c04-650d-4965-bb7f-b40d0538b849
-->

