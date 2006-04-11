#!/bin/sh

set -e -x

./static-picture-publish -g ,a ,b
( cd ,b && xsltproc index.xml | tidy -i -q )

# arch-tag: f904124a-6cb8-4148-b5b6-fbdc7c1529f4
