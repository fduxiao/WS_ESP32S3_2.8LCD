#!/bin/sh
HERE=`dirname $0`
HERE=`realpath $HERE`
USER_C_MODULES=$HERE/user_mods/micropython.cmake
cd ../../
echo $PWD
make -j USER_C_MODULES="$USER_C_MODULES" BOARD=AntiGM
