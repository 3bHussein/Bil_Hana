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
# Only publish photos with a matching, explicit attribution record.
files={}
with (ROOT/'PHOTO-CREDITS.csv').open(encoding='utf-8-sig',newline='') as fh:
    for row in csv.DictReader(fh):
        recipe=row.get('recipe_id','')
        filename=row.get('filename','')
        if not re.fullmatch(r'(?:seed|extra|v19_)\d+',recipe): continue
        if Path(filename).name!=filename: continue
        photo=PHOTOS/filename
        if photo.suffix.lower() not in ALLOWED or not photo.is_file(): continue
        if photo.stat().st_size>4*1024*1024: continue
        if not all(row.get(key,'').strip() for key in ('photographer','source_url','license')): continue
        files[recipe]='assets/photos/'+filename
html=HTML.read_text(encoding='utf-8')
pattern=r'(<script id="bh-photo-manifest" type="application/json">).*?(</script>)'
html,n=re.subn(pattern,lambda m:m.group(1)+json.dumps(files,ensure_ascii=False)+m.group(2),html,count=1,flags=re.S)
if n!=1:sys.exit('ERROR: photo manifest marker missing')
HTML.write_text(html,encoding='utf-8')
print(f'Bundled {len(files)} real photos. {100-len(files)} recipes use illustration fallbacks.')
