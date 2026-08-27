#!/bin/bash
# 每天凌晨2点自动收集最新免费公开资料，生成PDF并上传面包多

cd /home/auto_data_packer
python3 scraper.py --sources "zhihu,weibo,小红书" --keywords "AI赚钱,经济周期" --output raw_data.txt
cat raw_data.txt | gamma-cli generate --template "expert_guide" --output guide.pdf
curl -X POST https://api.mbd.pub/upload \
  -H "Authorization: Bearer YOUR_MBD_KEY" \
  -F "file=@guide.pdf" \
  -F "title=每日财富流自动简报" \
  -F "price=9.9"