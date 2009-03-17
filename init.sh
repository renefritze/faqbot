#!/bin/bash

set -e
cd $(dirname $0)

if [ ! -d ../common ] ; then
	echo "assumed to be in submodule structure"
	exit 1
fi

for py in $(ls ../common/*.py) ; do
	ln -s ${py} 
	echo ${py}:t >> .gitignore
done

cp Main.conf.example Main.conf

