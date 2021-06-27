#!/bin/bash
wget --adjust-extension http://127.0.0.1:5000/praktici
wget_res=$?

if [ $wget_res -ne 0 ]; then
  rm -f praktici.html
  exit $wget_res
fi

cp praktici.html /home/ockovani/prd/web/ockovani-covid-pages/
rm praktici.html
cd /home/ockovani/prd/web/ockovani-covid-pages
git add *
git commit -m "Update - free vaccines"
git push origin master

