# Retrieve image comments from the file system, as stored by other programs.

from xml.sax.handler import ContentHandler
from xml.sax import parse as xml_sax_parse
from os.path import basename, dirname, isfile, join
from gzip import GzipFile

__all__ = ['getImageComment']

# Content handler for gthumb .comment files.
class GthumbContentHandler(ContentHandler):
    def __init__(self):
        self.inNote = False
        self.note = None
    def startElement(self, name, attrs):
        if name == 'Note':
            self.inNote = True
    def endElement(self, name):
        if name == 'Note':
            self.inNote = False
    def characters(self, content):
        if self.inNote:
            if self.note:
                self.note += content
            else:
                self.note = content


def getGthumbComment(imageName):
    dirName = dirname(imageName)
    xmlName = join(dirName, '.comments', basename(imageName)+'.xml')
    if isfile(xmlName):
        gf = GzipFile(xmlName)
        h = GthumbContentHandler()
        xml_sax_parse(gf, h)
        return h.note
    else:
        return None


def getImageComment(imageName):
    gthumbComment = getGthumbComment(imageName)
    return gthumbComment


# This section is for emacs.
# Local variables: ***
# mode:python ***
# py-indent-offset:4 ***
# fill-column:100 ***
# End: ***
# arch-tag: d33b8f10-07b2-4fd2-8fc5-be4211746043