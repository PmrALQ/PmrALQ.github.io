"""验证版本日志页：条目是否齐全 + 版本号徽章是否渲染出来"""
import os
import re
import urllib.request

os.environ['NO_PROXY'] = '*'
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

for url in ('http://localhost:3000/zh/changelog', 'http://localhost:3000/en/changelog'):
    try:
        with opener.open(url, timeout=20) as r:
            html = r.read().decode('utf-8', 'ignore')
        print(f'{url}  {r.status}')
        for v in ('v0.1', 'v0.2', 'v0.4'):
            print(f'    含 {v}: {v in html}')
        # 徽章：<span class="tag-accent">v0.4</span>
        badges = re.findall(r'tag-accent"[^>]*>\s*([^<]*?)\s*<', html)
        print(f'    徽章内容: {badges}')
        print(f'    v0.3 残留: {"v0.3" in html}')
    except Exception as e:
        print(f'{url}  失败: {e}')
