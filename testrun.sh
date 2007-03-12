#!/bin/sh

set -e -x

./bin/static-picture-publish -t "Test pics" -g "$@" ,a ,b

