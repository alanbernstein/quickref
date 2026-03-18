#!/usr/bin/env python3
"""Generate index.html, index-static.html, and data/index.json from template.html + data/*.txt."""
import json
import os
from datetime import datetime

root = os.path.dirname(os.path.abspath(__file__))
data_dir = os.environ.get('QR_DATA_DIR') or os.path.join(root, 'data')
app_filename = os.environ.get('QR_APP_FILENAME') or os.path.join(root, 'qr.html')
index = {}

for fname in sorted(os.listdir(data_dir)):
    if not fname.endswith('.txt') or fname.startswith('.') or fname.endswith('.txt~'):
        continue
    topic = fname[:-4]
    path = os.path.join(data_dir, fname)
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        index[topic] = f.read()

raw_json = json.dumps(index, ensure_ascii=False).replace('</', '<\\/')

# Write data/index.json
out_path = os.path.join(data_dir, 'index.json')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(raw_json)
print(f"Wrote {len(index)} topics to {out_path}")

rendered_at = datetime.now().strftime('%Y-%m-%d %H:%M')

with open(os.path.join(root, 'template.html'), 'r') as f:
    template = f.read().replace('%%RENDERED_AT%%', rendered_at)

FETCH_INIT = """    fetch('data/index.json')
      .then(r => r.json())
      .then(data => {
        index = data;
        topics = Object.keys(data);
        statusEl.textContent = topics.length + ' topics loaded';
      });"""

INLINE_INIT = f"""    const _data = {raw_json};
    index = _data;
    topics = Object.keys(_data);
    statusEl.textContent = topics.length + ' topics loaded';"""

# app_filename: data embedded inline
static_html = template.replace('%%DATA_INIT%%', INLINE_INIT)
with open(app_filename, 'w', encoding='utf-8') as f:
    f.write(static_html)
print(f"Wrote {app_filename} ({len(static_html):,} bytes)")
