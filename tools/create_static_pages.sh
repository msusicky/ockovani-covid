wget -r http://127.0.0.1:5000/
find ./127.0.0.1:5000/ -type f -print0 | xargs -0 -I{} mv "{}" "{}".html
mv ./127.0.0.1:5000/index.html.html ./127.0.0.1:5000/index.html

cp -r 127.0.0.1:5000/* /home/ockovani/web/ockovani-covid-pages/
rm -r 127.0.0.1:5000
cd /home/ockovani/web/ockovani-covid-pages/
git add *
git commit -m "Update"
git push origin master

