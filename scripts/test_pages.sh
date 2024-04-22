#!/bin/bash

WEB_TMP_DIR="/home/ockovani/acc/web-tmp"

mkdir -p $WEB_TMP_DIR

wget -r -P $WEB_TMP_DIR -e robots=off --adjust-extension http://127.0.0.1:5001/
wget_res=$?

rm -r $WEB_TMP_DIR

exit $wget_res