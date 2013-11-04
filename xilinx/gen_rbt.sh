#!/usr/bin/env bash

ROOT=sweep_clb
if [ $# -eq 1 ]
then
    ROOT=$1
fi

#echo $#
#echo "'$ROOT'"
#exit 1

OUT=bash
find $ROOT -name '*.BIT' -exec echo 'echo {}; python fc-xibit2rbt.py {} --prefix --core > {}.FCRBT' ';' |sed s/.BIT.FCRBT/.FCRBT/g |$OUT

