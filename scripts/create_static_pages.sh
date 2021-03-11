#!/bin/bash
wget -r --adjust-extension http://127.0.0.1:5000/
cp -r 127.0.0.1:5000/* /home/ockovani/prd/web/ockovani-covid-pages/
rm -r 127.0.0.1:5000
cd /home/ockovani/prd/web/ockovani-covid-pages
git add *
git commit -m "Update"
git push origin master

