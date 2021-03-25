#!/bin/bash
wget -r --adjust-extension http://127.0.0.1:5000/
wget_res=$?

if [ $wget_res -ne 0 ]; then
  rm -r 127.0.0.1:5000
  exit $wget_res
fi

cp -r 127.0.0.1:5000/* /home/ockovani/prd/web/ockovani-covid-pages/
rm -r 127.0.0.1:5000
cd /home/ockovani/prd/web/ockovani-covid-pages
git add *
git commit -m "Update"
git push origin master

