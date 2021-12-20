#!/bin/bash
wget -r --adjust-extension http://127.0.0.1:5000/
wget_res=$?

if [ $wget_res -ne 0 ]; then
  rm -r 127.0.0.1:5000
  exit $wget_res
fi

WEB_DIR="/home/ockovani/prd/web/ockovani-covid-pages"

find $WEB_DIR -name "*.html" -type f -delete
cp -r 127.0.0.1:5000/* ${WEB_DIR}/
rm -r 127.0.0.1:5000

cd $WEB_DIR || exit 1
git add *
git commit -am "Update"
git push origin master
