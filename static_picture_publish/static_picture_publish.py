#!/usr/bin/python

from sys import argv, exit, path as syspath, stderr
from os import getcwd, listdir, makedirs, readlink, rmdir, stat, symlink, \
     system, unlink
from os.path import abspath, basename, exists as pathexists, isdir, isfile, islink, \
     join as pathjoin, normpath, split as pathsplit, splitext
from optparse import Option, OptionGroup, OptionParser, OptionValueError
from copy import copy
import Image
from errno import EEXIST, ENOENT
from StringIO import StringIO
from string import join as stringjoin
from time import time
from shutil import copyfile
from ConfigParser import ConfigParser

# init the random number generator.
from random import randint, seed
seed()

# XSLT processing
from Ft.Lib.Uri import OsPathToUri
from Ft.Xml import InputSource
from Ft.Xml.Xslt import Processor

from ImageComments import getImageComment



defaultExtensions = '.jpg,.jpeg,.gif,.png'
defaultImagesPerRow = 3


class SppOption(Option):
    '''Extend OptionParser to parse image dimension specifications (AxB).'''

    def check_intpair(option, opt, value):
        intstrs = value.split('x')
        try:
            if len(intstrs) == 1:
                i = int(intstrs[0])
                ints = (i,i)
            elif len(intstrs) == 2:
                ints = ( int(intstrs[0]), int(intstrs[1]) )
            else:
                raise OptionValueError(
                    "option %s: Must be an integer or integer pair AxB: %r" % \
                    (opt, value))
        except ValueError,reason:
            raise OptionValueError(
                "option %s: not an integer or integer pair: %s" % (opt, value))
        return ints

    TYPES = Option.TYPES + ("intpair",)
    TYPE_CHECKER = copy(Option.TYPE_CHECKER)
    TYPE_CHECKER["intpair"] = check_intpair


opt = OptionParser(
option_class=SppOption,
version="%prog 0.1",
usage=
'Usage: %prog [options] picdir webdir.\n'
'  Recursively publish pics from picdir into webdir\n'
'\n'
'  Directories and pics from picdir will be mirrored into webdir, as\n'
'  thumbnails and small copies.  Symlinks will be used to point to the\n'
'  originals in picdir.\n'
'\n'
'  %prog can be run multiple times with the same picdir\n'
'  and webdir.  Pre-existing content in picdir that is still current will\n'
'  not have its webdir output regenerated.  Directories and images in picdir\n'
'  that no longer exist will have their equivalents removed from webdir.')

opt.add_option('-q','--quiet',
               action='store_true',
               help='Don\'t print any output')
opt.add_option('-v','--verbose',
               action='store_true',
               help='Print more information about actions')

image_opts = OptionGroup(opt, "Image options")
image_opts.add_option(
    '-c','--copy',
    action='store_true',
    help='Copy originals instead of symlinking')
image_opts.add_option(
    '-e','--extensions',
    action='store',
    help='Comma-separated list of file extensions to use.  '
    'These are compared case-insenstiively.  '
    '(Default is "%s").  ' % defaultExtensions)
image_opts.add_option(
    '-n','--no-originals',
    action='store_true',
    help='Don\'t symlink or copy originals')
image_opts.add_option(
    '-s','--image-size',
    type='intpair',
    action='store',
    help='Set maximum dimension for images (Default 640x640 pixels)')
image_opts.add_option(
    '-z','--thumbnail-size',
    type='intpair',
    action='store',
    help='Set maximum dimension for thumbnails '
    '(Default 128x128 pixels)')
opt.add_option_group(image_opts)

markup_opts = OptionGroup(opt, "Markup options")
markup_opts.add_option(
    '-g','--regen-markup',
    action='store_true',
    help='Force regeneration of HTML or XML output')
markup_opts.add_option(
    '-N','--no-html',
    action='store_true',
    help='Don\'t create HTML from XML')
markup_opts.add_option(
    '-r','--regen-all',
    action='store_true',
    help='Force regeneration of all output')
markup_opts.add_option(
    '-S', '--subdir',
    action='store_true',
    help='Run as if in a subdirectory of the output directory')
markup_opts.add_option(
    '-t','--title',
    type='string',
    action='store',
    help='Set the HTML title')
opt.add_option_group(markup_opts)

layout_opts = OptionGroup(opt, "Layout options")
layout_opts.add_option(
    '--css',
    action='store',
    #metavar="css_file",
    help='CSS style to use in HTML or XML output. (Default "plain").'
    ' The file "spp-<style>.css" or equivalent will be used, and renamed "spp.css".')
layout_opts.add_option(
    '--row',
    type='int',
    action='store',
    help='Number of images per row in HTML. (Default 3)')
layout_opts.add_option(
    '--xsl-dir',
    action='store',
    help='XSLT file to use for directory XML output. (Default inbuilt)')
layout_opts.add_option(
    '--xsl-image',
    action='store',
    help='XSLT file to use for image XML output. (Default inbuilt)')

opt.add_option_group(layout_opts)

other_opts = OptionGroup(opt, "Other options")
other_opts.add_option(
    '--delete',
    action='store_true',
    help="Delete unused files in the output directory.  Files and directories we have "
    "generated (or were generated on previous runs) and files called .htaccess will be "
    "kept.")
other_opts.add_option(
    '--xsltproc',
    action='store_true',
    help="Use the xsltproc program to create HTML, instead of the python XML libraries.")
opt.add_option_group(other_opts)

def parseOptions():
    global options, picRoot, webRoot, picTree, webTree
    (options, args) = opt.parse_args()
    if len(args) != 2:
        usage()
    if options.extensions:
        options.extensions = options.extensions.split(',')
    else:
        options.extensions = defaultExtensions.split(',')
    if not options.image_size:
        options.image_size = (640,640)
    if not options.thumbnail_size:
        options.thumbnail_size = (128,128)
    if options.thumbnail_size[0] > options.image_size[0] or \
       options.thumbnail_size[1] > options.image_size[1]:
        print >>stderr, "%s: warning: thumbnail (%s) is bigger than image (%s)"\
              % (str(options.thumbnail_size), str(options.image_size))
    if options.css:
        options.css_file = "css/spp-%s.css" % options.css
    else:
        options.css_file = "css/spp-plain.css"
    if options.xsl_dir:
        options.xsl_dir_file = "xsl/spp-dir-%s.xsl" % options.xsl_dir
    else:
        options.xsl_dir_file = "xsl/spp-dir-plain.xsl"
    if options.xsl_image:
        options.xsl_image_file = "xsl/spp-image-%s.xsl" % options.xsl_image
    else:
        options.xsl_image_file = "xsl/spp-image-plain.xsl"
    options.messageLevel = 1
    if options.verbose:
        options.messageLevel = 2
    if options.quiet:
        options.messageLevel = 0
    if not options.row:
        options.row = defaultImagesPerRow
    if not options.title:
        options.title = 'Pics'
    picRoot = args[0]
    webRoot = args[1]
    if abspath(picRoot) == abspath(webRoot):
        print >>stderr, "%s: cannot publish into source directory: %s" \
              % (argv[0], abspath(picRoot))
        exit(1)


def usage(errcode=1):
    opt.print_help(stderr)
    exit(errcode)


def message(msg, level=1):
    if level <= options.messageLevel:
        print msg


def verboseMessage(msg):
    message(msg, 2)


entityChars = {
    '&'  : "&amp;",
    '<'  : "&lt;",
    '>'  : "&gt;",
    '\'' : "&apos;",
    '"'  : "&quot;",
    ';'  : "&#59;",
    # '#' needs to be escaped as it is used to indicate an anchor in a page.
    '#'  : '%23',
    # '?' indicates CGI arguments (or whatever they're really called).
    '?'  : '%3f',
    }


def entityReplace(s):
    '''Replace the characters "&<>\'" with html entities.'''
    r = StringIO()
    for c in s:
        if c in entityChars:
            r.write(entityChars[c])
        else:
            r.write(c)
    s2 = r.getvalue()
    r.close()
    return s2


class Picture(dict):
    '''Process one pic.'''
    def __init__(self, picName, picDirName, webDirName, dirName, configEntry,
                 stylesheetPath=None):
        self['picName'] = picName          # file name only
        self['picDirName'] = picDirName    # path to pic dir
        self['webDirName'] = webDirName    # path to web dir
        self['dirName'] = dirName          # path to either dir, relative to root
        self['configEntry'] = configEntry
        self['stylesheetPath'] = stylesheetPath
        self['picPath'] = pathjoin(picDirName, picName)
        (base, ext) = splitext(self['picName'])
        self['picNameBase'] = base
        self['picNameExt'] = ext
        self['imageName'] = picName
        self['fullImageName'] = pathjoin('.spp-full', picName)
        self['downloadImageName'] = pathjoin('.spp-download', picName)
        self['imagePath'] = pathjoin(webDirName, self['imageName'])
        self['thumbnailName'] = base + "-thumb" + ext
        self['thumbnailPath'] = pathjoin(webDirName, self['thumbnailName'])
        self['htmlName'] = base + ".html"
        self['htmlPath'] = pathjoin(webDirName, self['htmlName'])
        self['xmlName'] = base + ".xml"
        self['xmlPath'] = pathjoin(webDirName, self['xmlName'])
        self['htmlName'] = base + ".html"
        self['htmlPath'] = pathjoin(webDirName, self['htmlName'])
        self['comment'] = getImageComment(pathjoin(picRoot, dirName, picName))
        self['rotateDone'] = False      # Set to true when we've checked the rotate stuff.
        # If we were supplied a path to the CSS and XSL files, then we use that.  Otherwise,
        # calculate the path by going up until we get to the top.
        if stylesheetPath:
            self['xslPath'] = pathjoin(stylesheetPath, 'spp-image.xsl')
            self['cssPath'] = pathjoin(stylesheetPath, 'spp.css')
        else:
            if self['dirName'] == '':
                self['xslPath'] = 'spp-image.xsl'
                self['cssPath'] = 'spp.css'
            else:
                self['xslPath'] = '../spp-image.xsl'
                self['cssPath'] = '../spp.css'
                ht = pathsplit(self['dirName'])[0]
                #print "self['dirName'] == %s" % self['dirName']
                while len(ht) != 0 and ht != '/':
                    #print 'ht is %s' % str(ht)
                    self['xslPath'] = '../' + self['xslPath']
                    self['cssPath'] = '../' + self['cssPath']
                    ht = pathsplit(ht)[0]


    def go(self, prevPic, nextPic):
        '''Create the output files (thumbnail, image and html).'''

        if not options.regen_all:
            picStat = stat(self['picPath'])

        modified = False
        image = None
        try:
            # Open the image so we can read the size and stuff.
            image = Image.open(self['picPath'])
            self['fullImageWidth'] = image.size[0]
            self['fullImageHeight'] = image.size[1]
            bytes = stat(self['picPath']).st_size
            self['fullImageSize'] = self.readableSize(bytes)

            # Create the web image, if necessary.
            if options.regen_all \
                   or not fileIsNewer(self['imagePath'], picStat) \
                   or not self.imageSizeCheck('image', options.image_size):
                #print "Regenerating %s" % self['imagePath']
                image = self.generateImage('image', options.image_size, image)
                modified = True
            # Create the thumbnail, if necessary.
            if options.regen_all \
                   or not fileIsNewer(self['thumbnailPath'], picStat) \
                   or not self.imageSizeCheck('thumbnail', options.thumbnail_size):
                #print "Regenerating %s" % self['thumbnailPath']
                image = self.generateImage('thumbnail', options.thumbnail_size, image)
                modified = True
            image = None                # gc
        # Should we handle Exception here, instead of listing the ones that have been seen so
        # far?  If we get one more to add to this list, then do that instead.
        except (IOError, SystemError, IndexError), reason:
            print >>stderr, "%s: error processing %s: %s" % \
                  (argv[0], self['picPath'], str(reason.args))
        self.createMarkup(prevPic, nextPic)
        for n in ['image', 'thumbnail']:
            self[n+'-image'] = None
        return modified


    def readableSize(self, bytes):
        if bytes >= 10485760:
            return "%1.0f MB" % (bytes / 1048576.0)
        elif bytes >= 1048576:
            return "%3.1f MB" % (bytes / 1048576.0)
        elif bytes >= 10240:
            return "%1.0f kB" % (bytes / 1024.0)
        elif bytes >= 1024:
            return "%3.1f kB" % (bytes / 1024.0)
        else:
            return "%d bytes" % bytes


    def imageSizeCheck(self, image_basename, requiredSize):
        '''Check to see if the output image is the correct size.

        Return True if the size is correct, false otherwise.'''
        imagePath = self[image_basename+'Path']
        imageKeyName = image_basename+'-image'
        try:
            if not self.has_key(imageKeyName) or not self[imageKeyName]:
                im = Image.open(imagePath)
            self[image_basename+'-image'] = im
            self[image_basename+'-width']  = im.size[0]
            self[image_basename+'-height'] = im.size[1]
            if  im.size[0] > requiredSize[0] or \
                im.size[1] > requiredSize[1] or \
                (im.size[0] < requiredSize[0] and im.size[1] < requiredSize[1]):
                flag = False
            else:
                flag = True
        except IOError, reason:
            print >>stderr, "%s: error opening %s, it will be regenerated" % \
                  (argv[0], imagePath)
            print >>stderr, "%s" % str(reason.args)
            self[image_basename+'-width']  = None
            self[image_basename+'-height'] = None
            self[image_basename+'-image'] = None
            flag = False
        #print "%s: size:%s required:%s flag:%s" % (imagePath, str(smallimage.size),
        #str(requiredSize), str(flag))
        return flag


    def generateImage(self, image_basename, imageSize, image):
        '''Make an output image.'''

        # Check for image rotation here, so we don't have to do it unnecessarily if we're not
        # actually going to write an image.
        if not self['rotateDone']:
            self['rotateDone'] = True
            angle = self.getRotateAngle(image)
            if angle:
                message(" -- Rotating %s: %s" % (self['picPath'], self.imageRotateDict[angle]))
                image = image.transpose(angle)

        imagePath = self[image_basename+'Path']
        verboseMessage("  %s => %s" % (self['picPath'], imagePath))
        starttime = time()
        image.thumbnail(imageSize, Image.ANTIALIAS)
        self[image_basename+'-width']  = image.size[0]
        self[image_basename+'-height'] = image.size[1]
        image.save(imagePath)
        endtime = time()
        verboseMessage("  generation time %s: %.2f" % (imagePath, endtime-starttime))
        modified = True
        # Return the image in case we're rotated it.  This substantially reduces the run time
        # when the output images have already been generated.
        return image


    # Dictionaries for converting between angles, strings and PIL constants.  Currently we only
    # handle the three simple rotation cases, although the others could be easily handled with
    # a combination of rotate and flip.  There probably aren't any digital cameras that need
    # the other cases.
    orientationDict = { 1:None, 2:None, 3:Image.ROTATE_180, 4:None,
                        5:None, 6:Image.ROTATE_270, 7:None, 8:Image.ROTATE_90 }
    angleDict = { '90':Image.ROTATE_90, '180':Image.ROTATE_180, '270':Image.ROTATE_270,
                  '-90':Image.ROTATE_270,
                  'left':Image.ROTATE_90, 'right':Image.ROTATE_270,
                  'upsidedown':Image.ROTATE_180 }
    angleStrings = "90, 180, 270, -90, left, right or upsidedown"
    imageRotateDict = { Image.ROTATE_90:'left', Image.ROTATE_180:'upsidedown',
                        Image.ROTATE_270:'right', }


    def getRotateAngle(self, image):
        '''Find out how we should rotate the image.'''
        angle = None
        if self['configEntry'].has_key('rotate'):
            # If the user specifies a valid value, use that.
            try:
                angleString = self['configEntry']['rotate'].lower()
                angle = self.angleDict[angleString]
            except KeyError, reason:
                print >>stderr, "%s: rotate value '%s' for %s is not one of %s" % \
                      (argv[0], angleString, pathjoin(self['dirName'], self['picName']),
                       self.angleStrings)
                angle = None
        if angle == None and hasattr(image, '_getexif'):
            # PIL 1.1.4 and above have experimental EXIF code, but it seems a bit flaky still.
            try:
                ex = image._getexif()
            except KeyError, reason:
                verboseMessage("%s contains no EXIF data" % (self['picName']))
                pass
            except Exception, reason:
                print >>stderr, "Error reading EXIF data for %s: %s" % \
                      (self['picName'], str(reason))
            else:
                if ex and ex.has_key(0x112):
                    orientation = ex[0x112]
                    try:
                        angle = self.orientationDict[orientation]
                    except KeyError, reason:
                        print >>stderr, "%s: unknown orientation value %s in image %s" % \
                              (argv[0], str(orientation),
                               pathjoin(self['dirName'], self['picName']))
        return angle


    def createMarkup(self, prevPic, nextPic):
        x = file(self['xmlPath'], "w")
        s = StringIO()
        s.write(
            '<?xml version="1.0"?>\n'+\
            '<?xml-stylesheet type="text/xsl" href="%s"?>\n' % self['xslPath']+\
            '<picinfo css="%s">\n' % self['cssPath'])
        if options.title:
            s.write(' <title>%s</title>\n' %  entityReplace(options.title))
        s.write(
            ' <this>\n'+\
            '  <name>%s</name>\n' % entityReplace(self['picNameBase'])+\
            '  <ext>%s</ext>\n' % entityReplace(self['picNameExt']))
        if self.has_key('image-width'):
            s.write('  <size width="%d" height="%d" />\n' % \
                    (self['image-width'],self['image-height']))
        if self.has_key('fullImageWidth') and self.has_key('fullImageHeight'):
            s.write('  <fullsize width="%d" height="%d" />\n' % \
                    (self['fullImageWidth'], self['fullImageHeight']))
        if self.has_key('fullImageSize'):
            s.write('  <filesize>%s</filesize>\n' % self['fullImageSize'])
        else:
            s.write('  <!-- no image width -->\n')
        if self['comment']:
            comment = self['comment']
            if len(comment) > 295:
                comment = comment[:295]+'...'
            s.write('  <comment>%s</comment>\n' % entityReplace(comment))
        s.write(' </this>\n')
        if prevPic is not None:
            s.write(
                ' <prev>\n'+\
                '  <name>%s</name>\n' % entityReplace(prevPic['picNameBase'])+\
                '  <ext>%s</ext>\n' % entityReplace(prevPic['picNameExt'])+\
                ' </prev>\n')
        if nextPic is not None:
            s.write(
                ' <next>\n'+\
                '  <name>%s</name>\n' % entityReplace(nextPic['picNameBase'])+\
                '  <ext>%s</ext>\n' % entityReplace(nextPic['picNameExt'])+\
                ' </next>\n')
        s.write('</picinfo>\n')
        x.write(s.getvalue())
        s.close()
        x.close()
        if not options.no_html:
            if options.xsltproc:
                cmd = 'cd %s && xsltproc ' \
                      '--param imagePageExtension \'".html"\' ' \
                      '-o %s %s' % (shellEscape(self['webDirName']),
                                    shellEscape(self['htmlName']),
                                    shellEscape(self['xmlName']))
                verboseMessage('Command: %s' % cmd)
                system(cmd)
            else:
                verboseMessage('Creating %s' % pathjoin(self['webDirName'], self['htmlName']))
                styuri = OsPathToUri(abspath(pathjoin(webRoot, self['dirName'],
                                                      self['xslPath'])))
                verboseMessage("stylesheet URI: %s" % styuri)
                srcuri = OsPathToUri(abspath(pathjoin(webRoot, self['dirName'],
                                                      self['xmlName'])))
                verboseMessage("source     URI: %s" % srcuri)
                STY = InputSource.DefaultFactory.fromUri(styuri)
                SRC = InputSource.DefaultFactory.fromUri(srcuri)
                processor = Processor.Processor()
                processor.appendStylesheet(STY)
                result = processor.run(SRC, topLevelParams={ 'imagePageExtension':'.html' })
                htmlf = file(self['htmlPath'], 'w+')
                htmlf.write(result)
                htmlf.close()
        if not options.no_originals:
            self.createImageLink(abspath(pathjoin(self['picDirName'], self['picName'])),
                                 abspath(pathjoin(self['webDirName'], self['fullImageName'])))
            self.createImageLink(abspath(pathjoin(self['picDirName'], self['picName'])),
                                 abspath(pathjoin(self['webDirName'],
                                                  self['downloadImageName'])))


    def createImageLink(self, targetPath, symlinkPath):
        '''Create a symlink to the full image.'''

        st = None
        try:
            st = stat(symlinkPath)
        except OSError, reason:
            if reason.errno == ENOENT: pass
            else: raise
        if st is None:
            verboseMessage("symlink: %s -> %s" % (symlinkPath, targetPath))
            symlink(targetPath, symlinkPath)
        else:
            # This logic will delete relative symlinks that do point to the
            # right place, and replace them with absolute symlinks that point
            # to the same place.  The alternative is to call readlink() with
            # cwd of the symlink location, but I haven't coded that yet.
            if not islink(symlinkPath) or abspath(readlink(symlinkPath)) != targetPath:
                verboseMessage("symlink: %s -> %s" % \
                               (symlinkPath, targetPath))
                unlink(symlinkPath)
                symlink(targetPath, symlinkPath)


    def name(self):
        return self['picName']


    def __eq__(self, other): return self['picName'] == other['picName']
    def __ne__(self, other): return self['picName'] != other['picName']
    def __gt__(self, other): return self['picName'] >  other['picName']
    def __lt__(self, other): return self['picName'] <  other['picName']
    def __ge__(self, other): return self['picName'] >= other['picName']
    def __le__(self, other): return self['picName'] <= other['picName']


class PictureDir(dict):
    '''Contains information about a picture directory.'''

    # List of files to leave in the output directory.  Normally, files we don't recognise in
    # the output will be deleted, but not if they're named in here.
    filesToKeep = { '.htaccess':1, 'index.xml':1, 'index.html':1,
                    'spp.css':1, 'spp-dir.xsl':1, 'spp-image.xsl':1,
                    'tl1.gif':1, 'tl2.gif':1, 't.gif':1, 'tr.gif':1,
                    'l.gif':1, 'r.gif':1,
                    'bl.gif':1, 'b.gif':1, 'br.gif':1,
                    'empty-folder.gif':1,
                    'folder-pics.gif':1,
                    }
    # List of special subdirs to keep.  These subdirs are in the output tree, but not in the
    # source tree.
    subdirsToKeep = { '.spp-full':1, '.spp-download':1 }
    # List of files to keep in the sppSubdirsToKeep list.
    subdirFilesToKeep = { '.htaccess':1 }

    def __init__(self, picRoot, webRoot, dirName='', doUp=False, stylesheetPath=None):
        '''Search through the directory, looking for pictures and
        sub-directories.  We do not process anything yet, but wait until we
        know if the subdirs contain anything interesting.'''
        self['picRoot'] = picRoot
        self['webRoot'] = webRoot
        # dirName is relative to picRoot (and webRoot).  If dirName is '', we know we are at
        # the root.
        self['dirName'] = dirName
        # dirBasename is the name of this directory.  It is not a path name (like dirName).
        self['dirBasename'] = basename(pathjoin(picRoot,dirName))
        self['doUp'] = doUp                # If true, put "Up" link in html
        self['configEntries'] = {}

        self['dirConfig'] = ConfigParser()
        dirConfigs[self['dirName']] = self['dirConfig']
        # Grudgingly allow reading a config file with '.txt' on the end, so that Windows can
        # work out how to edit the file.  You don't need both (or either) of these files.
        # Nothing bad will happen if they don't exist.
        self['dirConfig'].read((pathjoin(self['picRoot'], self['dirName'],
                                         '.static-picture-publish'),
                                pathjoin(self['picRoot'], self['dirName'],
                                         '.static-picture-publish.txt')))

        if self['dirName']=='':
            self['picPath'] = self['picRoot']
            self['webPath'] = self['webRoot']
            self['fullLinkPath'] = pathjoin(self['webPath'], '.spp-full')
            self['downloadLinkPath'] = pathjoin(self['webPath'], '.spp-download')
        else:
            self['picPath'] = pathjoin(self['picRoot'], self['dirName'])
            self['webPath'] = pathjoin(self['webRoot'], self['dirName'])
            self['fullLinkPath'] = pathjoin(self['webPath'], '.spp-full')
            self['downloadLinkPath'] = pathjoin(self['webPath'], '.spp-download')
        self['htmlPath'] = pathjoin(self['webPath'], "index.html")
        self['xmlPath'] = pathjoin(self['webPath'], "index.xml")
        # If we were supplied a path to the CSS and XSL files, then we use that.  Otherwise,
        # calculate the path by going up until we get to the top.
        self['stylesheetPath'] = stylesheetPath
        if not self['stylesheetPath']:
            # This looks very inefficient, but it will only happen once, at the root of the
            # tree.  All the subdirectory instances will be supplied the childStylesheetPath
            # parameter, so won't have to do this search.
            self['stylesheetPath'] = ''
            if not self['dirName'] == '':
                ht = pathsplit(self['dirName'])[0]
                while ht != '':
                    self['stylesheetPath'] = pathjoin('..', self['stylesheetPath'])
                    ht = pathsplit(ht)[0]

        self['xslPath'] = pathjoin(self['stylesheetPath'], 'spp-dir.xsl')
        self['cssPath'] = pathjoin(self['stylesheetPath'], 'spp.css')
        childStylesheetPath = pathjoin('..', self['stylesheetPath'])

        self['subdirList'] = []
        self['subdirDict'] = {}
        self['picList'] = []
        self['picDict'] = {}
        # Now create our lists
        lst = listdir(self['picPath'])
        for l in lst:
            configEntry = self.readConfigEntry(l)
            if not self.isIncluded(l, configEntry):
                continue
            self['configEntries'][l] = configEntry
            subPath = pathjoin(self['picPath'], l)
            if isdir(subPath):
                # If it's a directory, recursively create an instance and process that
                # directory.
                p = PictureDir(self['picRoot'], self['webRoot'],
                               dirName=pathjoin(self['dirName'],l),
                               doUp=True, stylesheetPath=childStylesheetPath)
                if p.hasPics():
                    self['subdirList'].append(p)
                    self['subdirDict'][l] = p
            elif isPicFile(self['picPath'], subPath):
                # Otherwise it's a file.
                im = Picture(l, self['picPath'], self['webPath'], dirName, configEntry,
                             stylesheetPath=stylesheetPath)
                self['picList'].append(im)
                self['picDict'][l] = im
        # Now sort the lists, and then rearrange them given the information in
        # the config file.
        self.sortSubList(self['subdirList'], 'folder order')
        self.sortSubList(self['picList'], 'image order')


    booleanTrueValues  = ['1', 'yes', 'true',  'on' ]
    booleanFalseValues = ['0', 'no',  'false', 'off']


    def readConfigEntry(self, name):
        '''Read the configuration information for an entry, if it is available.'''
        configEntry = {}

        if self['dirConfig'].has_option('include', name):
            s = self['dirConfig'].get('include', name)
            self.interpretConfigEntry(configEntry, s, 'include')
            if not configEntry.has_key('include'):
                # If there was no include= value in here, assume one just because the name was
                # in the [include] section.
                configEntry['include'] = True

        if self['dirConfig'].has_option('exclude', name):
            s = self['dirConfig'].get('exclude', name)
            self.interpretConfigEntry(configEntry, s, 'exclude')

        #print "configEntry<%s>" % name
        #for key in configEntry.keys():
        #    print "  %s: %s" % (key, configEntry[key])
        return configEntry


    def interpretConfigEntry(self, configEntry, s, default):
        for ss in s.split():
            kv = ss.split('=',1)
            if len(kv) == 2:
                # A value like "key=value"
                configEntry[kv[0]] = kv[1]
            elif kv[0].lower() in self.booleanTrueValues:
                # A bare true value
                configEntry[default] = True
            elif kv[0].lower() in self.booleanFalseValues:
                # A bare false value
                configEntry[default] = False
            else:
                # A bare word with no value
                configEntry[kv[0]] = True
        return configEntry


    def isIncluded(self, name, configEntry):
        '''Find out if an entry is to be included in the output.'''
        # Default is to include, unless there is an [include] section.
        if self['dirConfig'].has_section('include'):
            # But if the [include] section has a * entry, honour that.
            if self['dirConfig'].has_option('include','*'):
                included = self['dirConfig'].getboolean('include','*')
            else:
                included = False
        else:
            included = True
        # Ignore anything starting with '.'
        if name[0] == '.':
            included = False
        if configEntry.has_key('include'):
            included = configEntry['include']
        # Exclusion takes precedence, if specified.
        if configEntry.has_key('exclude'):
            included = not configEntry['exclude']
        #print "isIncluded(%s, %s): %s" % (self['dirName'],name,str(included))
        return included


    def sortSubList(self, lst, sectionName):
        # Sort gives us the default order.
        lst.sort()
        if not self['dirConfig'].has_section(sectionName):
            return
        # Take a shallow copy, then null the original.
        lstcopy = copy(lst)
        for i in range(len(lst)):
            lst[i] = None
        # Copy the original data back into the original array, if it's
        # referenced in the config.
        for i in range(len(lst)):
            sub = lstcopy[i]
            # This requires Picture and PictureDir objects to have a name()
            # method that returns the directory entry name.
            name = sub.name()
            if self['dirConfig'].has_option(sectionName, name):
                order = self['dirConfig'].getint(sectionName, name) - 1
                # Error if there are duplicate indexes in the config.
                if lst[order] is not None:
                    print >>stderr, "%s: duplicate index in [folder order] for %s: %s and %s" \
                          % (argv[0], self['dirName'],
                             lst[order]['dirBasename'], sub['dirBasename'])
                    print >>stderr, "  I cannot continue, I don't know what to do here."
                    exit(1)
                # Copy the data, and zero the copy.
                lst[order] = sub
                lstcopy[i] = None
        # Now for all the data in the copied array that hasn't been copied back
        # to the original array, copy it back in order.
        for i in range(len(lst)):
            if lstcopy[i] is None:
                continue
            sub = lstcopy[i]
            for j in range(len(lst)):
                if lst[j] is None:
                    lst[j] = sub
                    break


    def name(self):
        return self['dirBasename']


    def __str__(self):
        s = '<<PictureDir("%s","%s","%s",%s)' % \
            (self['picRoot'], self['webRoot'], self['dirName'], str(self['doUp']))
        s += ':im=[ '
        for p in self['picList']:
            s = s + p['picName'] + ' '
        s = s + ']'
        s = s + ':sd[ '
        for d in self['subdirList']:
            s = s + d['dirName']+' '
        s = s + ']>>'
        return s


    def hasPics(self):
        return len(self['subdirList']) > 0 or len(self['picList']) > 0


    def go(self, prevDir=None, nextDir=None):
        '''Process the pics and sub-directories.'''
        if not self.hasPics():
            message("No pics in %s: doing nothing" % self['picPath'])
            return False
        message("%s" % self['picPath'])
        for d in (self['webPath'], self['fullLinkPath'], self['downloadLinkPath']):
            if not isdir(d):
                makedirs(d)
        modified = False
        for i in range(len(self['picList'])):
            pic = self['picList'][i]
            if pic is None:
                continue
            if i > 0: prevPic = self['picList'][i-1]
            else: prevPic = None
            if i < len(self['picList'])-1: nextPic = self['picList'][i+1]
            else: nextPic = None
            m = pic.go(prevPic, nextPic)
            if m: modified = True
        for i in range(len(self['subdirList'])):
            d = self['subdirList'][i]
            if d is None:
                continue
            if i > 0: prevSubdir = self['subdirList'][i-1]
            else: prevSubdir = None
            if i < len(self['subdirList'])-1: nextSubdir = self['subdirList'][i+1]
            else: nextSubdir = None
            m = d.go(prevSubdir, nextSubdir)
            if m: modified = True
        if options.regen_all or options.regen_markup or modified:
            # Create our directory index
            self.createMarkup(prevDir, nextDir)
        htafilename = pathjoin(self['downloadLinkPath'], '.htaccess')
        if options.regen_markup or options.regen_all \
           or not isfile(htafilename):
            htafile = open(htafilename, 'w')
            htafile.write('<IfModule mod_headers.c>\n')
            htafile.write(' <FilesMatch ".*">\n')
            htafile.write('  Header onsuccess set Content-Disposition attachment\n')
            htafile.write(' </FilesMatch>\n')
            htafile.write('</IfModule>\n')
            htafile.close()
        return modified

    numberClasses = { 2:'p2', 3:'p3', 4:'p4', 5:'p5' }


    def createMarkup(self, prevDir=None, nextDir=None):
        verboseMessage("  %s" % self['xmlPath'])
        x = file(self['xmlPath'], "w")
        s = StringIO()
        if self['dirName'] == '':
            if options.title:
                dname = entityReplace(options.title)
                dpath = entityReplace(options.title)
            else:
                dname = 'Pics'
                dpath = 'Pics'
            if options.subdir:
                dname = dname + ' - ' + entityReplace(basename(picRoot))
                dpath = dpath + ' - ' + entityReplace(basename(picRoot))
        else:
            # dirName is not null, so it's definitely a subdir
            if options.title:
                dname = entityReplace(options.title+' - '+self['dirBasename'])
                dpath = entityReplace(options.title+' - '+self['dirName'])
            else:
                dname = entityReplace(self['dirBasename'])
                dpath = entityReplace(self['dirName'])
        if self['stylesheetPath']:
            spath = self['stylesheetPath']
        else:
            spath = ''
        s.write(
            '<?xml version="1.0"?>\n' \
            '<?xml-stylesheet type="text/xsl" href="#stylesheet"?>\n' \
            '<!DOCTYPE picturedir ' \
            '[ <!ATTLIST xsl:stylesheet id ID #REQUIRED> ]>\n' \
            '<picturedir name="%s" path="%s" css="%s" stylesheetPath="%s"' % \
            (dname, dpath, self['cssPath'], spath))
        s.write('>\n')
        # xsl:import must be before xsl:param.  But the param here has
        # precedence because there's an import tree.  Weird, but true.
        s.write('<xsl:stylesheet id="stylesheet"\n'
                '   version="1.0"\n'
                '   xmlns:xsl="http://www.w3.org/1999/XSL/Transform">\n'
                '  <xsl:import href="%s"/>\n' % self['xslPath'] +\
                '  <xsl:param name="nTableColumns">%d</xsl:param>\n' % \
                options.row)
        if options.no_html:
            s.write('  <xsl:param name="nohtml">yes</xsl:param>\n')
        s.write('</xsl:stylesheet>\n')

        if self['doUp']:
            s.write('  <updir/>\n')
        if prevDir:
            s.write('  <prev>\n')
            s.write('    <name>%s</name>\n' % entityReplace(prevDir['dirBasename']))
            (tname,twidth,theight) = prevDir.thumbnailName()
            if tname:
                if twidth:
                    s.write('    <thumbnail width="%d" height="%d">%s</thumbnail>\n' % \
                            (twidth, theight, entityReplace(tname)))
                else:
                    s.write('    <thumbnail>%s</thumbnail>\n' % entityReplace(tname))
            s.write('  </prev>\n')
        if nextDir:
            s.write('  <next>\n')
            s.write('    <name>%s</name>\n' % entityReplace(nextDir['dirBasename']))
            (tname,twidth,theight) = nextDir.thumbnailName()
            if tname:
                if twidth:
                    s.write('    <thumbnail width="%d" height="%d">%s</thumbnail>\n' % \
                            (twidth, theight, entityReplace(tname)))
                else:
                    s.write('    <thumbnail>%s</thumbnail>\n' % entityReplace(tname))
            s.write('  </next>\n')
        s.write(
            '  <thumbnails>\n'
            '    <x>%s</x>\n    <y>%s</y>\n' % options.thumbnail_size+\
            '  </thumbnails>\n')
        s.write('  <dirs>\n')
        for d in self['subdirList']:
            s.write(
                '    <dir>\n' \
                '      <name>%s</name>\n' % entityReplace(d['dirBasename']) +\
                '      <path>%s</path>\n' % entityReplace(d['dirName']))
            (tname,twidth,theight) = d.thumbnailName()
            if tname:
                if twidth:
                    s.write('      <thumbnail width="%d" height="%d">%s</thumbnail>\n' % \
                            (twidth, theight, entityReplace(tname)))
                else:
                    s.write('      <thumbnail>%s</thumbnail>\n' % entityReplace(tname))
            s.write('    </dir>\n')
        s.write('  </dirs>\n')
        s.write('  <images>\n')
        for f in self['picList']:
            s.write(
                '    <image>\n' \
                '      <name>%s</name>\n' % entityReplace(f['picNameBase']) +\
                '      <ext>%s</ext>\n' % entityReplace(f['picNameExt']))
            if f.has_key('thumbnail-width'):
                s.write('      <size width="%d" height="%d" />\n' % (f['thumbnail-width'],
                                                                     f['thumbnail-height']))
            else:
                s.write('      <!-- no thumbnail size -->\n')
            if f['comment']:
                # Make sure a long comment doesn't take up all the space.
                comment = f['comment']
                if len(comment) > 75:
                    comment = comment[:75]+'...'
                s.write('      <comment>%s</comment>\n' % entityReplace(comment))
            if f.has_key('fullImageWidth') and f.has_key('fullImageHeight'):
                s.write('      <fullsize width="%d" height="%d" />\n' % \
                        (f['fullImageWidth'], f['fullImageHeight']))
            if f.has_key('fullImageHeight'):
                s.write('      <filesize>%s</filesize>\n' % f['fullImageSize'])
            s.write('    </image>\n')
        s.write('  </images>\n')
        s.write('</picturedir>\n')
        x.write(s.getvalue())
        s.close()
        x.close()
        if not options.no_html:
            verboseMessage('Creating %s' % pathjoin(self['webRoot'],self['dirName'],
                                                    'index.html'))
            if options.xsltproc:
                cmd = 'cd %s && xsltproc ' \
                      '--param imagePageExtension \'".html"\' ' \
                      '-o index.html index.xml' % \
                      shellEscape(pathjoin(self['webRoot'], self['dirName']))
                verboseMessage('Command: %s' % cmd)
                system(cmd)
            else:
                styuri = OsPathToUri(abspath(pathjoin(webRoot, self['dirName'],
                                                      self['xslPath'])))
                verboseMessage("stylesheet URI: %s" % styuri)
                srcuri = OsPathToUri(abspath(pathjoin(webRoot, self['dirName'], 'index.xml')))
                verboseMessage("source     URI: %s" % srcuri)
                STY = InputSource.DefaultFactory.fromUri(styuri)
                SRC = InputSource.DefaultFactory.fromUri(srcuri)
                processor = Processor.Processor()
                processor.appendStylesheet(STY)
                result = processor.run(SRC, topLevelParams={ 'imagePageExtension':'.html',
                                                             'nTableColumns': options.row})
                htmlf = file(self['htmlPath'], 'w+')
                htmlf.write(result)
                htmlf.close()


    # Comparisons assume that all the dirs compared are siblings (ie direct
    # children of one parent directory.)
    def __eq__(self, other): return self['dirName'] == other['dirName']
    def __ne__(self, other): return self['dirName'] != other['dirName']
    def __gt__(self, other): return self['dirName'] >  other['dirName']
    def __lt__(self, other): return self['dirName'] <  other['dirName']
    def __ge__(self, other): return self['dirName'] >= other['dirName']
    def __le__(self, other): return self['dirName'] <= other['dirName']

    def __repr__(self): return self['dirName']


    def thumbnailName(self):
        '''Find out the name of the image used as a thumbnail.'''
        ret = (None,None,None)
        im = None
        if self['dirConfig'].has_option('folder', 'thumbnail'):
            nm = self['dirConfig'].get('folder','thumbnail')
            try:
                im = self['picDict'][nm]
            except KeyError, reason:
                print >>stderr, "%s: %s does not contain %s" % (argv[0], self['dirName'], nm)
                im = None
        elif len(self['picList']) != 0:
            im = self['picList'][randint(0,len(self['picList'])-1)]

        if im:
            if im.has_key('thumbnail-width') and im.has_key('thumbnail-height'):
                ret = (im['thumbnailName'], im['thumbnail-width'], im['thumbnail-height'])
            else:
                ret = (im['thumbnailName'], None, None)
        verboseMessage("For %s, thumbnail is %s" % (self, ret))
        return ret


    def deleteUnused(self):
        '''Delete unused directories and files in the output tree.'''
        # First, do the same thing in our subdirectories.
        for d in self['subdirList']:
            d.deleteUnused()

        # Now, construct the list of files and directories in this directory that we want to
        # keep.
        filesToKeep = copy(self.filesToKeep)
        subdirFilesToKeep = copy(self.subdirFilesToKeep)
        # Keep all the subdirs with pics in them.
        for z in self['subdirDict'].keys():
            filesToKeep[z] = 1
        # Loop through our pics and find out what files they have want to keep.
        for z in self['picList']:
            filesToKeep[z['imageName']] = 1
            filesToKeep[z['thumbnailName']] = 1
            filesToKeep[z['xmlName']] = 1
            filesToKeep[z['htmlName']] = 1
            # In the .spp-full and .spp-download directories, there is one symlink for each of
            # the pics we have, so we make sure we keep them.
            subdirFilesToKeep[z['imageName']] = 1

        # Get the list of things that are in the output directory.
        lst = listdir(self['webPath'])
        for l in lst:
            p = pathjoin(self['webPath'], l)
            if isdir(p) and l in self.subdirsToKeep:
                sublst = listdir(p)
                for sl in sublst:
                    if not sl in subdirFilesToKeep:
                        self.deleteSomething(pathjoin(p, sl))
            elif not l in filesToKeep:
                self.deleteSomething(p)


    def deleteSomething(self, p):
        try:
            if isdir(p):
                self.deleteDir(p)
            else:
                self.deleteNonDir(p)
        except Exception, reason:
            print >>stderr, "%s: error deleting %s: %s" % (argv[0], p, str(reason.args))


    def deleteDir(self, d):
        '''Recursively delete a whole directory tree.'''
        if options.delete:
            lst = listdir(d)
            for e in lst:
                p = pathjoin(d,e)
                self.deleteSomething(p)
            message("Removing directory %s" % d)
            rmdir(d)
        else:
            message("I want to delete dir  %s" % d)


    def deleteNonDir(self, p):
        '''Delete one file'''
        if options.delete:
            unlink(p)
        else:
            message("I want to delete file %s" % p)



# Characters that can be included in shell commands without escaping.
shellOKChars = 'abcdefghijklmnopqrstuvwxyz' \
               'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
               '0123456789' \
               '.@+-_,/'

def shellEscape(sin):
    '''Return a string escaped to protect it from the shell.'''
    sout = StringIO()
    for c in sin:
        if c in shellOKChars:
            sout.write(c)
        else:
            sout.write('\\'+c)
    r = sout.getvalue()
    sout.close()
    return r


def isPicFile(path, pic):
    '''Determine if a file is a known picture type.

    This currently only looks at the file name (actually the extension).  It
    should also identify the file contents, perhaps using Image methods?'''

    (base, ext) = splitext(pic)
    if ext.lower() in options.extensions:
        return True
    return False


def fileIsNewer(file1, file2):
    '''Return true if first named file is newer than the second.

    file1 and file2 can be names, or the results of calling os.stat().  If
    either file does not exist, we return false.'''
    if isinstance(file1,str):
        try:
            file1stat = stat(file1)
        except OSError,reason:
            if reason.errno == ENOENT: return False
            else: raise
    else:
        file1stat = file1
    if isinstance(file2,str):
        try:
            file2stat = stat(file2)
        except OSError,reason:
            if reason.errno == ENOENT: return False
            else: raise
    else:
        file2stat = file2
    return file1stat.st_mtime > file2stat.st_mtime


def searchForFile(path, type, filename):
    '''Look for a file in the python search path, with a couple of optional
    prefixes.'''
    #print >>stderr, "searchfor  (%s, %s)" % (path,filename)
    p = pathjoin(path, filename)
    pe = pathjoin(path, type, filename)
    pse = pathjoin(path, 'static_picture_publish', filename)
    pste = pathjoin(path, 'static_picture_publish', type, filename)
    #print >>stderr, "Looking for %s, cwd is %s" % (p, getcwd())
    if pathexists(pste):
        #print "Found %s" % pste
        return pste
    elif pathexists(pse):
        #print "Found %s" % pse
        return pse
    elif pathexists(pe):
        #print "Found %s" % pe
        return pe
    elif pathexists(p):
        #print "Found %s" % p
        return p
    else:
        return None


def findFile(filename, filetype):
    filepathname = None
    # If we are given a full or relative-to-pwd path to the file, use that.
    if filename.startswith('/') or filename.startswith('./') \
           or filename.startswith('../'):
        filepathname = filename
    else:
        # Otherwise, construct the full path to the file.  If we are running
        # from the development directory, or otherwise not from a full path
        # name, look at relative locations first.
        if argv[0].startswith('.'):
            searchpath = ['.', '..', '../..']
        else:
            searchpath = ['.']
        for p in syspath:
            searchpath.append(p)
        #print >>sys.stderr, "searchpath is %s" % str(searchpath)
        for path in searchpath:
            filepathname = searchForFile(path, filetype, filename)
            if filepathname:
                break
    return filepathname


def sppCopyFile(filename, destfilename, filetype, stylesheetPath=None):
    f = findFile(filename, filetype)
    if f is None:
        print >>stderr, "%s: cannot find %s" % (argv[0], filename)
        return
    if stylesheetPath is None:
        p = pathjoin(webRoot, destfilename)
    else:
        p = pathjoin(webRoot, stylesheetPath, destfilename)
    p = normpath(p)
    #print "Copying %s to %s" % (f,p)
    copyfile(f, p)


# A place to keep all the directory configuration information.  Indexed by
# dirName, so we can get to the info from both the source and destination
# trees.
dirConfigs = {}


def findstylesheetPath():
    '''Locate the CSS and XSL files if we are processing only a subdirectory.'''
    path = '.'
    while True:
        tryPath = normpath(pathjoin(webRoot, path))
        # Search terminating condition
        if abspath(tryPath) == '/':
            return None
        verboseMessage("findstylesheetPath(): trying %s" % tryPath)
        if isfile(pathjoin(tryPath,'spp-dir.xsl')) \
           and isfile(pathjoin(tryPath,'spp-image.xsl')) \
           and isfile(pathjoin(tryPath,'spp.css')):
            # normpath gets rid of the leading './'
            return normpath(path)
        # Try the next directory up
        path = pathjoin(path,'..')


def go():
    parseOptions()

    #print "subdir is %s" % str(options.subdir)
    if options.subdir:
        # Search for the XSL and CSS stylesheets.
        stylesheetPath = findstylesheetPath()
        if stylesheetPath is None:
            print >>stderr, "%s: cannot find spp.css, spp-dir.xsl and spp-image.xsl" % argv[0]
            exit(1)
    else:
        stylesheetPath = None
    pd = PictureDir(picRoot, webRoot, doUp=options.subdir, stylesheetPath=stylesheetPath)
    # Create the output directory.
    try:
        makedirs(webRoot)
    except OSError, reason:
        if reason.errno == EEXIST and isdir(webRoot):
            pass
        else:
            print >>stderr, "%s: error creating %s: %s" % \
                  (argv[0], webRoot, str(reason.args))
            exit(1)
    # Copy in the XSL and CSS files.
    if not options.subdir:
        sppCopyFile(options.css_file,       "spp.css",       "css", stylesheetPath=stylesheetPath)
        sppCopyFile(options.xsl_dir_file,   "spp-dir.xsl",   "xsl", stylesheetPath=stylesheetPath)
        sppCopyFile(options.xsl_image_file, "spp-image.xsl", "xsl", stylesheetPath=stylesheetPath)
        for f in ('tl1.gif','tl2.gif','t.gif','tr.gif',
                  'l.gif','r.gif',
                  'bl.gif','b.gif','br.gif',
                  'folder-pics.gif'):
            sppCopyFile(f, f, "images")
    # Now create thumbnails and markup.
    pd.go()
    pd.deleteUnused()


if __name__ == '__main__':
    go()


# This section is for emacs.
# Local variables: ***
# mode:python ***
# py-indent-offset:4 ***
# fill-column:95 ***
# End: ***

