mkdir web
cd web
mkdir kraj
cd ..
wget http://127.0.0.1:5000/ockovani-covid/ -O web/index.html
wget http://127.0.0.1:5000/ockovani-covid/info -O web/info.html 
wget http://127.0.0.1:5000/ockovani-covid/kraj/Jihočeský -O web/kraj/Jihočeský.html
wget http://127.0.0.1:5000/ockovani-covid/kraj/Jihomoravský -O web/kraj/Jihomoravský.html
wget http://127.0.0.1:5000/ockovani-covid/kraj/Karlovarský -O web/kraj/Karlovarský.html
wget http://127.0.0.1:5000/ockovani-covid/kraj/Královéhradecký -O web/kraj/Královéhradecký.html
wget http://127.0.0.1:5000/ockovani-covid/kraj/Liberecký -O web/kraj/Liberecký.html
wget http://127.0.0.1:5000/ockovani-covid/kraj/Moravskoslezský -O web/kraj/Moravskoslezský.html 
wget http://127.0.0.1:5000/ockovani-covid/kraj/Olomoucký -O web/kraj/Olomoucký.html 
wget http://127.0.0.1:5000/ockovani-covid/kraj/Plzeňský -O web/kraj/Plzeňský.html 
wget http://127.0.0.1:5000/ockovani-covid/kraj/Praha -O web/kraj/Praha.html
wget http://127.0.0.1:5000/ockovani-covid/kraj/Středočeský -O web/kraj/Středočeský.html
wget http://127.0.0.1:5000/ockovani-covid/kraj/Ústecký -O web/kraj/Ústecký.html
wget http://127.0.0.1:5000/ockovani-covid/kraj/Vysočina -O web/kraj/Vysočina.html 
wget http://127.0.0.1:5000/ockovani-covid/kraj/Zlínský -O web/kraj/Zlínský.html
cp -r web/* /home/ockovani/web/msusicky.github.io/ockovani-covid
rm -r web
cd /home/ockovani/web/msusicky.github.io/ockovani-covid
git add *
git commit -m "Update"
git push origin master

