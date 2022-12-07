#!/bin/bash
DJANGO_ADMIN=django-admin
DIRS="
 django_webix
"
PROJ=`pwd`/

for D in $DIRS
do
  echo $D
  DIR="${PROJ}${D}"
  echo "Process $DIR"

  CMD="pushd $DIR"
  eval $CMD

 for L in en it de fr es ca el
  do
    CMD="$DJANGO_ADMIN makemessages --extension=js,html,py -l $L"
    echo $CMD
    eval $CMD
  done

  for L in en it de fr es ca el
  do
    CMD="$DJANGO_ADMIN  makemessages -d djangojs -l $L"
    echo $CMD
    eval $CMD
  done

  CMD="$DJANGO_ADMIN compilemessages"
  echo $CMD
  eval $CMD

  CMD="popd"
  eval $CMD
done

