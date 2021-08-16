#!/bin/bash
LIMIT=75
used_str=$(df -Ph . | tail -1 | awk '{print $5}')
used_num=$(echo "$used_str" | tr -d "%")
if [ $used_num -gt $LIMIT ]; then
  echo "Disk usage is over $LIMIT% ($used_str)!"
  exit 1
fi