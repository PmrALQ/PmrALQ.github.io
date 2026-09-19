"""验证版本日志页：徽章（版本号）+ 标题（改动总结）分别取到什么"""
import os
import re
import urllib.request

os.environ['NO_PROXY'] = '*'
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))

for loc, label in (('zh', '中文'), ('en', 'English')):
    try:
        html = op.open(f'http://localhost:3000/{loc}/changelog', timeout=25).read().decode('utf-8', 'ignore')
        badges = re.findall(r'tag-accent"[^>]*>\s*([^<]*?)\s*<', html)
        titles = re.findall(r'<h3[^>]*>\s*([^<]*?)\s*</h3>', html)
        print(f'--- {label} ---')
        print(f'  徽章(版本号): {badges}')
        print(f'  标题(总结)  : {titles}')
    except Exception as e:
        print(loc, '失败', e)
