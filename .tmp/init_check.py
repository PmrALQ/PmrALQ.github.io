# -*- coding: utf-8 -*-
"""Step 1: minimal state check. Writes results to .tmp/init_result.txt"""
import os, subprocess, sys, io

root = r'D:\self_website'
out = []

def sh(cmd, cwd=root):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
        return (r.stdout or r.stderr or '').strip()
    except Exception as e:
        return 'ERR:' + str(e)

out.append('ROOT_EXISTS=' + str(os.path.isdir(root)))
out.append('GIT_ROOT=' + sh(['git', 'rev-parse', '--show-toplevel']))
out.append('---GIT_STATUS---')
out.append(sh(['git', 'status', '--short']) or '(clean)')
out.append('---GIT_DIFF_STAT---')
out.append(sh(['git', 'diff', '--stat']) or '(no diff)')
out.append('---GIT_STAGED_DIFF_STAT---')
out.append(sh(['git', 'diff', '--cached', '--stat']) or '(no staged)')

# tracked file list
files = sh(['git', 'ls-files'])
with open(os.path.join(root, '.workbuddy', 'files.txt'), 'w', encoding='utf-8') as f:
    f.write(files)
out.append('FILES_WRITTEN .workbuddy/files.txt lines=' + str(files.count('\n') + 1))

# .tmp/PROGRESS.md check
progress = os.path.join(root, '.workbuddy', 'PROGRESS.md')
out.append('PROGRESS_EXISTS=' + str(os.path.exists(progress)))
if os.path.exists(progress):
    with open(progress, 'r', encoding='utf-8') as f:
        out.append('---PROGRESS_HEAD---')
        out.append('\n'.join(f.read().splitlines()[:60]))

# keyword scan (excluding common dirs)
SKIP_DIRS = {'.git', 'node_modules', '.nuxt', '.output', 'dist', '.data', '.claude', '.workbuddy'}
keywords = ['github.io', 'GitHub Pages', 'gh-pages', 'formatDate', 'useSplash', 'baseURL', 'nitro', 'waline']
hits = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, root).replace('\\', '/')
        try:
            if os.path.getsize(full) > 512 * 1024:
                continue
            with open(full, 'r', encoding='utf-8', errors='ignore') as f:
                for i, line in enumerate(f, 1):
                    for kw in keywords:
                        if kw in line:
                            hits.append(f'{rel}:{i} [{kw}] {line.strip()[:140]}')
                            break
        except Exception:
            continue

out.append('---KEYWORD_HITS---')
out.append('TOTAL=' + str(len(hits)))
out.extend(hits[:300])

# docs / readme / markdown files with decision keywords in name or content
out.append('---DOC_FILES---')
doc_files = []
for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
    for fn in filenames:
        if fn.lower() in ('readme.md', 'readme', 'architecture.md', 'tech-stack.md', 'technology.md', 'decisions.md', 'adr.md'):
            doc_files.append(os.path.join(dirpath, fn).replace(root + '\\', '').replace('\\', '/'))
        if fn.endswith('.md') and any(k in fn.lower() for k in ('stack', 'decision', 'tech', 'archi')):
            doc_files.append(os.path.join(dirpath, fn).replace(root + '\\', '').replace('\\', '/'))
out.extend(doc_files if doc_files else ['(none)'])

os.makedirs(os.path.dirname(os.path.join(root, '.workbuddy', 'init_result.txt')), exist_ok=True)
with open(os.path.join(root, '.workbuddy', 'init_result.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out))
print('written init_result.txt lines=' + str(len(out)))
