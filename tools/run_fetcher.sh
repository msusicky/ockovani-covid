cd /home/ockovani/ockovani-covid
source venv/bin/activate
nohup python3 -u ./freespace_fetcher.py >> fetcher.log &
wait
nohup source tools/create_static_pages.sh >> create_web.log &