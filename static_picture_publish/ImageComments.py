# Retrieve image comments from the file system, as stored by other programs.

from xml.sax.handler import ContentHandler
from xml.sax import parse as xml_sax_parse
from os.path import basename, dirname, expanduser, isfile, join
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
    if dirName[0] == '/':
        relativeDirName = dirName[1:]
    else:
        relativeDirName = dirName
    xmlName1 = join(dirName, '.comments', basename(imageName)+'.xml')
    xmlName2 = expanduser(join('~/.gnome2/gthumb/comments',
                               relativeDirName, basename(imageName)+'.xml'))
    for name in (xmlName1, xmlName2):
        if isfile(name):
            #print "Found %s" % name
            gf = GzipFile(name)
            h = GthumbContentHandler()
            xml_sax_parse(gf, h)
            return h.note
    return None


def getImageComment(imageName):
    gthumbComment = getGthumbComment(imageName)
    return gthumbComment


# This section is for emacs.
# Local variables: ***
# mode:python ***
# py-indent-offset:4 ***
# fill-column:95 ***
# End: ***
