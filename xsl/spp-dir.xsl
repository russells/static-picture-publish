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

  <xsl:param name="nTableCells">4</xsl:param>
  <xsl:param name="imagePageExtension">.xml</xsl:param>
  <xsl:param name="repeatDirsAfterNImages">9</xsl:param>
  <xsl:param name="doDownloads">yes</xsl:param>

  <xsl:template match="/picturedir">
    <html>
      <xsl:element name="META">
        <xsl:attribute name="http-equiv">Content-Script-Type</xsl:attribute>
        <xsl:attribute name="content">text/javascript</xsl:attribute>
      </xsl:element>
      <head>
        <xsl:if test="$doDownloads = 'yes'">
<script type="text/javascript">
<![CDATA[

function select_all_images()
{
  var cb
  var n
  var cbs = document.getElementsByName("image-select")
  for (n=0; n<cbs.length; n++) {
    cb = cbs[n]
    cb.checked = true
  }
}

function unselect_all_images()
{
  var cb
  var n
  var cbs = document.getElementsByName("image-select")
  for (n=0; n<cbs.length; n++) {
    cb = cbs[n]
    cb.checked = false
  }
}

function download_selected_images()
{
  var cb
  var n
  var cbs = document.getElementsByName("image-select")
  for (n=0; n<cbs.length; n++) {
    cb = cbs[n]
    if (cb.checked) {
      alert("downloading "+cb.value)
    }
  }
}

]]>
</script>
        </xsl:if>
        <title>
          <xsl:value-of select="@name"/>
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
        <span class="page-title"><xsl:value-of select="@name"/></span>
        <div class="picturedir">
          <xsl:apply-templates select="updir"/>
          <xsl:comment>
            <xsl:text> We have </xsl:text>
            <xsl:value-of select="count(dirs/dir)"/>
            <xsl:text> folders </xsl:text>
          </xsl:comment>
          <xsl:apply-templates select="dirs"/>
          <xsl:comment>
            <xsl:text> We have </xsl:text>
            <xsl:value-of select="count(images/image)"/>
            <xsl:text> images </xsl:text>
          </xsl:comment>
          <xsl:apply-templates select="images"/>
          <xsl:if test="count(images/image) &gt; $repeatDirsAfterNImages">
            <xsl:apply-templates select="dirs"/>
            <xsl:apply-templates select="updir"/>
          </xsl:if>
        </div>
        <div class="footer">
          <xsl:text>Generated by </xsl:text>
          <xsl:element name="a">
            <xsl:attribute name="href">
              <xsl:text>http://adelie.cx/static-picture-publish/</xsl:text>
            </xsl:attribute>
            <xsl:attribute name="target">
              <xsl:text>_blank</xsl:text>
            </xsl:attribute>
            <xsl:text>static-picture-publish</xsl:text>
            <xsl:text> </xsl:text>
            <xsl:value-of select="@version"/>
          </xsl:element>
        </div>
      </body>
    </html>
  </xsl:template>


  <xsl:template name="doDownloads">
    <xsl:if test="$doDownloads = 'yes'">
      <table class="downloads-table">
        <tr>
          <td width="33%" class="download-table-cell">
            <button class="download-button" type="submit"
                    onclick="select_all_images()">Select all images</button>
          </td>
          <td width="33%" class="download-table-cell">
            <button class="download-button" type="submit"
                    onclick="unselect_all_images()">Unselect all images</button>
          </td>
          <td width="33%" class="download-table-cell">
            <button class="download-button" type="submit"
                    onclick="download_selected_images()">Download selected images</button>
          </td>
        </tr>
      </table>
    </xsl:if>
  </xsl:template>


  <xsl:template match="updir">
    <table class="updir-table">
      <tr>
        <td width="100%" class="updir-table-cell">
          <xsl:text>[</xsl:text>
          <xsl:choose>
            <xsl:when test="$imagePageExtension = '.xml'">
              <xsl:element name="a">
                <xsl:attribute name="href">
                  <xsl:text>../index.xml</xsl:text>
                </xsl:attribute>
                <xsl:text>Go up one folder</xsl:text>
              </xsl:element>
            </xsl:when>
            <xsl:otherwise>
              <xsl:element name="a">
                <xsl:attribute name="href">
                  <xsl:text>..</xsl:text>
                </xsl:attribute>
                <xsl:text>Go up one folder</xsl:text>
              </xsl:element>
            </xsl:otherwise>
          </xsl:choose>
          <xsl:text>]</xsl:text>
        </td>
      </tr>
    </table>
    <!-- xsl:apply-templates/ -->
  </xsl:template>

  <xsl:template match="/picturedir/dirs">
    <xsl:if test="count(dir) != 0">
      <span class="dir-list-title">Folders</span>
      <table class="dir-table">
        <xsl:attribute name="summary">
          <xsl:text>Folder list</xsl:text>
        </xsl:attribute>
        <xsl:for-each select="dir[ position() mod $nTableCells = 1 ]">
          <tr class="dir-table-row">
            <xsl:for-each select=". | following-sibling::dir[position()&lt;$nTableCells]">
              <xsl:call-template name="dirtemplate">
                <!-- <xsl:with-param name="p"> -->
                  <!-- <xsl:value-of select="position()"/> -->
                <!-- </xsl:with-param> -->
              </xsl:call-template>
            </xsl:for-each>
          </tr>
        </xsl:for-each>
      </table>
    </xsl:if>
  </xsl:template>

  <xsl:template name="dirtemplate">
    <xsl:element name="td">
      <xsl:attribute name="class">
        <xsl:text>dir-table-cell</xsl:text>
      </xsl:attribute>
      <xsl:attribute name="width">
        <xsl:value-of select="100 div $nTableCells" /><xsl:text>%</xsl:text>
      </xsl:attribute>
      <xsl:choose>
        <xsl:when test="$imagePageExtension = '.xml'">
          <xsl:element name="a">
            <xsl:attribute name="href">
              <xsl:value-of select="name"/>
              <xsl:text>/index.xml</xsl:text>
            </xsl:attribute>
            <xsl:value-of select="name"/>
          </xsl:element>
        </xsl:when>
        <xsl:otherwise>
          <xsl:element name="a">
            <xsl:attribute name="href">
              <xsl:value-of select="name"/>
            </xsl:attribute>
            <xsl:value-of select="name"/>
          </xsl:element>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:element>
    <!-- <xsl:apply-templates/ -->
  </xsl:template>

  <xsl:template match="/picturedir/images">
    <xsl:if test="count(image) != 0">
      <span class="thumbnail-list-title">Images</span>
      <xsl:if test="count(image) &gt; $repeatDirsAfterNImages">
        <xsl:call-template name="doDownloads" />
      </xsl:if>
      <table class="thumbnail-table">
        <xsl:attribute name="summary">
          <xsl:text>Thumbnail list</xsl:text>
        </xsl:attribute>
        <xsl:for-each select="image[ position() mod $nTableCells = 1 ]">
          <tr class="thumbnail-table-row">
            <xsl:for-each select=". | following-sibling::image[position()&lt;$nTableCells]">
              <xsl:call-template name="imagetemplate">
                <!-- <xsl:with-param name="p"> -->
                  <!-- <xsl:value-of select="position()"/> -->
                <!-- </xsl:with-param> -->
              </xsl:call-template>
            </xsl:for-each>
          </tr>
        </xsl:for-each>
      </table>
      <xsl:call-template name="doDownloads" />
    </xsl:if>
  </xsl:template>


  <xsl:template name="imagetemplate">
    <xsl:element name="td">
      <xsl:attribute name="class">
        <xsl:text>thumbnail-table-cell</xsl:text>
      </xsl:attribute>
      <xsl:attribute name="width">
        <xsl:value-of select="100 div $nTableCells" /><xsl:text>%</xsl:text>
      </xsl:attribute>
      <xsl:element name="div">
        <xsl:attribute name="class">
          <xsl:text>thumbnail-image</xsl:text>
        </xsl:attribute>
        <xsl:element name="a">
          <xsl:attribute name="name">
            <xsl:value-of select="name"/>
            <xsl:value-of select="ext"/>
          </xsl:attribute>
        </xsl:element>
        <xsl:element name="a">
          <xsl:attribute name="href">
            <xsl:value-of select="name"/>
            <xsl:value-of select="$imagePageExtension"/>
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
            <xsl:value-of select="$imagePageExtension"/>
          </xsl:attribute>
          <xsl:value-of select="name"/>
          <xsl:value-of select="ext"/>
        </xsl:element>
      </xsl:element>
      <xsl:if test="$doDownloads = 'yes'">
        <!-- Box for selecting a download. -->
        <span class="download-text">
          <xsl:text>Select for download: </xsl:text>
        </span>
        <xsl:element name="input">
          <xsl:attribute name="type">checkbox</xsl:attribute>
          <xsl:attribute name="name">image-select</xsl:attribute>
          <xsl:attribute name="value">
            <xsl:value-of select="name" />
            <xsl:text>-full</xsl:text>
            <xsl:value-of select="ext" />
          </xsl:attribute>
          <xsl:text>WTF</xsl:text>
        </xsl:element>
      </xsl:if>
    </xsl:element>
    <!-- xsl:apply-templates/ -->
  </xsl:template>

</xsl:stylesheet>

<!-- arch-tag: ca508c04-650d-4965-bb7f-b40d0538b849
-->

