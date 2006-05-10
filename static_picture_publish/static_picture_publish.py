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
from random import randint, seed

# init the random number generator.
seed()


defaultExtensions = '.jpg,.jpeg,.gif,.png'


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
    help='Don\'t create HTML from XML (Unimplemented)')
markup_opts.add_option(
    '-r','--regen-all',
    action='store_true',
    help='Force regeneration of all output')
markup_opts.add_option(
    '-S', '--subdir',
    action='store_true',
    help='Run as if in a subdirectory of the output directory (Unimplemented)')
markup_opts.add_option(
    '-t','--title',
    type='string',
    action='store',
    help='Set the HTML title (Unimplemented)')
opt.add_option_group(markup_opts)

layout_opts = OptionGroup(opt, "Layout options")
layout_opts.add_option(
    '--css',
    action='store',
    #metavar="css_file",
    help='CSS file to use in HTML or XML output. (Default inbuilt)')
layout_opts.add_option(
    '--javascript',
    action='store',
    help='Javascript file to use in HTML or XML output. (Default inbuilt)')
layout_opts.add_option(
    '--with-javascript',
    action='store_true',
    help='Use javascript in output.  (Default no)')
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
    if not options.css:
        options.css = "css/spp.css"
    if not options.xsl_dir:
        options.xsl_dir = "xsl/spp-dir.xsl"
    if not options.xsl_image:
        options.xsl_image = "xsl/spp-image.xsl"
    if not options.javascript:
        options.javascript = "javascript/spp.js"
    options.messageLevel = 1
    if options.verbose:
        options.messageLevel = 2
    if options.quiet:
        options.messageLevel = 0
    if not options.row:
        options.row = 3
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
        self['fullImageName'] = base + "-full" + ext
        self['imagePath'] = pathjoin(webDirName, self['imageName'])
        self['thumbnailName'] = base + "-thumb" + ext
        self['thumbnailPath'] = pathjoin(webDirName, self['thumbnailName'])
        self['htmlName'] = base + ".html"
        self['htmlPath'] = pathjoin(webDirName, self['htmlName'])
        self['xmlName'] = base + ".xml"
        self['xmlPath'] = pathjoin(webDirName, self['xmlName'])
        self['htmlName'] = base + ".html"
        self['htmlPath'] = pathjoin(webDirName, self['htmlName'])
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
                image = None            # gc
        except (IOError, SystemError), reason:
            print >>stderr, "%s: error processing %s: %s" % \
                  (argv[0], self['picPath'], str(reason.args))
        self.createMarkup(prevPic, nextPic)
        for n in ['image', 'thumbnail']:
            self[n+'-image'] = None
        return modified


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
        #print "%s: size:%s required:%s flag:%s" % (imagePath, str(smallimage.size), str(requiredSize), str(flag))
        return flag


    def generateImage(self, image_basename, imageSize, image):
        '''Make an output image.'''
        imagePath = self[image_basename+'Path']
        verboseMessage("  %s => %s" % (self['picPath'], imagePath))
        starttime = time()
        if image is None:
            image = Image.open(self['picPath'])
            if self['configEntry'].has_key('rotate'):
                angle = int(self['configEntry']['rotate'])
                print " -- Rotating %s by %d" % (imagePath, angle)
                if angle == 90:
                    image = image.transpose(Image.ROTATE_90)
                elif angle == 180:
                    image = image.transpose(Image.ROTATE_180)
                elif angle == 270:
                    image = image.transpose(Image.ROTATE_270)
                else:
                    image = image.rotate(angle)
        image.thumbnail(imageSize, Image.ANTIALIAS)
        self[image_basename+'-width']  = image.size[0]
        self[image_basename+'-height'] = image.size[1]
        image.save(imagePath)
        endtime = time()
        verboseMessage("  generation time %s: %.2f" % (imagePath, endtime-starttime))
        modified = True
        return image


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
        else:
            s.write('  <!-- no image width -->\n')
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
            verboseMessage('Creating %s' % \
                           pathjoin(self['webDirName'], self['htmlName']))
            cmd = 'cd %s && xsltproc ' \
                  '--param imagePageExtension \'".html"\' ' \
                  '-o %s %s' % (shellEscape(self['webDirName']),
                               shellEscape(self['htmlName']),
                               shellEscape(self['xmlName']))
            verboseMessage('Command: %s' % cmd)
            system(cmd)
        if not options.no_originals:
            self.createFullImageLink()


    def createFullImageLink(self):
        '''Create a symlink to the full image.'''

        fullImagePath = abspath(pathjoin(self['picDirName'], self['picName']))
        symlinkPath = abspath(pathjoin(self['webDirName'], self['fullImageName']))
        st = None
        try:
            st = stat(symlinkPath)
        except OSError, reason:
            if reason.errno == ENOENT: pass
            else: raise
        if st is None:
            verboseMessage("symlink: %s -> %s" % (symlinkPath, fullImagePath))
            symlink(fullImagePath, symlinkPath)
        else:
            # This logic will delete relative symlinks that do point to the
            # right place, and replace them with absolute symlinks that point
            # to the same place.  The alternative is to call readlink() with
            # cwd of the symlink location, but I haven't coded that yet.
            if not islink(symlinkPath) \
               or abspath(readlink(symlinkPath)) != fullImagePath:
                verboseMessage("symlink: %s -> %s" % \
                               (symlinkPath, fullImagePath))
                unlink(symlinkPath)
                symlink(fullImagePath, symlinkPath)


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
    filesToKeep = [ '.htaccess', 'index.xml', 'index.html',
                    'spp.css', 'spp-dir.xsl', 'spp-image.xsl', 'spp.js']

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
        else:
            self['picPath'] = pathjoin(self['picRoot'], self['dirName'])
            self['webPath'] = pathjoin(self['webRoot'], self['dirName'])
        self['htmlPath'] = pathjoin(self['webPath'], "index.html")
        self['xmlPath'] = pathjoin(self['webPath'], "index.xml")
        # If we were supplied a path to the CSS and XSL files, then we use that.  Otherwise,
        # calculate the path by going up until we get to the top.
        if stylesheetPath:
            childStylesheetPath = pathjoin('..',stylesheetPath)
            self['xslPath'] = pathjoin(stylesheetPath, 'spp-dir.xsl')
            self['cssPath'] = pathjoin(stylesheetPath, 'spp.css')
            if options.with_javascript:
                self['javascriptPath'] = pathjoin(stylesheetPath, 'spp.js')
        else:
            # This looks very inefficient, but it will only happen once, at the root of the
            # tree.  All the subdirectory instances will be supplied the childStylesheetPath
            # parameter, so won't have to do this search.
            childStylesheetPath = None
            if self['dirName'] == '':
                self['xslPath'] = 'spp-dir.xsl'
                self['cssPath'] = 'spp.css'
                if options.with_javascript:
                    self['javascriptPath'] = 'spp.js'
            else:
                self['xslPath'] = '../spp-dir.xsl'
                self['cssPath'] = '../spp.css'
                if options.with_javascript:
                    self['javascriptPath'] = '../spp.js'
                ht = pathsplit(self['dirName'])[0]
                while ht != '':
                    self['xslPath'] = '../'+self['xslPath']
                    self['cssPath'] = '../'+self['cssPath']
                    if options.with_javascript:
                        self['javascriptPath'] = '../'+self['javascriptPath']
                    ht = pathsplit(ht)[0]

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
                p = PictureDir(self['picRoot'], self['webRoot'], dirName=pathjoin(self['dirName'],l),
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
                    raise IndexError('Duplicate index')
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


    def go(self):
        '''Process the pics and sub-directories.'''
        if not self.hasPics():
            message("No pics in %s: doing nothing" % self['picPath'])
            return False
        message("%s" % self['picPath'])
        if not isdir(self['webPath']):
            makedirs(self['webPath'])
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
            m = d.go()
            if m: modified = True
        if options.regen_all or options.regen_markup or modified:
            # Create our directory index
            self.createMarkup()
        return modified

    numberClasses = { 2:'p2', 3:'p3', 4:'p4', 5:'p5' }


    def createMarkup(self):
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
        s.write(
            '<?xml version="1.0"?>\n' \
            '<?xml-stylesheet type="text/xsl" href="#stylesheet"?>\n' \
            '<!DOCTYPE picturedir ' \
            '[ <!ATTLIST xsl:stylesheet id ID #REQUIRED> ]>\n' \
            '<picturedir name="%s" path="%s" css="%s"' % \
            (dname, dpath, self['cssPath']))
        if options.with_javascript:
            s.write(' javascript="%s"' % self['javascriptPath'])
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
            s.write('    </image>\n')
        s.write('  </images>\n')
        s.write('</picturedir>\n')
        x.write(s.getvalue())
        s.close()
        x.close()
        if not options.no_html:
            verboseMessage('Creating %s' % \
                           pathjoin(self['webRoot'], self['dirName'], 'index.html'))
            cmd = 'cd %s && xsltproc ' \
                  '--param imagePageExtension \'".html"\' ' \
                  '-o index.html index.xml' % \
                  shellEscape(pathjoin(self['webRoot'], self['dirName']))
            verboseMessage('Command: %s' % cmd)
            system(cmd)


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
            im = self['picDict'][nm]
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
        # Now, construct the list of files and directories we want to keep.
        keepList = {}
        for z in self.filesToKeep:
            keepList[z] = 1
        for z in self['subdirDict'].keys():
            keepList[z] = 1
        for z in self['picList']:
            keepList[z['imageName']] = 1
            keepList[z['fullImageName']] = 1
            keepList[z['thumbnailName']] = 1
            keepList[z['xmlName']] = 1
            keepList[z['htmlName']] = 1
        # Get the list of things that are in the output directory.
        lst = listdir(self['webPath'])
        for l in lst:
            if not l in keepList:
                p = pathjoin(self['webPath'], l)
                try:
                    if isdir(p):
                        self.deleteDir(p)
                    else:
                        unlink(p)
                except OSError,reason:
                    print >>stderr, "%s: error deleting %s: %s" % (argv[0], p, str(reason.args))


    def deleteDir(self, d):
        '''Recursively delete a whole directory tree.'''
        lst = listdir(d)
        for e in lst:
            p = pathjoin(d,e)
            try:
                if isdir(p):
                    self.deleteDir(p)
                else:
                    unlink(p)
            except OSError,reason:
                print >>stderr, "%s: error deleting %s: %s" % (argv[0], p, str(reason.args))
        message("Removing directory %s" % d)
        rmdir(d)


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
        #print "findstylesheetPath(): trying %s" % path
        if isfile(normpath(pathjoin(webRoot, path,'spp-dir.xsl'))) \
           and isfile(normpath(pathjoin(webRoot, path,'spp-image.xsl'))) \
           and isfile(normpath(pathjoin(webRoot, path,'spp.css'))):
            # normpath gets rid of the leading './'
            return normpath(path)
        # Try the next directory up
        path = pathjoin(path,'..')
        # Search terminating condition
        if abspath(path) == '/':
            return None


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
        sppCopyFile(options.css,       "spp.css",       "css", stylesheetPath=stylesheetPath)
        sppCopyFile(options.xsl_dir,   "spp-dir.xsl",   "xsl", stylesheetPath=stylesheetPath)
        sppCopyFile(options.xsl_image, "spp-image.xsl", "xsl", stylesheetPath=stylesheetPath)
        if options.with_javascript:
            sppCopyFile(options.javascript,"spp.js", "javascript",
                        stylesheetPath=stylesheetPath)
    # Now create thumbnails and markup.
    pd.go()
    pd.deleteUnused()


if __name__ == '__main__':
    go()


# This section is for emacs.
# Local variables: ***
# mode:python ***
# py-indent-offset:4 ***
# fill-column:100 ***
# End: ***
# arch-tag: dbd38a8f-6259-49ca-a125-6b5cd1f48bdb

