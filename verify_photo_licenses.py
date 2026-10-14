#!/usr/bin/env python3
"""Verify that bundled photographs have complete source and license metadata."""
import csv,json,re,sys
from pathlib import Path
root=Path(__file__).resolve().parent
photos=list((root/'assets/photos').glob('*.webp'))
with (root/'PHOTO-CREDITS.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
byfile={r['filename']:r for r in rows}
issues=[]
for p in photos:
 r=byfile.get(p.name)
 if not r:issues.append(f'{p.name}: no credits entry');continue
 for field in ('recipe_id','photographer','source_url','license'):
  if not r.get(field,'').strip():issues.append(f'{p.name}: missing {field}')
 if not re.match(r'https://',r.get('source_url','')):issues.append(f'{p.name}: source must be HTTPS')
 if not re.match(r'^(CC0|Public Domain|CC BY(?:-SA)? [234]\.0)$',r.get('license','')):issues.append(f'{p.name}: license requires manual verification')
try:
 from PIL import Image
 for p in photos:
  try:
   with Image.open(p) as im:
    if im.format!='WEBP':issues.append(f'{p.name}: not actual WebP')
    im.verify()
  except Exception as e:issues.append(f'{p.name}: invalid image {e}')
except ImportError:issues.append('Pillow not installed: cannot validate image encoding')
html=(root/'index.html').read_text(encoding='utf-8')
m=re.search(r'<script id="bh-photo-manifest" type="application/json">(.*?)</script>',html,re.S)
manifest=json.loads(m.group(1)) if m else {}
for key,relative in manifest.items():
 if not (root/relative).is_file():issues.append(f'{key}: missing bundled file')
 if Path(relative).name not in byfile:issues.append(f'{key}: no attribution')
print(json.dumps({'verified_webp_files':len(photos),'manifest_entries':len(manifest),'issues':issues},ensure_ascii=False,indent=2))
sys.exit(bool(issues))
