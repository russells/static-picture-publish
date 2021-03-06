<?xml version="1.0"?> <!-- -*- mode:sgml; indent-tabs-mode:nil -*- -->

<!-- Directory display for static-picture-publish. -->
<!-- Russell Steicke, 2006 -->
<!-- http://adelie.cx/static-picture-publish -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

<!--
Enabling these extra output attributes results in firefox (at least) not
being able to display the translated html when it does the XSLT itself.

  <xsl:output method="xml" omit-xml-declaration="yes"
  doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN"
  doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"/>
-->
  <xsl:output method="html"/>

  <xsl:template match="*"/>

  <xsl:param name="nTableColumns">3</xsl:param>
  <xsl:param name="imagePageExtension">.xml</xsl:param>
  <xsl:param name="repeatDirsAfterNImages">9</xsl:param>

  <!-- This is the text to put on the end of directory links. -->
  <!-- If we're in xml mode, it's "/index.xml", otherwise "/". -->
  <xsl:variable name="directoryLinkEnding">
    <xsl:choose>
      <xsl:when test="$imagePageExtension = '.xml'">
        <xsl:text>/index.xml</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>/</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:template match="/picturedir">
    <html>
      <head>
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
          <xsl:if test="count(updir) != 0 or count(dirs/dir) != 0">
            <hr class="table-separator folders-table" />
            <span class="dir-list-title">Folders</span>
          </xsl:if>
          <xsl:call-template name="dirnavTemplate"/>
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
            <xsl:if test="count(updir) != 0 or count(dirs/dir) != 0">
              <xsl:if test="count(dirs/dir) &lt; $repeatDirsAfterNImages">
                <hr class="table-separator folders-table" />
                <span class="dir-list-title">Folders</span>
                <xsl:call-template name="dirnavTemplate"/>
                <xsl:apply-templates select="dirs"/>
              </xsl:if>
            </xsl:if>
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


  <!-- Output a table with links to a directory. -->
  <xsl:template name="singleDirnavTemplate">
    <xsl:param name="link" /> <!-- Directory name -->
    <xsl:param name="thumbnail" />
    <xsl:param name="thumbnail-width" />
    <xsl:param name="thumbnail-height" />
    <xsl:param name="preText" />
    <xsl:param name="text" />
    <xsl:param name="postText" />

    <xsl:element name="table">
      <xsl:attribute name="align">center</xsl:attribute>
      <xsl:attribute name="cellpadding">0</xsl:attribute>
      <xsl:attribute name="cellspacing">0</xsl:attribute>
      <tr> <!-- top row -->
        <!-- top left cell -->
        <td>
          <xsl:element name="img">
            <xsl:attribute name="src">
              <xsl:value-of select="/picturedir/@stylesheetPath" />
              <xsl:text>tl1.gif</xsl:text>
            </xsl:attribute>
          </xsl:element>
        </td>
        <!-- top middle cell -->
        <xsl:element name="td">
          <xsl:attribute name="style">
            <xsl:text>background-image: url(</xsl:text>
            <xsl:value-of select="/picturedir/@stylesheetPath" />
            <xsl:text>t.gif); background-repeat: repeat-x;</xsl:text>
          </xsl:attribute>
          <xsl:element name="img">
            <xsl:attribute name="src">
              <xsl:value-of select="/picturedir/@stylesheetPath" />
              <xsl:text>tl2.gif</xsl:text>
            </xsl:attribute>
          </xsl:element>
        </xsl:element>
        <!-- top right cell -->
        <td>
          <xsl:element name="img">
            <xsl:attribute name="src">
              <xsl:value-of select="/picturedir/@stylesheetPath" />
              <xsl:text>tr.gif</xsl:text>
            </xsl:attribute>
          </xsl:element>
        </td>
      </tr>
      <tr>
        <!-- left cell -->
        <xsl:element name="td">
          <xsl:attribute name="style">
            <xsl:text>background-image: url(</xsl:text>
            <xsl:value-of select="/picturedir/@stylesheetPath" />
            <xsl:text>l.gif); background-repeat: repeat-y;</xsl:text>
          </xsl:attribute>
        </xsl:element>
        <!-- middle cell, with thumbnail -->
        <xsl:element name="td">
          <xsl:element name="a">
            <xsl:attribute name="href">
              <xsl:value-of select="$link" />
              <xsl:value-of select="$directoryLinkEnding" />
            </xsl:attribute>
            <xsl:element name="img">
              <xsl:attribute name="src">
                <xsl:value-of select="$thumbnail" />
              </xsl:attribute>
              <xsl:if test="string-length($thumbnail-width) != 0">
                <xsl:attribute name="width">
                  <xsl:value-of select="$thumbnail-width" />
                </xsl:attribute>
              </xsl:if>
              <xsl:if test="string-length($thumbnail-height) != 0">
                <xsl:attribute name="height">
                  <xsl:value-of select="$thumbnail-height" />
                </xsl:attribute>
              </xsl:if>
            </xsl:element>
          </xsl:element>
        </xsl:element>
        <!-- right cell -->
        <xsl:element name="td">
          <xsl:attribute name="style">
            <xsl:text>background-image: url(</xsl:text>
            <xsl:value-of select="/picturedir/@stylesheetPath" />
            <xsl:text>r.gif); background-repeat: repeat-y;</xsl:text>
          </xsl:attribute>
        </xsl:element>
      </tr>
      <tr>
        <!-- bottom left cell -->
        <xsl:element name="td">
          <xsl:attribute name="style">
            <xsl:text>background-image: url(</xsl:text>
            <xsl:value-of select="/picturedir/@stylesheetPath" />
            <xsl:text>bl.gif); background-repeat: repeat-y;</xsl:text>
          </xsl:attribute>
        </xsl:element>
        <!-- bottom middle cell -->
        <xsl:element name="td">
          <xsl:attribute name="style">
            <xsl:text>background-image: url(</xsl:text>
            <xsl:value-of select="/picturedir/@stylesheetPath" />
            <xsl:text>b.gif); background-repeat: repeat-x;</xsl:text>
          </xsl:attribute>
        </xsl:element>
        <!-- top right cell -->
        <td>
          <xsl:element name="img">
            <xsl:attribute name="src">
              <xsl:value-of select="/picturedir/@stylesheetPath" />
              <xsl:text>br.gif</xsl:text>
            </xsl:attribute>
          </xsl:element>
        </td>
      </tr>
      <!-- end of table -->
    </xsl:element>

    <!-- Text -->
    <p class="dir-text">
      <xsl:if test="string-length($preText) != 0">
        <xsl:value-of select="$preText" />
      </xsl:if>
      <xsl:element name="a">
        <xsl:attribute name="href">
          <xsl:value-of select="$link" />
          <xsl:value-of select="$directoryLinkEnding" />
        </xsl:attribute>
        <xsl:attribute name="title">
          <xsl:text>Go to folder: </xsl:text>
          <xsl:value-of select="$link" />
        </xsl:attribute>
        <xsl:value-of select="$text" />
      </xsl:element>
      <xsl:if test="string-length($postText) != 0">
        <xsl:value-of select="$postText" />
      </xsl:if>
    </p>
  </xsl:template>


  <!-- Create the directory navigation table. -->
  <xsl:template name="dirnavTemplate">

    <xsl:comment> start of dirnav table </xsl:comment>
    <xsl:if test="count(updir) != 0">
      <table class="dirnav-table">
        <tr>

          <!-- Navigate to previous -->
          <td width="33%" class="dirnav-table-cell">
            <xsl:choose>
              <xsl:when test="count(prev) != 0">
                <xsl:for-each select="prev[position()=1]">
                  <xsl:variable name="thumbnail">
                    <xsl:choose>
                      <xsl:when test="string-length(thumbnail) != 0">
                        <xsl:text>../</xsl:text>
                        <xsl:value-of select="name" />
                        <xsl:text>/</xsl:text>
                        <xsl:value-of select="thumbnail" />
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="/picturedir/@stylesheetPath" />
                        <xsl:text>folder-pics.gif</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                  <xsl:call-template name="singleDirnavTemplate">
                    <xsl:with-param name="link">
                      <xsl:text>../</xsl:text>
                      <xsl:value-of select="name" />
                    </xsl:with-param>
                    <xsl:with-param name="thumbnail">
                      <xsl:value-of select="$thumbnail" />
                    </xsl:with-param>
                    <xsl:with-param name="preText">
                      <xsl:text>&lt;&lt; </xsl:text>
                    </xsl:with-param>
                    <xsl:with-param name="text">
                      <xsl:value-of select="name" />
                    </xsl:with-param>
                  </xsl:call-template>
                </xsl:for-each>
              </xsl:when>
              <xsl:otherwise>
                <xsl:text disable-output-escaping="yes">&amp;nbsp;</xsl:text>
              </xsl:otherwise>
            </xsl:choose>
          </td>

          <!-- Navigate up -->
          <td width="33%" class="dirnav-table-cell">
            <xsl:call-template name="singleDirnavTemplate">
              <xsl:with-param name="link">..</xsl:with-param>
              <xsl:with-param name="thumbnail">
                <xsl:value-of select="/picturedir/@stylesheetPath" />
                <xsl:text>folder-pics.gif</xsl:text>
              </xsl:with-param>
              <xsl:with-param name="preText">
                <xsl:text>[</xsl:text>
              </xsl:with-param>
              <xsl:with-param name="text">
                <xsl:text>Go up one folder</xsl:text>
              </xsl:with-param>
              <xsl:with-param name="postText">
                <xsl:text>]</xsl:text>
              </xsl:with-param>
            </xsl:call-template>
          </td>

          <!-- Navigate to next -->
          <td width="33%" class="dirnav-table-cell">
            <xsl:choose>
              <xsl:when test="count(next) != 0">
                <xsl:for-each select="next[position()=1]">
                  <xsl:variable name="thumbnail">
                    <xsl:choose>
                      <xsl:when test="string-length(thumbnail) != 0">
                        <xsl:text>../</xsl:text>
                        <xsl:value-of select="name" />
                        <xsl:text>/</xsl:text>
                        <xsl:value-of select="thumbnail" />
                      </xsl:when>
                      <xsl:otherwise>
                        <xsl:value-of select="/picturedir/@stylesheetPath" />
                        <xsl:text>folder-pics.gif</xsl:text>
                      </xsl:otherwise>
                    </xsl:choose>
                  </xsl:variable>
                  <xsl:call-template name="singleDirnavTemplate">
                    <xsl:with-param name="link">
                      <xsl:text>../</xsl:text>
                      <xsl:value-of select="name" />
                    </xsl:with-param>
                    <xsl:with-param name="thumbnail">
                      <xsl:value-of select="$thumbnail" />
                    </xsl:with-param>
                    <xsl:with-param name="text">
                      <xsl:value-of select="name" />
                    </xsl:with-param>
                    <xsl:with-param name="postText">
                      <xsl:text> &gt;&gt;</xsl:text>
                    </xsl:with-param>
                  </xsl:call-template>
                </xsl:for-each>
              </xsl:when>
              <xsl:otherwise>
                <xsl:text disable-output-escaping="yes">&amp;nbsp;</xsl:text>
              </xsl:otherwise>
            </xsl:choose>
          </td>

        </tr>
      </table>
    </xsl:if>

    <xsl:comment> end of dirnav table </xsl:comment>
  </xsl:template>



  <xsl:template match="/picturedir/dirs">
    <xsl:if test="count(dir) != 0">

      <xsl:variable name="nRows">
        <xsl:value-of select="ceiling(count(dir) div $nTableColumns)" />
      </xsl:variable>

      <xsl:variable name="nExtraCells">
        <xsl:choose>
          <xsl:when test="(count(dir) mod $nTableColumns) = 0">0</xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$nTableColumns - (count(dir) mod $nTableColumns)" />
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <xsl:comment> nRows == <xsl:value-of select="$nRows"/> </xsl:comment>
      <xsl:comment> nExtraCells == <xsl:value-of select="$nExtraCells"/> </xsl:comment>
      <table class="dir-table">
        <xsl:attribute name="summary">
          <xsl:text>Folder list</xsl:text>
        </xsl:attribute>
        <xsl:for-each select="dir[ position() mod $nTableColumns = 1 ]">
          <tr class="dir-table-row">
            <xsl:for-each select=". | following-sibling::dir[position()&lt;$nTableColumns]">
              <td width="33%" class="dir-table-cell">
              <xsl:variable name="thisThumbnail">
                <xsl:choose>
                  <xsl:when test="string-length(thumbnail) != 0">
                    <xsl:value-of select="name" />
                    <xsl:text>/</xsl:text>
                    <xsl:value-of select="thumbnail" />
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="/picturedir/@stylesheetPath" />
                    <xsl:text>folder-pics.gif</xsl:text>
                  </xsl:otherwise>
                </xsl:choose>
              </xsl:variable>
              <!-- <xsl:call-template name="dirtemplate" /> -->
              <xsl:call-template name="singleDirnavTemplate">
                <xsl:with-param name="link">
                  <xsl:value-of select="name" />
                </xsl:with-param>
                <xsl:with-param name="text">
                  <xsl:value-of select="name" />
                </xsl:with-param>
                <xsl:with-param name="thumbnail">
                  <xsl:value-of select="$thisThumbnail" />
                </xsl:with-param>
                <xsl:with-param name="thumbnail-width">
                  <xsl:value-of select="thumbnail/@width" />
                </xsl:with-param>
                <xsl:with-param name="thumbnail-height">
                  <xsl:value-of select="thumbnail/@height" />
                </xsl:with-param>
              </xsl:call-template>
              </td>
            </xsl:for-each>
            <!-- If we just did the last row, and we require extra cells, -->
            <!-- then fill in the table with blank cells -->
            <xsl:comment> position() == <xsl:value-of select="position()"/> </xsl:comment>
            <xsl:if test="position() = $nRows">
              <xsl:if test="$nExtraCells != 0">
                <xsl:call-template name="emptyCellTemplate">
                  <xsl:with-param name="i">1</xsl:with-param>
                  <xsl:with-param name="n">
                    <xsl:value-of select="$nExtraCells" />
                  </xsl:with-param>
                  <xsl:with-param name="className">
                    <xsl:text>dir-table-cell</xsl:text>
                  </xsl:with-param>
                </xsl:call-template>
              </xsl:if>
            </xsl:if>
          </tr>
        </xsl:for-each>
      </table>
    </xsl:if>
  </xsl:template>

  <xsl:template name="emptyCellTemplate">
    <xsl:param name="i" />
    <xsl:param name="n" />
    <xsl:param name="className" />
    <xsl:if test="$i &lt;= $n">
      <xsl:element name="td">
        <xsl:attribute name="class">
          <xsl:value-of select="$className" />
        </xsl:attribute>
        <xsl:attribute name="width">
          <xsl:value-of select="format-number(1 div $nTableColumns, '#%')" />
        </xsl:attribute>
        <xsl:text disable-output-escaping="yes">&amp;nbsp;</xsl:text>
        <xsl:comment> Extra cell </xsl:comment>
      </xsl:element>
      <xsl:call-template name="emptyCellTemplate">
        <xsl:with-param name="i">
          <xsl:value-of select="$i + 1" />
        </xsl:with-param>
        <xsl:with-param name="n">
          <xsl:value-of select="$n" />
        </xsl:with-param>
        <xsl:with-param name="className">
          <xsl:value-of select="$className" />
        </xsl:with-param>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>


  <xsl:template match="/picturedir/images">
    <xsl:if test="count(image) != 0">

      <xsl:variable name="nRows">
        <xsl:value-of select="ceiling(count(image) div $nTableColumns)" />
      </xsl:variable>

      <xsl:variable name="nExtraCells">
        <xsl:choose>
          <xsl:when test="(count(image) mod $nTableColumns) = 0">0</xsl:when>
          <xsl:otherwise>
            <xsl:value-of select="$nTableColumns - (count(image) mod $nTableColumns)" />
          </xsl:otherwise>
        </xsl:choose>
      </xsl:variable>

      <hr class="table-separator images-table" />
      <span class="thumbnail-list-title">Images</span>
      <table class="thumbnail-table">
        <xsl:attribute name="summary">
          <xsl:text>Thumbnail list</xsl:text>
        </xsl:attribute>
        <xsl:for-each select="image[ position() mod $nTableColumns = 1 ]">
          <tr class="thumbnail-table-row">
            <xsl:for-each select=". | following-sibling::image[position()&lt;$nTableColumns]">
              <xsl:call-template name="imagetemplate">
                <!-- <xsl:with-param name="p"> -->
                  <!-- <xsl:value-of select="position()"/> -->
                <!-- </xsl:with-param> -->
              </xsl:call-template>
            </xsl:for-each>
            <!-- If we just did the last row, and we require extra cells, -->
            <!-- then fill in the table with blank cells -->
            <xsl:comment> position() == <xsl:value-of select="position()"/> </xsl:comment>
            <xsl:if test="position() = $nRows">
              <xsl:if test="$nExtraCells != 0">
                <xsl:call-template name="emptyCellTemplate">
                  <xsl:with-param name="i">1</xsl:with-param>
                  <xsl:with-param name="n">
                    <xsl:value-of select="$nExtraCells" />
                  </xsl:with-param>
                  <xsl:with-param name="className">
                    <xsl:text>thumbnail-table-cell</xsl:text>
                  </xsl:with-param>
                </xsl:call-template>
              </xsl:if>
            </xsl:if>
          </tr>
        </xsl:for-each>
      </table>
    </xsl:if>
  </xsl:template>


  <xsl:template name="imagetemplate">
    <xsl:element name="td">
      <xsl:attribute name="class">
        <xsl:text>thumbnail-table-cell</xsl:text>
      </xsl:attribute>
      <xsl:attribute name="width">
        <xsl:value-of select="format-number(1 div $nTableColumns, '#%')" />
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

        <!-- start of image anchor -->
        <xsl:element name="a">
          <xsl:attribute name="href">
            <xsl:value-of select="name"/>
            <xsl:value-of select="$imagePageExtension"/>
          </xsl:attribute>

          <!-- start of image -->
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
            <xsl:if test="string-length(size/@width) != 0">
              <xsl:attribute name="width">
                <xsl:value-of select="size/@width" />
              </xsl:attribute>
            </xsl:if>
            <xsl:if test="string-length(size/@height) != 0">
              <xsl:attribute name="height">
                <xsl:value-of select="size/@height" />
              </xsl:attribute>
            </xsl:if>
            <xsl:attribute name="title">
              <xsl:text>View larger image</xsl:text>
            </xsl:attribute>
          </xsl:element>
          <!-- end of image -->

        </xsl:element>
        <!-- end of image anchor -->

      </xsl:element>

      <!-- start of image name anchor -->
      <xsl:element name="div">
        <xsl:attribute name="class">
          <xsl:text>thumbnail-text</xsl:text>
        </xsl:attribute>
        <xsl:element name="a">
          <xsl:attribute name="href">
            <xsl:value-of select="name"/>
            <xsl:value-of select="$imagePageExtension"/>
          </xsl:attribute>
          <xsl:attribute name="title">
            <xsl:text>View larger image</xsl:text>
          </xsl:attribute>
          <xsl:value-of select="name"/>
          <xsl:value-of select="ext"/>
        </xsl:element>
      </xsl:element>
      <!-- end of image name anchor -->

      <xsl:if test="string-length(comment) != 0">
        <div class="imagecomment-dir">
          <xsl:value-of select="comment" />
        </div>
      </xsl:if>

      <xsl:element name="div">
        <xsl:attribute name="class">
          <xsl:text>download-link</xsl:text>
        </xsl:attribute>
        <xsl:text>Full size </xsl:text>
        <xsl:if test="string-length(filesize) != 0">
          <xsl:text>(</xsl:text>
          <xsl:value-of select="filesize" />
          <xsl:text>)</xsl:text>
        </xsl:if>
        <xsl:text>: </xsl:text>

        <!-- start of download anchor -->
        <xsl:element name="a">
          <xsl:attribute name="href">
            <xsl:text>.spp-download/</xsl:text>
            <xsl:value-of select="name"/>
            <xsl:value-of select="ext"/>
          </xsl:attribute>
          <xsl:attribute name="type">
            <xsl:text>application/octet-stream</xsl:text>
          </xsl:attribute>
          <xsl:attribute name="title">
            <xsl:text>Download full-sized image</xsl:text>
            <xsl:if test="string-length(filesize) != 0">
              <xsl:text>, </xsl:text>
              <xsl:value-of select="filesize" />
            </xsl:if>
            <xsl:if test="string-length(fullsize/@width) != 0 and string-length(fullsize/@height) != 0">
              <xsl:text>, </xsl:text>
              <xsl:value-of select="fullsize/@width" />
              <xsl:text>x</xsl:text>
              <xsl:value-of select="fullsize/@height" />
              <xsl:text> pixels</xsl:text>
            </xsl:if>
          </xsl:attribute>
          <xsl:text>download</xsl:text>
        </xsl:element>
        <!-- end of download anchor -->

      </xsl:element>
    </xsl:element>
  </xsl:template>

</xsl:stylesheet>


