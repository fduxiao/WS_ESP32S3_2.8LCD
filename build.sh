#!/bin/sh
HERE=`dirname $0`
HERE=`realpath $HERE`
source $HERE/env
cd ../../
echo $PWD
make -j
