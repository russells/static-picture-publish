# Setup for static-picture-publish.


from distutils.core import setup

# This version number must match the version number in VERSION.

_sppVersion = '0.1'

setup(name='static-picture-publish',
      description="""Publish images.""",

      long_description="""
      Publish images.""",

      author='Russell Steicke',
      author_email='russells@adelie.cx',
      url='http://adelie.cx/static-picture-publish',
      version=_sppVersion,
      license="GPL",
      packages=['static_picture_publish'],
      scripts=['bin/static-picture-publish'],
      data_files=[('share/man/man1',
                   ['man/static-picture-publish.1.gz']),
                  ('lib/site-python/static_picture_publish/css',
                   ['css/spp-plain.css'] ),
                  ('lib/site-python/static_picture_publish/xsl',
                   ['xsl/spp-dir-plain.xsl',
                    'xsl/spp-image-plain.xsl'] ),
                  ('lib/site-python/static_picture_publish/images',
                   ['images/tl1.gif',
                    'images/tl2.gif',
                    'images/t.gif',
                    'images/tr.gif',
                    'images/l.gif',
                    'images/folder-pics.gif',
                    'images/r.gif',
                    'images/bl.gif',
                    'images/b.gif',
                    'images/br.gif',
                    ] ),
                  ]
      )

