#!/bin/bash
wget -r --adjust-extension http://127.0.0.1:5001/
wget_res=$?
rm -r 127.0.0.1:5001
exit $wget_res