#!/bin/bash
wget -r http://127.0.0.1:${1}/
find ./127.0.0.1:${1}/ -type f -print0 | xargs -0 -I{} mv "{}" "{}".html
mv ./127.0.0.1:${1}/index.html.html ./127.0.0.1:${1}/index.html

cp -r 127.0.0.1:${1}/* /home/ockovani/prd/web/ockovani-covid-pages/
rm -r 127.0.0.1:${1}
cd /home/ockovani/prd/web/ockovani-covid-pages
git add *
git commit -m "Update"
git push origin master

