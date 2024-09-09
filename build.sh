#!/bin/sh
HERE=`dirname $0`
HERE=`realpath $HERE`
source $HERE/env
$HERE/gen_rom_data.py
cd ../../
echo $PWD
make -j
