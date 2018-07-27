#!/bin/sh

$FC -c ../$NAME.f90 -fPIC
$FC $NAME.o -o $NAME.x
$FC $NAME.o -shared -fPIC -o $NAME.so

nm -g $NAME.so
