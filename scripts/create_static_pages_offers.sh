#!/bin/bash

WEB_TMP_DIR="/home/ockovani/prd/web-tmp"
WEB_DIR="/home/ockovani/prd/web/ockovani-covid-pages"

mkdir -p $WEB_TMP_DIR

wget -r -P $WEB_TMP_DIR -e robots=off --adjust-extension -l 2 -I /nabidky,/praktik,/okres,/kraj http://127.0.0.1:5000/nabidky
wget_res=$?

if [ $wget_res -ne 0 ]; then
  rm -r $WEB_TMP_DIR
  exit $wget_res
fi

wget -P $WEB_TMP_DIR/127.0.0.1:5000 -e robots=off --adjust-extension http://127.0.0.1:5000/praktici
wget_res=$?

if [ $wget_res -ne 0 ]; then
  rm -r $WEB_TMP_DIR
  exit $wget_res
fi

cp -r ${WEB_TMP_DIR}/127.0.0.1:5000/* ${WEB_DIR}/
rm -r $WEB_TMP_DIR

cd $WEB_DIR || exit 1
git add *
git commit -am "Update offers"
git push origin master
