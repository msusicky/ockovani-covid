#!/bin/bash

WEB_TMP_DIR="/home/ockovani/prd/web-tmp"
WEB_DIR="/home/ockovani/prd/web/ockovani-covid-pages"

mkdir -p $WEB_TMP_DIR

wget -P $WEB_TMP_DIR -e robots=off --adjust-extension http://127.0.0.1:5000/nabidky
wget_res=$?

if [ $wget_res -ne 0 ]; then
  rm -r $WEB_TMP_DIR
  exit $wget_res
fi

cp ${WEB_TMP_DIR}/nabidky.html ${WEB_DIR}/
rm -r $WEB_TMP_DIR

cd $WEB_DIR || exit 1
git add *
git commit -am "Update"
git push origin master
