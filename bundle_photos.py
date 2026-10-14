#!/usr/bin/env python3
"""Bundle legally sourced, dish-matched photos in GitHub Pages build.
Place files named seed0.webp, extra0.jpg etc in assets/photos.
Run python bundle_photos.py. Images are not fetched automatically.
"""
from pathlib import Path
import json,re,sys,csv
ROOT=Path(__file__).resolve().parent
HTML=ROOT/'index.html'
PHOTOS=ROOT/'assets'/'photos'
ALLOWED={'.jpg','.jpeg','.png','.webp','.avif'}
files={}
for p in sorted(PHOTOS.iterdir()):
    if p.suffix.lower() not in ALLOWED: continue
    if not re.fullmatch(r'(seed|extra)\d+',p.stem):
        print('SKIP invalid recipe ID:',p.name);continue
    if p.stat().st_size>4*1024*1024:
        print('SKIP photo >4MB:',p.name);continue
    files[p.stem]='assets/photos/'+p.name
# Map reviewed photo filenames to their actual recipe IDs.
with (ROOT/'PHOTO-CREDITS.csv').open(encoding='utf-8-sig',newline='') as fh:
    for row in csv.DictReader(fh):
        photo=PHOTOS/row['filename']
        if photo.is_file() and re.fullmatch(r'(seed|extra)\d+',row['recipe_id']):
            files[row['recipe_id']]='assets/photos/'+photo.name
            if photo.stem!=row['recipe_id']:
                files.pop(photo.stem,None)
html=HTML.read_text(encoding='utf-8')
pattern=r'(<script id="bh-photo-manifest" type="application/json">).*?(</script>)'
html,n=re.subn(pattern,lambda m:m.group(1)+json.dumps(files,ensure_ascii=False)+m.group(2),html,count=1,flags=re.S)
if n!=1:sys.exit('ERROR: photo manifest marker missing')
HTML.write_text(html,encoding='utf-8')
print(f'Bundled {len(files)} real photos. {100-len(files)} recipes use illustration fallbacks.')
