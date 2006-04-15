# Setup for static-picture-publish.


from distutils.core import setup

# This version number must match the version number in VERSION.

_sppVersion = '0.1'

setup(name='static-picture-publish',
      description="""Publish images.""",

      long_description="""
      Print diaries on a range of paper sizes.  The diaries can
      include a cover page, various types of front matter pages
      (planners, calendars, addresses etc), and a year's worth of day
      pages.""",

      author='Russell Steicke',
      author_email='russells@adelie.cx',
      url='http://adelie.cx/static-picture-publish',
      version=_sppVersion,
      license="GPL",
      packages=['static-picture-publish'],
      scripts=['bin/static-picture-publish'],
      data_files=[('share/man/man1', ['man/static-picture-publish.1.gz'])])

# arch-tag: a7b4fe07-d658-43fc-962d-bb9456914ec8
